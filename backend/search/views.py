from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import (
    SearchInputError,
    get_example_protein,
    protein_embedding_search,
)


def get_float_param(request, *names, default=None):
    """
    从 GET 参数中读取 float 类型参数。

    支持多个参数名别名。
    例如：
        get_float_param(request, "similarity_min", "min_similarity", default=0)

    表示优先读取 similarity_min；
    如果没有，再读取 min_similarity；
    如果都没有，返回 default。
    """
    for name in names:
        value = request.GET.get(name)

        if value not in (None, ""):
            try:
                return float(value)
            except ValueError as exc:
                raise SearchInputError(f"{name} must be a number.") from exc

    return default


class ProteinEmbeddingSearchAPIView(APIView):
    """
    蛋白 embedding 相似性搜索 API。

    示例请求：

    1. 默认返回所有正相似度：
       /api/protein-embedding-search/?protein_id=xxx&target_species=Zjujuba

    2. 只返回指定范围内的正相似：
       /api/protein-embedding-search/?protein_id=xxx&target_species=Zjujuba&similarity_min=20&similarity_max=100

    3. 如果 protein_id 在多个物种中重复，需要指定 query_species：
       /api/protein-embedding-search/?protein_id=xxx&query_species=Zmays_493_RefGen_V4&target_species=Zjujuba
    """

    def get(self, request):
        """
        处理 GET 请求。
        """

        # 读取 query protein id。
        protein_id = request.GET.get("protein_id", "").strip()

        # 读取目标物种。
        target_species = request.GET.get("target_species", "").strip()

        # 读取 query 所属物种。
        # 如果没有传，则转成 None。
        query_species = request.GET.get("query_species", "").strip() or None

        # protein_id 是必填参数。
        if not protein_id:
            return Response(
                {
                    "code": 400,
                    "message": "protein_id is required",
                    "data": [],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # target_species 是必填参数。
        if not target_species:
            return Response(
                {
                    "code": 400,
                    "message": "target_species is required",
                    "data": [],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # 读取最小相似度。
            #
            # 支持两个参数名：
            #   similarity_min
            #   min_similarity
            #
            # 默认 0，表示默认只返回正相似度。
            similarity_min = get_float_param(
                request,
                "similarity_min",
                "min_similarity",
                default=0,
            )

            # 读取最大相似度。
            #
            # 支持两个参数名：
            #   similarity_max
            #   max_similarity
            #
            # 默认 100。
            similarity_max = get_float_param(
                request,
                "similarity_max",
                "max_similarity",
                default=100,
            )

            # 调用真正的 embedding 搜索函数。
            payload = protein_embedding_search(
                protein_id=protein_id,
                target_species_name=target_species,
                similarity_min=similarity_min,
                similarity_max=similarity_max,
                query_species_name=query_species,
            )

            # 搜索成功，返回结果。
            return Response(
                {
                    "code": 200,
                    "message": "success",
                    "data": payload["results"],
                    "meta": {
                        "query": payload["query"],
                        "target": payload["target"],
                        "filters": payload["filters"],
                        "matched_count": payload["matched_count"],
                    },
                },
                status=status.HTTP_200_OK,
            )

        except SearchInputError as exc:
            # 业务输入错误，例如：
            # - species 找不到
            # - protein_id 找不到
            # - protein_id 不唯一
            # - similarity_min / similarity_max 非法
            return Response(
                {
                    "code": 400,
                    "message": str(exc),
                    "data": [],
                    "meta": exc.data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ExampleProteinAPIView(APIView):
    def get(self, request):
        query_species = request.GET.get("query_species", "").strip()

        if not query_species:
            return Response(
                {
                    "code": 400,
                    "message": "query_species is required",
                    "data": None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload = get_example_protein(query_species)
        except SearchInputError as exc:
            return Response(
                {
                    "code": 400,
                    "message": str(exc),
                    "data": None,
                    "meta": exc.data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "code": 200,
                "message": "success",
                "data": payload,
            },
            status=status.HTTP_200_OK,
        )
