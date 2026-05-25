import math

import numpy as np

from api.models import SpeciesInfo

from .models import ProteinEmbedding


# ============================================================
# 全局参数
# ============================================================

# embedding 的维度。
# 你的数据库字段 embedding_norm 是 VARBINARY(2048)，
# 因为每个 embedding 是 512 维 float32。
#
# float32 每个数占 4 字节：
#   512 * 4 = 2048 bytes
DIM = 512


# NumPy 批量计算时，每次处理多少个目标蛋白向量。
#
# 注意：
# 这个值不是数据库读取 chunk。
# 这个值控制的是每次把多少个 embedding 拼成矩阵，然后做矩阵乘法。
#
# 如果太小：
#   NumPy 调用次数多，效率低。
#
# 如果太大：
#   内存占用变大，np.vstack 压力变大，可能反而变慢。
#
# 对 512 维 float32 向量，一般 5000~20000 都可以。
TARGET_CHUNK_SIZE = 10000


# ============================================================
# 自定义异常
# ============================================================

class SearchInputError(ValueError):
    """
    搜索输入错误。

    这个异常主要用于把后端错误清楚地返回给前端。

    例如：
    1. 找不到 query protein_id
    2. 找不到 target species
    3. protein_id 在多个物种中重复
    4. similarity_min / similarity_max 不合法
    5. embedding 维度不是 512

    data 用于保存额外信息，方便前端显示。
    """

    def __init__(self, message, data=None):
        super().__init__(message)
        self.data = data or {}


# ============================================================
# 二进制 embedding 转 numpy 向量
# ============================================================

def bytes_to_vec(value):
    """
    将数据库中的 embedding_norm 从二进制转回 numpy 向量。

    数据库中：
        embedding_norm VARBINARY(2048)

    Python 中：
        value 通常是 bytes；
        有时也可能是 memoryview。

    转换后：
        np.ndarray, dtype=float32, shape=(512,)

    为什么用 np.frombuffer？
        因为数据库存的是 float32 的原始字节。
        np.frombuffer 可以直接按 float32 解释这些字节。
    """

    # 某些数据库驱动可能返回 memoryview。
    # 为了兼容，先转成 bytes。
    if isinstance(value, memoryview):
        value = value.tobytes()

    # 按 float32 类型解析二进制内容。
    # 如果 value 长度是 2048 bytes，那么会得到 512 个 float32。
    vec = np.frombuffer(value, dtype=np.float32)

    # 检查维度是否正确。
    # 正常情况下应该是 512。
    if vec.shape[0] != DIM:
        raise SearchInputError(
            f"Vector dim error: expected {DIM}, got {vec.shape[0]}"
        )

    # 返回 float32 向量。
    # copy=False 表示尽量不复制，节省内存。
    return vec.astype(np.float32, copy=False)


# ============================================================
# species 查询
# ============================================================

def get_species(conservatory_genome_name):
    """
    根据 conservatory_genome_name 查询 species_info 表。

    conservatory_genome_name 是你前面导入 npy 文件时用的 prefix，
    例如：
        Zjujuba
        Zmays_493_RefGen_V4

    返回 dict，例如：
        {
            "id": 1,
            "species": "Zea mays",
            "genome_version": "RefGen_V4",
            "conservatory_genome_name": "Zmays_493_RefGen_V4"
        }

    如果查不到，抛出 SearchInputError。
    """

    species = (
        SpeciesInfo.objects
        .filter(conservatory_genome_name=conservatory_genome_name)
        .values(
            "id",
            "species",
            "genome_version",
            "conservatory_genome_name",
        )
        .first()
    )

    if species is None:
        raise SearchInputError(
            "Cannot find species.",
            {
                "conservatory_genome_name": conservatory_genome_name,
            },
        )

    return species


# ============================================================
# query protein 查询
# ============================================================

def get_query_embedding(protein_id, query_species_name=None):
    """
    获取 query protein 的 embedding。

    参数：
        protein_id:
            用户输入的查询蛋白 ID。

        query_species_name:
            查询蛋白所属物种的 conservatory_genome_name。
            这个参数可以为空。

    为什么 query_species_name 可以为空？
        如果 protein_id 在所有物种中唯一，那么可以不提供。
        如果 protein_id 在多个物种中都存在，就必须提供。

    原因：
        你的 protein_embedding 表是：
            UNIQUE(species_id, protein_id)

        所以 protein_id 不是全局唯一。
    """

    # 先按 protein_id 查询。
    # select_related("species") 用于关联 species_info 表。
    # values(...) 只取需要的字段，减少不必要的数据加载。
    queryset = (
        ProteinEmbedding.objects
        .select_related("species")
        .filter(protein_id=protein_id)
        .values(
            "species_id",
            "species__species",
            "species__genome_version",
            "species__conservatory_genome_name",
            "protein_id",
            "embedding_norm",
        )
    )

    # 如果用户指定 query_species_name，
    # 就进一步限制 species_id。
    if query_species_name:
        query_species = get_species(query_species_name)
        queryset = queryset.filter(species_id=query_species["id"])

    # 执行查询。
    rows = list(queryset)

    # 没有找到该 protein_id。
    if not rows:
        raise SearchInputError(
            "Cannot find query protein_id.",
            {
                "protein_id": protein_id,
                "query_species": query_species_name,
            },
        )

    # 如果找到多条，说明这个 protein_id 出现在多个物种里。
    # 这种情况下不能确定用户要查询哪个物种的 protein。
    if len(rows) > 1:
        matches = [
            {
                "species_id": row["species_id"],
                "species": row["species__species"],
                "genome_version": row["species__genome_version"],
                "conservatory_genome_name": row[
                    "species__conservatory_genome_name"
                ],
                "protein_id": row["protein_id"],
            }
            for row in rows
        ]

        raise SearchInputError(
            "protein_id is not unique across species. Please provide query_species.",
            {
                "protein_id": protein_id,
                "matches": matches,
            },
        )

    # 只找到唯一一条 query protein。
    row = rows[0]

    # 将数据库中的 VARBINARY(2048) 转回 float32[512]。
    query_vec = bytes_to_vec(row["embedding_norm"])

    # 理论上你的导入脚本已经做过 L2 normalization。
    # 这里再算一次 norm，是为了防止数据库中存在异常向量。
    query_norm = np.linalg.norm(query_vec)

    if query_norm == 0:
        raise SearchInputError("Query vector is zero vector.")

    # 再归一化一次。
    # 这样后面可以直接用点积计算 cosine similarity。
    query_vec = query_vec / query_norm

    return {
        "species_id": row["species_id"],
        "species": row["species__species"],
        "genome_version": row["species__genome_version"],
        "species_name": row["species__conservatory_genome_name"],
        "protein_id": row["protein_id"],
        "embedding": query_vec.astype(np.float32, copy=False),
    }


# ============================================================
# 相似度范围检查：只返回正相似度
# ============================================================

def validate_similarity_range(similarity_min, similarity_max):
    """
    检查 similarity_min 和 similarity_max 是否合法。

    这里严格只返回大于 0 的相似度。

    cosine similarity 的理论范围：
        -1 到 1

    搜索结果只保留正相似度，所以前端过滤范围只接受：
        0 到 100

    例如：
        similarity_min = 0
        similarity_max = 100
        表示返回所有正相似度结果。

        similarity_min = 20
        similarity_max = 100
        表示只返回相似度大于等于 20% 的正相似结果。

        similarity_min = 0
        similarity_max = 80
        表示只返回 80% 以内的正相似结果。
    """

    # 有些前端传过来的可能是字符串。
    # 这里可以尝试转成 float。
    try:
        similarity_min = float(similarity_min)
        similarity_max = float(similarity_max)
    except (TypeError, ValueError):
        raise SearchInputError("Similarity range must be numbers.")

    # 不能是 NaN、inf、-inf。
    if not math.isfinite(similarity_min) or not math.isfinite(similarity_max):
        raise SearchInputError("Similarity range must be finite numbers.")

    # 只接受 0 到 100。
    if similarity_min < 0 or similarity_max > 100:
        raise SearchInputError(
            "Similarity range must be between 0 and 100."
        )

    # 最小值不能大于最大值。
    if similarity_min > similarity_max:
        raise SearchInputError(
            "Minimum similarity cannot be greater than maximum similarity."
        )

    return similarity_min, similarity_max


# ============================================================
# 主搜索函数
# ============================================================

def protein_embedding_search(
    protein_id,
    target_species_name,
    similarity_min=0,
    similarity_max=100,
    query_species_name=None,
):
    """
    蛋白 embedding 相似性搜索。

    这个函数会：
        1. 找到 query protein 的 embedding
        2. 找到目标物种
        3. 遍历目标物种所有 protein embedding
        4. 计算 query 和每个 target protein 的 cosine similarity
        5. 按相似度从高到低排序
        6. 按 similarity_min 和 similarity_max 过滤
        7. 返回结果

    参数：
        protein_id:
            查询蛋白 ID。

        target_species_name:
            目标物种 conservatory_genome_name。
            会在这个物种的全部 protein_embedding 中搜索。

        similarity_min:
            最小相似度百分比。
            只支持 0 到 100。
            默认 0，表示只返回正相似度结果。

        similarity_max:
            最大相似度百分比。
            只支持 0 到 100。
            默认 100。

        query_species_name:
            查询蛋白所属物种 conservatory_genome_name。
            可选。
            如果 protein_id 在多个物种中重复，则必须提供。

    返回：
        dict，包含 query、target、filters、results、matched_count。
    """

    # 1. 检查并标准化相似度范围。
    similarity_min, similarity_max = validate_similarity_range(
        similarity_min,
        similarity_max,
    )

    # 2. 获取 query protein 的 embedding。
    query = get_query_embedding(
        protein_id=protein_id,
        query_species_name=query_species_name,
    )

    # 3. 获取目标物种信息。
    target_species = get_species(target_species_name)

    # 4. 读取目标物种下所有蛋白 embedding。
    #
    # 注意：
    # iterator(chunk_size=2000) 是数据库读取批量，
    # 不是 NumPy 计算批量。
    #
    # 这样可以避免一次性加载所有数据库记录。
    target_rows = (
        ProteinEmbedding.objects
        .filter(species_id=target_species["id"])
        .values_list("protein_id", "embedding_norm")
        .iterator(chunk_size=2000)
    )

    # 保存全部 target protein 的相似度结果。
    #
    # 注意：
    # 这是 Python 内存变量，不会写入数据库。
    # 请求结束后，这个变量就会被释放。
    scored_rows = []

    # 记录目标物种实际参与搜索的蛋白数量。
    target_count = 0

    # 当前 NumPy 计算批次中的 protein_id。
    chunk_protein_ids = []

    # 当前 NumPy 计算批次中的 embedding 向量。
    chunk_vectors = []

    def flush_chunk():
        """
        处理当前积累的一批 target embedding。

        假设当前 chunk 中有 N 个向量：
            chunk_vectors = [vec1, vec2, ..., vecN]

        每个向量 shape 是：
            (512,)

        np.vstack 后：
            matrix.shape = (N, 512)

        query["embedding"].shape 是：
            (512,)

        矩阵乘法：
            scores = matrix @ query["embedding"]

        得到：
            scores.shape = (N,)

        因为 query 和 target 都是归一化向量，
        所以这个点积结果就是 cosine similarity。
        """

        # 当前没有积累任何向量时，不做计算。
        if not chunk_vectors:
            return

        # 将 list of vectors 拼成二维矩阵。
        matrix = np.vstack(chunk_vectors).astype(np.float32, copy=False)

        # 计算 cosine similarity。
        # 如果 target 向量和 query 向量方向相似，score 接近 1。
        # 如果正交，score 接近 0。
        # 如果方向不相似，score 会接近或小于 0，后面会被过滤掉。
        scores = matrix @ query["embedding"]

        # 把当前 chunk 的结果追加到 scored_rows。
        # scored_rows 是完整搜索结果的临时内存表。
        scored_rows.extend(
            (target_protein_id, float(score))
            for target_protein_id, score in zip(chunk_protein_ids, scores)
        )

        # 清空当前 chunk，释放引用，准备处理下一批。
        chunk_protein_ids.clear()
        chunk_vectors.clear()

    # 5. 遍历目标物种的所有 protein embedding。
    for target_protein_id, embedding_norm in target_rows:
        target_count += 1

        # 保存当前 target protein 的 ID。
        chunk_protein_ids.append(target_protein_id)

        # 把数据库二进制 embedding 转成 numpy 向量。
        target_vec = bytes_to_vec(embedding_norm)

        # 注意：
        # 理论上导入数据库前已经对 target embedding 做过归一化。
        # 如果你不放心，也可以在这里重新归一化。
        # 但每个 target 都重新算 norm 会稍微增加计算时间。
        chunk_vectors.append(target_vec)

        # 如果当前 chunk 达到 TARGET_CHUNK_SIZE，就批量计算一次。
        if len(chunk_vectors) >= TARGET_CHUNK_SIZE:
            flush_chunk()

    # 6. 处理最后不足 TARGET_CHUNK_SIZE 的剩余向量。
    flush_chunk()

    # 如果目标物种没有任何 embedding，直接报错。
    if target_count == 0:
        raise SearchInputError(
            "No embeddings found for target species.",
            {
                "target_species": target_species_name,
            },
        )

    # 7. 所有结果按相似度从高到低排序。
    #
    # 注意：
    # 排序仍然先对全部分数进行，后面再只保留正相似度结果。
    # 例如完整分数可能包含正值、0，以及更低的分数。
    # 返回结果只会保留正值：
    #   0.9, 0.5, 0.1
    scored_rows.sort(key=lambda item: item[1], reverse=True)

    # 8. 把百分比范围转换成 cosine score 范围。
    #
    # 例如：
    #   0    -> 0.0
    #   80   -> 0.8
    #   100  -> 1.0
    min_score = similarity_min / 100.0
    max_score = similarity_max / 100.0

    # 浮点数比较容差。
    epsilon = 1e-7

    results = []

    # 9. 按过滤范围生成返回结果。
    for rank, (target_protein_id, score) in enumerate(scored_rows, start=1):

        # 只保留正相似度。
        # 0 或更小的相似度都不返回。
        if score <= epsilon:
            continue

        # 如果小于最小相似度，跳过。
        if score + epsilon < min_score:
            continue

        # 如果大于最大相似度，跳过。
        if score - epsilon > max_score:
            continue

        # 当前接口只返回正相似度，方便前端统一显示。
        similarity_type = "positive"

        results.append({
            # rank 是在所有 target protein 中按相似度排序后的全局排名。
            # 注意：
            # rank 不是过滤后的第几个，而是全部结果排序中的名次。
            "rank": rank,
            # query 信息
                "query_species": query["species"],
                "query_genome_version": query["genome_version"],
                "query_conservatory_genome_name": query["species_name"],
                "query_species_id": query["species_id"],
                "query_protein_id": query["protein_id"],

            # target 信息
            "target_species": target_species["species"],
            "target_genome_version": target_species["genome_version"],
            "target_conservatory_genome_name": target_species["conservatory_genome_name"],
            "target_species_id": target_species["id"],
            "target_protein_id": target_protein_id,

            # cosine similarity 原始值，理论范围是 -1 到 1。
            # 当前返回值一定大于 0。
            "cosine_similarity": round(score, 6),

            # 百分比形式，当前返回值一定大于 0。
            "cosine_similarity_percent": round(score * 100, 4),

            # 当前接口只返回 positive。
            "similarity_type": similarity_type,
        })

    # 10. 返回完整搜索结果。
    return {
        "query": {
            "species_id": query["species_id"],
            "species": query["species"],
            "genome_version": query["genome_version"],
            "conservatory_genome_name": query["species_name"],
            "protein_id": query["protein_id"],
            "vector_dim": DIM,
        },
        "target": {
            "species_id": target_species["id"],
            "species": target_species["species"],
            "genome_version": target_species["genome_version"],
            "conservatory_genome_name": target_species[
                "conservatory_genome_name"
            ],
            "protein_count": target_count,
        },
        "filters": {
            "similarity_min": similarity_min,
            "similarity_max": similarity_max,
            "score_min": min_score,
            "score_max": max_score,
        },
        "results": results,
        "matched_count": len(results),
    }
