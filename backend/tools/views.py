import hashlib
import hmac
import ipaddress
import json
import re
import uuid
from datetime import datetime, time, timedelta
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db import DatabaseError
from django.db.models import Count, Max
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .blastp_utils import run_combined_protein_alignment
from .models import VisitorEvent
from .structure_align_utils import run_usalign


BOT_USER_AGENT_PATTERN = re.compile(
    r"bot|crawler|spider|slurp|bingpreview|facebookexternalhit|headless",
    re.IGNORECASE,
)


def _json_error(message, status=400):
    return JsonResponse(
        {"success": False, "error": message},
        status=status,
    )


def _get_client_ip(request):
    """Return the first valid client IP supplied by the trusted reverse proxy."""
    candidates = []

    real_ip = request.META.get("HTTP_X_REAL_IP")
    if real_ip:
        candidates.append(real_ip)

    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        candidates.extend(part.strip() for part in forwarded_for.split(","))

    remote_addr = request.META.get("REMOTE_ADDR")
    if remote_addr:
        candidates.append(remote_addr)

    for candidate in candidates:
        try:
            return str(ipaddress.ip_address(candidate))
        except ValueError:
            continue

    return ""


@lru_cache(maxsize=1)
def _get_geoip_reader():
    database_path = getattr(settings, "GEOIP_COUNTRY_DB", None)
    if not database_path or not Path(database_path).is_file():
        return None

    try:
        from geoip2.database import Reader
    except ImportError:
        return None

    try:
        return Reader(str(database_path))
    except Exception:
        return None


def _lookup_country(ip_address):
    if not ip_address:
        return None, None

    try:
        if ipaddress.ip_address(ip_address).is_private:
            return None, None
    except ValueError:
        return None, None

    reader = _get_geoip_reader()
    if reader is None:
        return None, None

    try:
        country = reader.country(ip_address).country
        return country.iso_code, country.name
    except Exception:
        return None, None


def _anonymous_visitor_hash(visitor_id, ip_address, user_agent):
    identifier = visitor_id or f"{ip_address}|{user_agent}"
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        identifier.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _normalise_page_path(value):
    parsed = urlsplit(str(value or "/").strip())
    page_path = parsed.path or "/"
    return page_path[:512]


def _extract_referrer_host(value):
    referrer = str(value or "").strip()
    if not referrer:
        return None

    parsed = urlsplit(referrer)
    return parsed.hostname[:255] if parsed.hostname else None


def _visitor_period(period):
    stats_timezone = ZoneInfo(
        getattr(settings, "VISITOR_STATS_TIME_ZONE", "Asia/Shanghai")
    )
    local_now = timezone.now().astimezone(stats_timezone)
    end_date = local_now.date()
    end_exclusive = datetime.combine(
        end_date + timedelta(days=1),
        time.min,
        tzinfo=stats_timezone,
    )

    if period == "30days":
        start_date = end_date - timedelta(days=29)
        short_label = "30 days"
    elif period == "year":
        start_date = end_date.replace(month=1, day=1)
        short_label = str(end_date.year)
    elif period == "all":
        start_date = None
        short_label = "All time"
    else:
        raise ValueError("period must be one of: 30days, year, all")

    start_at = None
    if start_date is not None:
        start_at = datetime.combine(start_date, time.min, tzinfo=stats_timezone)

    return {
        "start_date": start_date,
        "end_date": end_date,
        "start_at": start_at,
        "end_exclusive": end_exclusive,
        "short_label": short_label,
    }


def _format_date_range(start_date, end_date):
    if start_date is None:
        return "Since launch"

    start_text = f"{start_date.strftime('%b')} {start_date.day}"
    end_text = f"{end_date.strftime('%b')} {end_date.day}, {end_date.year}"
    return f"{start_text} – {end_text}"


@csrf_exempt
@require_POST
def visitor_track_view(request):
    """Record one anonymous page-view event."""
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (UnicodeDecodeError, json.JSONDecodeError):
        return _json_error("Request body must be valid JSON.")

    if not isinstance(payload, dict):
        return _json_error("Request body must be a JSON object.")

    raw_event_id = payload.get("eventId") or payload.get("event_id")
    try:
        event_id = str(uuid.UUID(str(raw_event_id)))
    except (TypeError, ValueError, AttributeError):
        return _json_error("eventId must be a valid UUID.")

    visitor_id = str(
        payload.get("visitorId") or payload.get("visitor_id") or ""
    ).strip()[:256]
    user_agent = request.META.get("HTTP_USER_AGENT", "")[:1024]
    client_ip = _get_client_ip(request)
    visitor_hash = _anonymous_visitor_hash(visitor_id, client_ip, user_agent)
    country_code, country_name = _lookup_country(client_ip)

    page_path = _normalise_page_path(
        payload.get("pagePath") or payload.get("page_path") or payload.get("path")
    )
    referrer_host = _extract_referrer_host(
        payload.get("referrer") or request.META.get("HTTP_REFERER")
    )
    is_bot = bool(BOT_USER_AGENT_PATTERN.search(user_agent))

    try:
        event, created = VisitorEvent.objects.get_or_create(
            event_id=event_id,
            defaults={
                "visitor_hash": visitor_hash,
                "country_code": country_code,
                "country_name": country_name,
                "page_path": page_path,
                "referrer_host": referrer_host,
                "is_bot": is_bot,
            },
        )
    except DatabaseError:
        return _json_error(
            "Visitor statistics storage is unavailable.",
            status=500,
        )

    return JsonResponse(
        {
            "success": True,
            "data": {
                "eventId": event.event_id,
                "recorded": created,
            },
        },
        status=201 if created else 200,
    )


@require_GET
def visitor_stats_view(request):
    """Return aggregated visitor statistics for the map dashboard."""
    period = request.GET.get("period", "year")

    try:
        period_info = _visitor_period(period)
    except ValueError as error:
        return _json_error(str(error))

    events = VisitorEvent.objects.filter(is_bot=False)
    if period_info["start_at"] is not None:
        events = events.filter(visited_at__gte=period_info["start_at"])
    events = events.filter(visited_at__lt=period_info["end_exclusive"])

    try:
        totals = events.aggregate(
            page_views=Count("id"),
            unique_visitors=Count("visitor_hash", distinct=True),
        )
        location_rows = list(
            events.filter(country_code__isnull=False)
            .exclude(country_code="")
            .values("country_code")
            .annotate(
                country_name=Max("country_name"),
                page_views=Count("id"),
                unique_visitors=Count("visitor_hash", distinct=True),
            )
            .order_by("-page_views", "country_code")
        )
    except DatabaseError:
        return _json_error(
            "Visitor statistics storage is unavailable.",
            status=500,
        )

    locations = [
        {
            "countryCode": row["country_code"],
            "name": row["country_name"] or row["country_code"],
            "pageViews": row["page_views"],
            "uniqueVisitors": row["unique_visitors"],
        }
        for row in location_rows
    ]

    return JsonResponse(
        {
            "success": True,
            "data": {
                "period": period,
                "dateRange": {
                    "startDate": (
                        period_info["start_date"].isoformat()
                        if period_info["start_date"]
                        else None
                    ),
                    "endDate": period_info["end_date"].isoformat(),
                    "label": _format_date_range(
                        period_info["start_date"],
                        period_info["end_date"],
                    ),
                    "shortLabel": period_info["short_label"],
                },
                "summary": {
                    "pageViews": totals["page_views"],
                    "uniqueVisitors": totals["unique_visitors"],
                    "countries": len(locations),
                },
                "locations": locations,
                "generatedAt": timezone.now().isoformat(),
            },
        }
    )

@csrf_exempt
@require_POST
def protein_alignment_api(request):
    try:
        data = json.loads(request.body.decode("utf-8"))

        sequence1 = data.get("sequence1", "")
        sequence2 = data.get("sequence2", "")

        result = run_combined_protein_alignment(sequence1, sequence2)

        return JsonResponse({
            "success": True,
            "data": result
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)
        
@csrf_exempt
@require_POST
def structure_align_view(request):
    """
    结构比对接口。

    前端用 FormData 上传：
      file1: 第一个结构文件
      file2: 第二个结构文件

    返回 JSON：
      {
        "success": true,
        "tmScore1": 0.42701,
        "tmScore2": 0.05599,
        "rmsd": 4.82,
        "alignedLength": 94,
        "alignmentBlocks": [...],
        "rawOutput": "...",
        "superposedPdbUrl": "/media/structure_align/xxx/sup.pdb"
      }
    """
    try:
        file1 = request.FILES.get("file1")
        file2 = request.FILES.get("file2")

        if not file1 or not file2:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Both file1 and file2 are required.",
                },
                status=400,
            )

        result = run_usalign(file1, file2)
        return JsonResponse(result, status=200)

    except ValueError as e:
        # 上传文件类型、大小等错误。
        return JsonResponse(
            {
                "success": False,
                "message": str(e),
            },
            status=400,
        )

    except RuntimeError as e:
        # US-align 执行失败、路径错误等。
        return JsonResponse(
            {
                "success": False,
                "message": str(e),
            },
            status=500,
        )

    except Exception as e:
        # 兜底错误。
        return JsonResponse(
            {
                "success": False,
                "message": f"Unexpected server error: {str(e)}",
            },
            status=500,
        )
