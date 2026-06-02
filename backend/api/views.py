from django.shortcuts import render

from pathlib import Path
from urllib.parse import quote
from django.conf import settings
from django.db import DatabaseError
from django.db.models import Q
from django.http import FileResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from collections import defaultdict
from rest_framework import status
from django.views.decorators.http import require_GET
from .models import GeneInfo
from .models import SpeciesInfo
from .models import SearchResult
from .models import ProteinInfo

import json
import mimetypes
import re
from datetime import datetime

CIF_SPECIES_PREFIXES = {
    "glycine max": "gm",
    "lotus japonicus": "lj",
    "medicago truncatula": "mt",
    "phaseolus vulgaris": "pv",
}

CIF_PROTEIN_PREFIXES = {
    "glyma": "gm",
    "lj": "lj",
    "medtr": "mt",
    "phvul": "pv",
}

GENOME_RESOURCE_SUFFIXES = {
    "genome": [
        ".fasta",
        ".fasta.gz",
        ".fa",
        ".fa.gz",
        ".fna",
        ".fna.gz",
    ],
    "gff": [
        ".genes.sorted.gff3",
        ".genes.sorted.gff3.gz",
        ".genes.fixed_gene.sorted.gff3",
        ".genes.fixed_gene.sorted.gff3.gz",
        ".gff3",
        ".gff3.gz",
    ],
}

GENOME_RESOURCE_TYPES = {
    "genome": "genome",
    "fasta": "genome",
    "fa": "genome",
    "fna": "genome",
    "gff": "gff",
    "gff3": "gff",
}

NPY_RESOURCE_SUFFIX_TYPES = {
    "_meta.npy": "Protein ID",
    "_db.npy": "Vector",
}

HOMOLOGY_RESOURCE_SUFFIX = ".tmvec"
HOMOLOGY_RESOURCE_TYPE = "results"


def _normalize_cif_gene(value, species_prefix):
    gene = re.sub(r"[^a-z0-9]", "", str(value or "").lower())

    if species_prefix and gene.startswith(species_prefix):
        gene = gene[len(species_prefix):]

    return gene


def _normalize_cif_protein_id(value):
    return re.sub(r"[^a-z0-9.]", "", str(value or "").lower())


def _get_cif_file_url(protein_id):
    return f"/api/protein/cif/?protein_id={quote(str(protein_id or '').strip())}"


def _normalize_genome_resource_type(value):
    return GENOME_RESOURCE_TYPES.get(str(value or "").strip().lower())


def _get_genome_file_root():
    return Path(
        getattr(settings, "GENOME_FILE_ROOT", settings.BASE_DIR.parent / "genome")
    )


def _is_safe_genome_name(value):
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+", str(value or "")))


def _get_genome_resource_candidates(conservatory_genome_name, resource_type):
    suffixes = GENOME_RESOURCE_SUFFIXES.get(resource_type, [])
    return [
        f"{conservatory_genome_name}{suffix}"
        for suffix in suffixes
    ]


def _get_content_type(file_path):
    content_type, encoding = mimetypes.guess_type(file_path.name)

    if encoding == "gzip":
        return "application/gzip"

    return content_type or "application/octet-stream"


def _format_file_size(bytes_count):
    if not bytes_count:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(bytes_count)
    unit_index = 0

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    precision = 0 if size >= 10 or unit_index == 0 else 1
    return f"{size:.{precision}f} {units[unit_index]}"


def _get_genome_resource_type_from_filename(filename):
    for resource_type, suffixes in GENOME_RESOURCE_SUFFIXES.items():
        for suffix in suffixes:
            if filename.endswith(suffix):
                return resource_type

    return None


def _strip_genome_resource_suffix(filename, resource_type):
    for suffix in GENOME_RESOURCE_SUFFIXES.get(resource_type, []):
        if filename.endswith(suffix):
            return filename[:-len(suffix)]

    return Path(filename).stem


def _is_safe_genome_filename(value):
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+", str(value or "")))


def _get_genome_metadata_lookup():
    try:
        rows = SpeciesInfo.objects.values(
            "species",
            "genome_version",
            "conservatory_genome_name",
        )
        return {
            item["conservatory_genome_name"]: {
                "species": item["species"] or "",
                "genome_version": item["genome_version"] or "",
            }
            for item in rows
            if item["conservatory_genome_name"]
        }
    except DatabaseError:
        return {}


def _get_genome_file_url(filename):
    return f"/api/genome/file/?filename={quote(str(filename or '').strip())}"


def list_genome_resource_files():
    genome_file_root = _get_genome_file_root().resolve()
    metadata_lookup = _get_genome_metadata_lookup()

    if not genome_file_root.is_dir():
        return []

    rows = []

    for file_path in sorted(genome_file_root.iterdir(), key=lambda item: item.name.lower()):
        if not file_path.is_file():
            continue

        filename = file_path.name
        resource_type = _get_genome_resource_type_from_filename(filename)

        if not resource_type:
            continue

        conservatory_genome_name = _strip_genome_resource_suffix(filename, resource_type)
        metadata = metadata_lookup.get(conservatory_genome_name, {})
        file_stat = file_path.stat()

        rows.append({
            "species": metadata.get("species", ""),
            "genome_version": metadata.get("genome_version", conservatory_genome_name),
            "conservatory_genome_name": conservatory_genome_name,
            "type": "Genome" if resource_type == "genome" else "GFF",
            "format": "FASTA" if resource_type == "genome" else "GFF3",
            "bytes": file_stat.st_size,
            "sizeLabel": _format_file_size(file_stat.st_size),
            "updatedAt": datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d"),
            "filename": filename,
            "url": _get_genome_file_url(filename),
        })

    return rows


def _get_npy_file_root():
    return Path(getattr(settings, "PROTEIN_NPY_ROOT", settings.BASE_DIR.parent / "npy"))


def _is_safe_npy_filename(value):
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+\.npy", str(value or "")))


def _get_npy_resource_type_from_filename(filename):
    for suffix, resource_type in NPY_RESOURCE_SUFFIX_TYPES.items():
        if filename.endswith(suffix):
            return resource_type

    return None


def _strip_npy_resource_suffix(filename):
    for suffix in NPY_RESOURCE_SUFFIX_TYPES:
        if filename.endswith(suffix):
            return filename[:-len(suffix)]

    return Path(filename).stem


def _get_npy_download_url(filename):
    return f"/api/npy/file/?filename={quote(str(filename or '').strip())}"


def list_npy_resource_files():
    npy_root = _get_npy_file_root().resolve()
    metadata_lookup = _get_genome_metadata_lookup()

    if not npy_root.is_dir():
        return []

    rows = []

    for file_path in sorted(npy_root.glob("*.npy"), key=lambda item: item.name.lower()):
        if not file_path.is_file():
            continue

        filename = file_path.name
        resource_type = _get_npy_resource_type_from_filename(filename)

        if not resource_type:
            continue

        conservatory_genome_name = _strip_npy_resource_suffix(filename)
        metadata = metadata_lookup.get(conservatory_genome_name, {})
        file_stat = file_path.stat()

        rows.append({
            "species": metadata.get("species", ""),
            "genome_version": metadata.get("genome_version", conservatory_genome_name),
            "conservatory_genome_name": conservatory_genome_name,
            "type": resource_type,
            "bytes": file_stat.st_size,
            "sizeLabel": _format_file_size(file_stat.st_size),
            "updatedAt": datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d"),
            "filename": filename,
            "url": _get_npy_download_url(filename),
        })

    return rows


def _get_homology_file_root():
    return Path(
        getattr(settings, "PROTEIN_HOMOLOGY_ROOT", settings.BASE_DIR.parent / "tmvec")
    )


def _is_safe_homology_filename(value):
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+\.tmvec", str(value or "")))


def _strip_homology_resource_suffix(filename):
    if filename.endswith(HOMOLOGY_RESOURCE_SUFFIX):
        return filename[:-len(HOMOLOGY_RESOURCE_SUFFIX)]

    return Path(filename).stem


def _get_homology_download_url(filename):
    return f"/api/homology/file/?filename={quote(str(filename or '').strip())}"


def list_homology_resource_files():
    homology_root = _get_homology_file_root().resolve()
    metadata_lookup = _get_genome_metadata_lookup()

    if not homology_root.is_dir():
        return []

    rows = []

    for file_path in sorted(homology_root.glob(f"*{HOMOLOGY_RESOURCE_SUFFIX}"), key=lambda item: item.name.lower()):
        if not file_path.is_file():
            continue

        filename = file_path.name
        conservatory_genome_name = _strip_homology_resource_suffix(filename)
        metadata = metadata_lookup.get(conservatory_genome_name, {})
        file_stat = file_path.stat()

        rows.append({
            "species": metadata.get("species", ""),
            "genome_version": metadata.get("genome_version", conservatory_genome_name),
            "conservatory_genome_name": conservatory_genome_name,
            "type": HOMOLOGY_RESOURCE_TYPE,
            "bytes": file_stat.st_size,
            "sizeLabel": _format_file_size(file_stat.st_size),
            "updatedAt": datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d"),
            "filename": filename,
            "url": _get_homology_download_url(filename),
        })

    return rows


def _get_snf_file_path():
    return Path(
        getattr(
            settings,
            "SNF_RELATED_GENE_FILE",
            settings.BASE_DIR.parent / "output_protein_data_with_domain.csv",
        )
    )


def _get_snf_download_url():
    return "/api/snf/file/"


def list_snf_resource_files():
    snf_file = _get_snf_file_path().resolve()

    if not snf_file.is_file():
        return []

    file_stat = snf_file.stat()

    return [{
        "bytes": file_stat.st_size,
        "sizeLabel": _format_file_size(file_stat.st_size),
        "updatedAt": datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d"),
        "filename": snf_file.name,
        "url": _get_snf_download_url(),
    }]


def _get_cif_file_root():
    return Path(getattr(settings, "PROTEIN_CIF_ROOT", settings.BASE_DIR.parent / "cif"))


def _is_safe_cif_filename(value):
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+\.cif", str(value or "")))


def _get_cif_protein_id_from_filename(filename):
    stem = filename[:-len(".cif")] if filename.endswith(".cif") else Path(filename).stem

    if "__" in stem:
        stem = stem.split("__", 1)[1]

    if stem.endswith("_model"):
        stem = stem[:-len("_model")]

    return stem


def _get_cif_download_url(filename):
    return f"/api/protein/cif/?filename={quote(str(filename or '').strip())}"


def list_cif_resource_files():
    cif_root = _get_cif_file_root().resolve()

    if not cif_root.is_dir():
        return []

    rows = []

    for file_path in sorted(cif_root.glob("*.cif"), key=lambda item: item.name.lower()):
        if not file_path.is_file():
            continue

        file_stat = file_path.stat()

        rows.append({
            "protein_id": _get_cif_protein_id_from_filename(file_path.name),
            "filename": file_path.name,
            "bytes": file_stat.st_size,
            "sizeLabel": _format_file_size(file_stat.st_size),
            "updatedAt": datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d"),
            "format": "CIF",
            "url": _get_cif_download_url(file_path.name),
        })

    return rows


def get_genome_resource_file_info(conservatory_genome_name, file_type):
    resource_type = _normalize_genome_resource_type(file_type)
    genome_file_root = _get_genome_file_root().resolve()

    if not resource_type:
        return {
            "status": "invalid_type",
            "message": "Invalid file type",
            "root": str(genome_file_root),
            "candidates": [],
        }

    candidates = _get_genome_resource_candidates(
        conservatory_genome_name,
        resource_type
    )

    for filename in candidates:
        candidate_path = (genome_file_root / filename).resolve()

        try:
            candidate_path.relative_to(genome_file_root)
        except ValueError:
            continue

        if candidate_path.is_file():
            return {
                "status": "found",
                "message": "success",
                "resource_type": resource_type,
                "filename": candidate_path.name,
                "path": str(candidate_path),
                "root": str(genome_file_root),
                "candidates": candidates,
            }

    return {
        "status": "not_found",
        "message": "Genome resource file not found",
        "resource_type": resource_type,
        "filename": None,
        "path": None,
        "root": str(genome_file_root),
        "candidates": candidates,
    }


def _get_cif_species_prefix(organism, protein_id):
    organism_text = re.sub(r"\s+", " ", str(organism or "").lower()).strip()

    for species_name, prefix in CIF_SPECIES_PREFIXES.items():
        if species_name in organism_text:
            return prefix

    compact_organism = re.sub(r"[^a-z]", "", organism_text)
    for species_name, prefix in CIF_SPECIES_PREFIXES.items():
        if species_name.replace(" ", "") in compact_organism:
            return prefix

    protein_slug = _normalize_cif_protein_id(protein_id)
    for protein_prefix, species_prefix in CIF_PROTEIN_PREFIXES.items():
        if protein_slug.startswith(protein_prefix):
            return species_prefix

    return ""


def _get_cif_prefix(cif_path):
    filename = Path(cif_path).name

    if filename.endswith("_model.cif"):
        return filename[:-len("_model.cif")]

    return Path(filename).stem


def _format_confidence_metric(value):
    return "-" if value is None or value == "" else value


def get_confidence_summary_info(cif_path):
    confidence_root = Path(
        getattr(settings, "PROTEIN_CONFIDENCE_ROOT", settings.BASE_DIR.parent / "confidences.json")
    )
    cif_prefix = _get_cif_prefix(cif_path) if cif_path else ""
    expected_filename = f"{cif_prefix}_summary_confidences.json" if cif_prefix else ""
    expected_path = confidence_root / expected_filename if expected_filename else None

    base_info = {
        "exists": False,
        "filename": None,
        "path": None,
        "root": str(confidence_root),
        "expected_filename": expected_filename,
        "expected_path": str(expected_path) if expected_path else None,
        "lookup_status": "not_found",
        "iptm": "-",
        "ptm": "-",
    }

    matched_path = expected_path if expected_path and expected_path.is_file() else None

    if not matched_path and cif_prefix and confidence_root.is_dir():
        matches = sorted(confidence_root.glob(f"{cif_prefix}*summary_confidences.json"))
        matched_path = matches[0] if matches else None

    if not matched_path:
        return base_info

    try:
        with matched_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return {
            **base_info,
            "filename": matched_path.name,
            "path": str(matched_path),
            "lookup_status": "read_error",
        }

    return {
        **base_info,
        "exists": True,
        "filename": matched_path.name,
        "path": str(matched_path),
        "lookup_status": "exact_match" if matched_path == expected_path else "prefix_match",
        "iptm": _format_confidence_metric(data.get("iptm")),
        "ptm": _format_confidence_metric(data.get("ptm")),
    }


def get_cif_file_info(item):
    cif_root = Path(getattr(settings, "PROTEIN_CIF_ROOT", settings.BASE_DIR.parent / "cif"))
    species_prefix = _get_cif_species_prefix(item.organism, item.protein_id)
    gene_slug = _normalize_cif_gene(item.gene_id, species_prefix)
    protein_slug = _normalize_cif_protein_id(item.protein_id)
    expected_filename = ""
    expected_path = None

    if species_prefix and gene_slug and protein_slug:
        expected_filename = f"{species_prefix}{gene_slug}__{protein_slug}_model.cif"
        expected_path = cif_root / expected_filename

        if expected_path.is_file():
            confidence_summary = get_confidence_summary_info(expected_path)

            return {
                "exists": True,
                "filename": expected_path.name,
                "path": str(expected_path),
                "url": _get_cif_file_url(item.protein_id),
                "root": str(cif_root),
                "expected_filename": expected_filename,
                "expected_path": str(expected_path),
                "lookup_status": "exact_match",
                "species_prefix": species_prefix,
                "gene_slug": gene_slug,
                "protein_id_slug": protein_slug,
                "confidence_summary": confidence_summary,
            }

    matched_path = None
    if protein_slug and cif_root.is_dir():
        matches = sorted(cif_root.glob(f"*__{protein_slug}_model.cif"))
        matched_path = matches[0] if matches else None

    if matched_path:
        confidence_summary = get_confidence_summary_info(matched_path)

        return {
            "exists": True,
            "filename": matched_path.name,
            "path": str(matched_path),
            "url": _get_cif_file_url(item.protein_id),
            "root": str(cif_root),
            "expected_filename": expected_filename,
            "expected_path": str(expected_path) if expected_path else None,
            "lookup_status": "protein_id_match",
            "species_prefix": species_prefix,
            "gene_slug": gene_slug,
            "protein_id_slug": protein_slug,
            "confidence_summary": confidence_summary,
        }

    return {
        "exists": False,
        "filename": None,
        "path": None,
        "url": None,
        "root": str(cif_root),
        "expected_filename": expected_filename,
        "expected_path": str(expected_path) if expected_path else None,
        "lookup_status": "not_found",
        "species_prefix": species_prefix,
        "gene_slug": gene_slug,
        "protein_id_slug": protein_slug,
        "confidence_summary": get_confidence_summary_info(expected_path) if expected_path else None,
    }

class GeneUniqueListAPIView(APIView):
    def get(self, request):
        genes = (
            GeneInfo.objects
            .values_list("gene", flat=True)
            .distinct()
            .order_by("gene")
        )
        return Response({
            "code": 200,
            "message": "success",
            "data": list(genes)
        }, status=status.HTTP_200_OK)
        

class SpeciesGenomeVersionListAPIView(APIView):
    def get(self, request):
        queryset = (
            SpeciesInfo.objects
            .values(
                "family",
                "species",
                "genome_version",
                "conservatory_genome_name"
            )
            .order_by("species", "genome_version")
        )

        species_map = defaultdict(lambda: {
            "family": "",
            "species": "",
            "genome_versions": []
        })

        for item in queryset:
            species = item["species"]

            species_map[species]["family"] = item["family"]
            species_map[species]["species"] = species
            species_map[species]["genome_versions"].append({
                "genome_version": item["genome_version"],
                "conservatory_genome_name": item["conservatory_genome_name"]
            })

        return Response({
            "code": 200,
            "message": "success",
            "data": list(species_map.values())
        }, status=status.HTTP_200_OK)
        

class SearchResultAPIView(APIView):
    def get(self, request):
        genes = [
            g.strip()
            for g in request.GET.getlist("gene")
            if g.strip()
        ]

        species_names = [
            s.strip()
            for s in request.GET.getlist("species")
            if s.strip()
        ]

        categories = [
            c.strip().upper()
            for c in request.GET.getlist("category")
            if c.strip()
        ]

        conservatory_genome_names = [
            g.strip()
            for g in request.GET.getlist("conservatory_genome_name")
            if g.strip()
        ]

        if not genes:
            return Response({
                "code": 400,
                "message": "at least one gene is required",
                "data": []
            }, status=status.HTTP_400_BAD_REQUEST)

        if not species_names:
            return Response({
                "code": 400,
                "message": "at least one species is required",
                "data": []
            }, status=status.HTTP_400_BAD_REQUEST)

        if not conservatory_genome_names:
            return Response({
                "code": 400,
                "message": "genome version is required",
                "data": []
            }, status=status.HTTP_400_BAD_REQUEST)

        species_info_qs = (
            SpeciesInfo.objects
            .filter(
                species__in=species_names,
                conservatory_genome_name__in=conservatory_genome_names
            )
            .values(
                "species",
                "genome_version",
                "conservatory_genome_name"
            )
        )

        species_info_list = list(species_info_qs)

        if not species_info_list:
            return Response({
                "code": 400,
                "message": "no valid species or genome version found",
                "data": []
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_species_codes = {
            item["conservatory_genome_name"]
            for item in species_info_list
            if item["conservatory_genome_name"]
        }

        if not valid_species_codes:
            return Response({
                "code": 400,
                "message": "no valid conservatory genome name found",
                "data": []
            }, status=status.HTTP_400_BAD_REQUEST)

        gene_query = Q()

        for gene in genes:
            pattern = rf'^[A-Za-z]{{2}}{re.escape(gene)}__'
            gene_query |= Q(query_protein_name__regex=pattern)

        queryset = (
            SearchResult.objects
            .filter(species_code__in=valid_species_codes)
            .filter(gene_query)
        )

        if categories:
            valid_categories = {"A", "B", "C"}
            categories = [
                c for c in categories
                if c in valid_categories
            ]

            if categories:
                category_query = Q()

                if "A" in categories:
                    category_query |= Q(
                        tm_score__gte=50,
                        sequence_similarity__gte=50
                    )

                if "B" in categories:
                    category_query |= Q(
                        tm_score__gte=50,
                        sequence_similarity__gte=30,
                        sequence_similarity__lt=50
                    )

                if "C" in categories:
                    category_query |= Q(
                        tm_score__gte=50,
                        sequence_similarity__lt=30
                    )

                queryset = queryset.filter(category_query)

        queryset = queryset.order_by(
            "species_code",
            "query_protein_name"
        )

        data = list(queryset.values(
            "id",
            "species_code",
            "query_protein_name",
            "hit_protein_name",
            "tm_score",
            "sequence_similarity",
            "query_protein_length",
            "hit_protein_length"
        ))

        return Response({
            "code": 200,
            "message": "success",
            "data": data
        }, status=status.HTTP_200_OK)
        
class ProteinInfoAPIView(APIView):
    def get(self, request):
        gene_ids = request.GET.getlist('gene_id')
        organisms = request.GET.getlist('organism')

        gene_ids = [item.strip() for item in gene_ids if item.strip()]
        organisms = [item.strip() for item in organisms if item.strip()]

        queryset = ProteinInfo.objects.all()

        if gene_ids:
            gene_query = Q()

            for gene_id in gene_ids:
                # 输入 ACP，可以匹配：
                # ACP
                # GMACP
                # ACP_
                # ACP_001
                # GMACP_
                # GMACP_001
                #
                # 不匹配：
                # ACP12
                # GMACP12
                gene_query |= Q(gene_id__iendswith=gene_id)
                gene_query |= Q(gene_id__icontains=f'{gene_id}_')

            queryset = queryset.filter(gene_query)

        if organisms:
            queryset = queryset.filter(organism__in=organisms)

        queryset = queryset.order_by('gene_id', 'organism', 'protein_id')

        data = [
            {
                'protein_id': item.protein_id,
                'protein_class': item.protein_class,
                'amino_acids': item.amino_acids,
                'gene_id': item.gene_id,
                'organism': item.organism,
                'domain': item.domain,
            }
            for item in queryset
        ]

        return Response({
            'data': data,
            'total': len(data),
        })
        
class ProteinSequenceAPIView(APIView):
    def get(self, request):
        protein_id = request.GET.get('protein_id', '').strip()

        if not protein_id:
            return Response({
                'message': 'Missing protein_id'
            }, status=status.HTTP_400_BAD_REQUEST)

        item = ProteinInfo.objects.filter(protein_id=protein_id).first()

        if not item:
            return Response({
                'message': 'Protein not found'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'data': {
                'protein_id': item.protein_id,
                'gene_id': item.gene_id,
                'organism': item.organism,
                'protein_sequence': item.sequencs or '',
                'cif_file': get_cif_file_info(item),
            }
        })


class GenomeResourceFileAPIView(APIView):
    def get(self, request):
        filename = request.GET.get('filename', '').strip()

        if filename:
            if not _is_safe_genome_filename(filename):
                return Response({
                    'message': 'Invalid filename'
                }, status=status.HTTP_400_BAD_REQUEST)

            resource_type = _get_genome_resource_type_from_filename(filename)

            if not resource_type:
                return Response({
                    'message': 'Invalid genome resource filename'
                }, status=status.HTTP_400_BAD_REQUEST)

            genome_file_root = _get_genome_file_root().resolve()
            file_path = (genome_file_root / filename).resolve()

            try:
                file_path.relative_to(genome_file_root)
            except ValueError:
                return Response({
                    'message': 'Invalid genome resource path'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not file_path.is_file():
                return Response({
                    'message': 'Genome resource file not found'
                }, status=status.HTTP_404_NOT_FOUND)

            return FileResponse(
                file_path.open("rb"),
                as_attachment=True,
                filename=file_path.name,
                content_type=_get_content_type(file_path)
            )

        conservatory_genome_name = request.GET.get(
            'conservatory_genome_name',
            ''
        ).strip()
        file_type = request.GET.get('file_type', '').strip()

        if not conservatory_genome_name:
            return Response({
                'message': 'Missing conservatory_genome_name'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not _is_safe_genome_name(conservatory_genome_name):
            return Response({
                'message': 'Invalid conservatory_genome_name'
            }, status=status.HTTP_400_BAD_REQUEST)

        genome_file = get_genome_resource_file_info(
            conservatory_genome_name,
            file_type
        )

        if genome_file["status"] == "invalid_type":
            return Response({
                'message': genome_file["message"],
                'valid_file_types': ['genome', 'fasta', 'gff', 'gff3'],
            }, status=status.HTTP_400_BAD_REQUEST)

        if genome_file["status"] != "found" or not genome_file["path"]:
            return Response({
                'message': genome_file["message"],
                'genome_file': genome_file,
            }, status=status.HTTP_404_NOT_FOUND)

        file_path = Path(genome_file["path"])

        return FileResponse(
            file_path.open("rb"),
            as_attachment=True,
            filename=file_path.name,
            content_type=_get_content_type(file_path)
        )


class GenomeResourceListAPIView(APIView):
    def get(self, request):
        return Response({
            "code": 200,
            "message": "success",
            "data": list_genome_resource_files()
        }, status=status.HTTP_200_OK)


class NpyResourceListAPIView(APIView):
    def get(self, request):
        return Response({
            "code": 200,
            "message": "success",
            "data": list_npy_resource_files()
        }, status=status.HTTP_200_OK)


class NpyResourceFileAPIView(APIView):
    def get(self, request):
        filename = request.GET.get('filename', '').strip()

        if not filename:
            return Response({
                'message': 'Missing filename'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not _is_safe_npy_filename(filename):
            return Response({
                'message': 'Invalid NPY filename'
            }, status=status.HTTP_400_BAD_REQUEST)

        resource_type = _get_npy_resource_type_from_filename(filename)

        if not resource_type:
            return Response({
                'message': 'Invalid NPY filename'
            }, status=status.HTTP_400_BAD_REQUEST)

        npy_root = _get_npy_file_root().resolve()
        npy_path = (npy_root / filename).resolve()

        try:
            npy_path.relative_to(npy_root)
        except ValueError:
            return Response({
                'message': 'Invalid NPY file path'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not npy_path.is_file():
            return Response({
                'message': 'NPY file not found'
            }, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            npy_path.open("rb"),
            as_attachment=True,
            filename=npy_path.name,
            content_type="application/octet-stream"
        )


class HomologyResourceListAPIView(APIView):
    def get(self, request):
        return Response({
            "code": 200,
            "message": "success",
            "data": list_homology_resource_files()
        }, status=status.HTTP_200_OK)


class HomologyResourceFileAPIView(APIView):
    def get(self, request):
        filename = request.GET.get('filename', '').strip()

        if not filename:
            return Response({
                'message': 'Missing filename'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not _is_safe_homology_filename(filename):
            return Response({
                'message': 'Invalid homology filename'
            }, status=status.HTTP_400_BAD_REQUEST)

        homology_root = _get_homology_file_root().resolve()
        homology_path = (homology_root / filename).resolve()

        try:
            homology_path.relative_to(homology_root)
        except ValueError:
            return Response({
                'message': 'Invalid homology file path'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not homology_path.is_file():
            return Response({
                'message': 'Homology result file not found'
            }, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            homology_path.open("rb"),
            as_attachment=True,
            filename=homology_path.name,
            content_type="application/octet-stream"
        )


class SnfResourceListAPIView(APIView):
    def get(self, request):
        return Response({
            "code": 200,
            "message": "success",
            "data": list_snf_resource_files()
        }, status=status.HTTP_200_OK)


class SnfResourceFileAPIView(APIView):
    def get(self, request):
        snf_file = _get_snf_file_path().resolve()

        if not snf_file.is_file():
            return Response({
                'message': 'SNF-related gene file not found'
            }, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            snf_file.open("rb"),
            as_attachment=True,
            filename=snf_file.name,
            content_type=_get_content_type(snf_file)
        )


class ProteinCifFileListAPIView(APIView):
    def get(self, request):
        return Response({
            "code": 200,
            "message": "success",
            "data": list_cif_resource_files()
        }, status=status.HTTP_200_OK)


class ProteinCifFileAPIView(APIView):
    def get(self, request):
        filename = request.GET.get('filename', '').strip()

        if filename:
            if not _is_safe_cif_filename(filename):
                return Response({
                    'message': 'Invalid CIF filename'
                }, status=status.HTTP_400_BAD_REQUEST)

            cif_root = _get_cif_file_root().resolve()
            cif_path = (cif_root / filename).resolve()

            try:
                cif_path.relative_to(cif_root)
            except ValueError:
                return Response({
                    'message': 'Invalid CIF file path'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not cif_path.is_file():
                return Response({
                    'message': 'CIF file not found'
                }, status=status.HTTP_404_NOT_FOUND)

            return FileResponse(
                cif_path.open("rb"),
                as_attachment=True,
                filename=cif_path.name,
                content_type="chemical/x-cif"
            )

        protein_id = request.GET.get('protein_id', '').strip()

        if not protein_id:
            return Response({
                'message': 'Missing protein_id'
            }, status=status.HTTP_400_BAD_REQUEST)

        item = ProteinInfo.objects.filter(protein_id=protein_id).first()

        if not item:
            return Response({
                'message': 'Protein not found'
            }, status=status.HTTP_404_NOT_FOUND)

        cif_file = get_cif_file_info(item)

        if not cif_file["exists"] or not cif_file["path"]:
            return Response({
                'message': 'CIF file not found',
                'cif_file': cif_file,
            }, status=status.HTTP_404_NOT_FOUND)

        cif_root = Path(getattr(settings, "PROTEIN_CIF_ROOT", settings.BASE_DIR.parent / "cif")).resolve()
        cif_path = Path(cif_file["path"]).resolve()

        try:
            cif_path.relative_to(cif_root)
        except ValueError:
            return Response({
                'message': 'Invalid CIF file path'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not cif_path.is_file():
            return Response({
                'message': 'CIF file not found',
                'cif_file': cif_file,
            }, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(
            cif_path.open("rb"),
            as_attachment=False,
            filename=cif_path.name,
            content_type="chemical/x-cif"
        )
        
