import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .blastp_utils import run_combined_protein_alignment
from .structure_align_utils import run_usalign

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