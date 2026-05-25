import logging
import os
import re
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from django.conf import settings


"""
US-align 结构比对后端工具函数。

建议保存位置：
    backend/tools/usalign_utils.py

主入口函数：
    run_usalign(structure_file_1, structure_file_2)

这个文件主要完成以下工作：
    1. 检查用户上传的结构文件是否合法。
    2. 把上传文件保存到临时工作目录。
    3. 调用 US-align 进行结构比对。
    4. 解析 US-align 的文本输出结果。
    5. 把前端 3D 可视化需要的结构文件保存到 MEDIA_ROOT。
    6. 返回前端页面需要的结构化结果。

特别注意文件名区别：

    US-align 原始输出：
        sup.cif / sup.pdb

    后端保存到 media 目录后的输出：
        superposed.cif / superposed.pdb

    也就是说：
        superposed.cif 是由 US-align 生成的 sup.cif 复制并重命名得到的。
        它们表示的都是“叠合后的 Structure 1”。

前端 3D 显示时通常加载两个模型：
    1. superposedStructure1Url：叠合后的 Structure 1，通常显示为蓝色。
    2. referenceStructure2Url：原始 Structure 2，通常显示为红色。
"""


# 使用 logging 代替 print，方便以后调试和部署。
logger = logging.getLogger(__name__)


# ============================================================
# 1. 基础配置
# ============================================================

# 后端允许上传的结构文件后缀。
#
# 注意：
# 前端的 accept=".pdb,.cif,.mmcif" 只是限制文件选择窗口，
# 不能作为真正的安全校验。
# 因此后端必须再次检查文件后缀。
ALLOWED_STRUCTURE_EXTENSIONS = {".pdb", ".cif", ".mmcif"}

# US-align 输出文件前缀。
#
# 当命令中使用：
#   USalign structure_1.cif structure_2.cif -o sup
#
# US-align 通常会生成：
#   sup.cif 或 sup.pdb
#   sup.pml
#   sup_all.pml
#   sup_atm.pml
#   sup_all_atm.pml
#   sup_all_atm_lig.pml
#
# 其中 sup.cif / sup.pdb 才是前端 3Dmol.js 需要加载的坐标文件。
USALIGN_OUTPUT_PREFIX = "sup"


# ============================================================
# 2. 通用辅助函数
# ============================================================

def get_file_extension(filename: str) -> str:
    """
    获取文件后缀，并统一转换成小写。

    示例：
        1.cif       -> .cif
        model.PDB   -> .pdb
        test.mmcif  -> .mmcif
    """
    return Path(filename).suffix.lower()


def get_structure_format_from_ext(ext: str) -> str:
    """
    根据文件后缀，返回前端 3Dmol.js 需要的格式名称。

    对 3Dmol.js 来说：
        .pdb   -> "pdb"
        .cif   -> "cif"
        .mmcif -> "cif"

    如果是不支持的后缀，则返回空字符串。
    """
    ext = ext.lower()

    if ext == ".pdb":
        return "pdb"

    if ext in {".cif", ".mmcif"}:
        return "cif"

    return ""


def safe_float(value, default: Optional[float] = None) -> Optional[float]:
    """
    安全地把 value 转换成 float。

    如果 value 是 None、"-"、空字符串，或者无法转换成数字，
    就返回 default。
    """
    try:
        if value in [None, "-", ""]:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default: Optional[int] = None) -> Optional[int]:
    """
    安全地把 value 转换成 int。

    如果 value 是 None、"-"、空字符串，或者无法转换成整数，
    就返回 default。
    """
    try:
        if value in [None, "-", ""]:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def validate_structure_file(uploaded_file) -> str:
    """
    校验上传的结构文件是否合法。

    检查内容：
        1. 文件对象是否存在。
        2. 文件后缀是否是 .pdb / .cif / .mmcif。
        3. 文件大小是否超过限制。

    返回：
        文件后缀，例如：".pdb"、".cif"、".mmcif"。

    抛出：
        ValueError。错误信息可以直接返回给前端。

    注意：
        这个函数只做基础校验。
        它不能保证文件内容一定是真正合法的 PDB/mmCIF。
        如果文件内容不合法，后续 US-align 会运行失败，
        run_usalign() 会把失败转换成更清楚的错误信息。
    """
    if not uploaded_file:
        raise ValueError("Missing uploaded structure file.")

    ext = get_file_extension(uploaded_file.name)

    if ext not in ALLOWED_STRUCTURE_EXTENSIONS:
        raise ValueError("Only .pdb, .cif, and .mmcif files are allowed.")

    # 默认最大 50 MB。
    # 可以在 settings.py 中自定义：
    #   STRUCTURE_UPLOAD_MAX_SIZE = 100 * 1024 * 1024
    max_size = getattr(settings, "STRUCTURE_UPLOAD_MAX_SIZE", 50 * 1024 * 1024)

    if uploaded_file.size > max_size:
        max_size_mb = round(max_size / 1024 / 1024, 1)
        raise ValueError(f"Uploaded file is too large. Maximum allowed size is {max_size_mb} MB.")

    return ext


def save_uploaded_file(uploaded_file, output_path: Path) -> None:
    """
    把 Django UploadedFile 保存到磁盘。

    使用 uploaded_file.chunks()，避免大文件一次性读入内存。
    这是 Django 处理上传文件时更推荐的写法。
    """
    with open(output_path, "wb") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)


def cleanup_old_structure_align_jobs(max_age_hours: int = 24) -> None:
    """
    清理 MEDIA_ROOT/structure_align/ 下过期的结构比对结果目录。

    目录结构类似：
        MEDIA_ROOT/structure_align/<job_id>/

    参数：
        max_age_hours:
            保留最近多少小时的结果。
            默认 24 表示保留最近 24 小时的结果。

    开发阶段说明：
        开发阶段可以在每次运行 run_usalign() 前清理一次。

    正式部署建议：
        不建议每次请求都扫描目录。
        更推荐用 cron、Celery beat 或服务器定时任务定期清理。
    """
    media_root = getattr(settings, "MEDIA_ROOT", None)

    if not media_root:
        return

    base_dir = Path(media_root) / "structure_align"

    if not base_dir.exists():
        return

    now = time.time()
    max_age_seconds = max_age_hours * 3600

    for job_dir in base_dir.iterdir():
        if not job_dir.is_dir():
            continue

        try:
            age_seconds = now - job_dir.stat().st_mtime

            if age_seconds > max_age_seconds:
                shutil.rmtree(job_dir)
                logger.info("Deleted old structure alignment job: %s", job_dir)

        except Exception as exc:
            logger.warning("Failed to delete old structure alignment job %s: %s", job_dir, exc)


# ============================================================
# 3. 解析 US-align 输出：统计指标
# ============================================================

def parse_usalign_metrics(raw_output: str) -> Dict:
    """
    从 US-align 的 stdout 文本中解析核心统计指标。

    目标解析字段：
        - Structure 1 name
        - Structure 2 name
        - Structure 1 length
        - Structure 2 length
        - Aligned length
        - RMSD
        - Seq_ID
        - TM-score 1，也就是按 Structure 1 长度归一化的 TM-score
        - TM-score 2，也就是按 Structure 2 长度归一化的 TM-score
        - Structure 1 coverage
        - Structure 2 coverage
        - Seq_ID 百分比

    典型 US-align 输出示例：
        Name of Structure_1: structure_1.cif:A
        Name of Structure_2: structure_2.cif:A
        Length of Structure_1: 128 residues
        Length of Structure_2: 1476 residues

        Aligned length= 94, RMSD=   4.82, Seq_ID=n_identical/n_aligned= 0.064
        TM-score= 0.42701 (normalized by length of Structure_1: L=128, d0=4.19)
        TM-score= 0.05599 (normalized by length of Structure_2: L=1476, d0=12.27)
    """
    result = {
        "structure1Name": "-",
        "structure2Name": "-",
        "structure1Length": "-",
        "structure2Length": "-",
        "alignedLength": "-",
        "rmsd": "-",
        "seqId": "-",
        "tmScore1": "-",
        "tmScore2": "-",
        "coverage1": "-",
        "coverage2": "-",
        "seqIdPercent": "-",
    }

    # -------------------------------
    # 3.1 解析结构名称
    # -------------------------------
    name1_match = re.search(
        r"Name\s+of\s+Structure_?1\s*:\s*(.+)",
        raw_output,
        flags=re.IGNORECASE,
    )
    name2_match = re.search(
        r"Name\s+of\s+Structure_?2\s*:\s*(.+)",
        raw_output,
        flags=re.IGNORECASE,
    )

    if name1_match:
        result["structure1Name"] = name1_match.group(1).strip()

    if name2_match:
        result["structure2Name"] = name2_match.group(1).strip()

    # -------------------------------
    # 3.2 解析结构长度
    # -------------------------------
    length1_match = re.search(
        r"Length\s+of\s+Structure_?1\s*:\s*(\d+)",
        raw_output,
        flags=re.IGNORECASE,
    )
    length2_match = re.search(
        r"Length\s+of\s+Structure_?2\s*:\s*(\d+)",
        raw_output,
        flags=re.IGNORECASE,
    )

    if length1_match:
        result["structure1Length"] = int(length1_match.group(1))

    if length2_match:
        result["structure2Length"] = int(length2_match.group(1))

    # -------------------------------
    # 3.3 解析 Aligned length / RMSD / Seq_ID
    # -------------------------------
    aligned_match = re.search(
        r"Aligned\s+length\s*=\s*(\d+)\s*,\s*"
        r"RMSD\s*=\s*([0-9]*\.?[0-9]+)\s*,\s*"
        r"Seq_ID\s*=\s*[^=]*=\s*([0-9]*\.?[0-9]+)",
        raw_output,
        flags=re.IGNORECASE,
    )

    if aligned_match:
        result["alignedLength"] = int(aligned_match.group(1))
        result["rmsd"] = float(aligned_match.group(2))
        result["seqId"] = float(aligned_match.group(3))
    else:
        # 兼容不同版本 US-align 输出格式略有变化的情况。
        aligned_length_match = re.search(
            r"Aligned\s+length\s*=\s*(\d+)",
            raw_output,
            flags=re.IGNORECASE,
        )
        rmsd_match = re.search(
            r"RMSD\s*=\s*([0-9]*\.?[0-9]+)",
            raw_output,
            flags=re.IGNORECASE,
        )
        seqid_match = re.search(
            r"Seq_ID.*?=\s*([0-9]*\.?[0-9]+)\s*$",
            raw_output,
            flags=re.IGNORECASE | re.MULTILINE,
        )

        if aligned_length_match:
            result["alignedLength"] = int(aligned_length_match.group(1))

        if rmsd_match:
            result["rmsd"] = float(rmsd_match.group(1))

        if seqid_match:
            result["seqId"] = float(seqid_match.group(1))

    # -------------------------------
    # 3.4 解析两个 TM-score
    # -------------------------------
    # US-align 通常会输出两个 TM-score：
    #   第一个：normalized by length of Structure_1
    #   第二个：normalized by length of Structure_2
    #
    # 如果两个结构长度差异很大，这两个 TM-score 可能差别很大。
    tm_matches = re.findall(
        r"TM-score\s*=\s*([0-9]*\.?[0-9]+)\s*\(([^)]*)\)",
        raw_output,
        flags=re.IGNORECASE,
    )

    if len(tm_matches) >= 1:
        result["tmScore1"] = float(tm_matches[0][0])

    if len(tm_matches) >= 2:
        result["tmScore2"] = float(tm_matches[1][0])

    # 如果没有括号内容，则退而求其次，只提取 TM-score 数值。
    if result["tmScore1"] == "-" or result["tmScore2"] == "-":
        tm_scores = re.findall(
            r"TM-score\s*=\s*([0-9]*\.?[0-9]+)",
            raw_output,
            flags=re.IGNORECASE,
        )

        if len(tm_scores) >= 1:
            result["tmScore1"] = float(tm_scores[0])

        if len(tm_scores) >= 2:
            result["tmScore2"] = float(tm_scores[1])

    # -------------------------------
    # 3.5 计算 coverage
    # -------------------------------
    # coverage1 = aligned length / Structure 1 length * 100
    # coverage2 = aligned length / Structure 2 length * 100
    aligned_length = safe_int(result["alignedLength"])
    length1 = safe_int(result["structure1Length"])
    length2 = safe_int(result["structure2Length"])

    if aligned_length is not None and length1:
        result["coverage1"] = round(aligned_length / length1 * 100, 2)

    if aligned_length is not None and length2:
        result["coverage2"] = round(aligned_length / length2 * 100, 2)

    # -------------------------------
    # 3.6 计算 Seq_ID 百分比
    # -------------------------------
    seq_id = safe_float(result["seqId"])

    if seq_id is not None:
        result["seqIdPercent"] = round(seq_id * 100, 2)

    return result


# ============================================================
# 4. 解析 US-align 输出：残基比对文本
# ============================================================

def is_alignment_sequence_line(line: str) -> bool:
    """
    判断某一行是否像 US-align 的残基序列行。

    US-align 残基序列行通常只包含：
        - 大写字母 A-Z
        - gap 符号 '-'

    示例：
        MAAAA---BBBBB
    """
    stripped = line.strip()

    if not stripped:
        return False

    if stripped.startswith("#"):
        return False

    # 排除明显不是序列行的统计信息行。
    excluded_keywords = [
        "TM-score",
        "RMSD",
        "Aligned length",
        "Name of Structure",
        "Length of Structure",
    ]

    if any(keyword.lower() in stripped.lower() for keyword in excluded_keywords):
        return False

    return bool(re.fullmatch(r"[A-Z\-]+", stripped))


def is_alignment_match_line(line: str) -> bool:
    """
    判断某一行是否像 US-align 的 match line。

    US-align 的 match line 中：
        ':' 表示两个残基的空间距离 < 5.0 Å。
        '.' 表示其他 aligned residues。
        空格表示该列没有明显结构对应关系。
    """
    if not line:
        return False

    if ":" not in line and "." not in line:
        return False

    # 如果去掉 ':'、'.' 和空格之后没有其他字符，说明它是 match line。
    cleaned = line.replace(":", "").replace(".", "").replace(" ", "")
    return cleaned == ""


def extract_alignment_triple(raw_output: str) -> Optional[Tuple[str, str, str]]:
    """
    从 US-align 输出中提取三行残基结构比对：

        seq1
        match_line
        seq2

    返回：
        (seq1, match_line, seq2)

    如果没有找到，则返回 None。

    典型输出片段：
        (":" denotes residue pairs of d < 5.0 Angstrom, "." denotes other aligned residues)
        SEQUENCE1----
        :::::....
        SEQUENCE2----

    注意：
        match_line 中的空格是有意义的。
        因此不能对 match_line 使用 strip() 去掉左侧空格。
    """
    lines = raw_output.splitlines()

    start_index = None

    # US-align 通常会在残基比对前三行之前写一行说明文字。
    # 通过这行说明定位残基比对开始位置。
    for i, line in enumerate(lines):
        lower_line = line.lower()
        if "denotes residue pairs" in lower_line and "angstrom" in lower_line:
            start_index = i + 1
            break

    if start_index is None:
        return None

    candidate_lines = lines[start_index:]

    seq1 = None
    match_line = None
    seq2 = None

    for line in candidate_lines:
        if seq1 is None and is_alignment_sequence_line(line):
            seq1 = line.strip()
            continue

        if seq1 is not None and match_line is None and is_alignment_match_line(line):
            # 不能 strip 左侧空格，因为空格位置有意义。
            match_line = line.rstrip("\n")
            continue

        if seq1 is not None and match_line is not None and seq2 is None and is_alignment_sequence_line(line):
            seq2 = line.strip()
            break

    if not seq1 or match_line is None or not seq2:
        return None

    # 补齐三行长度，方便前端逐列渲染。
    max_len = max(len(seq1), len(match_line), len(seq2))
    seq1 = seq1.ljust(max_len)
    match_line = match_line.ljust(max_len)
    seq2 = seq2.ljust(max_len)

    return seq1, match_line, seq2


def build_alignment_blocks(
    seq1: str,
    match_line: str,
    seq2: str,
    block_size: int = 100,
    only_aligned_region: bool = False,
) -> List[Dict]:
    """
    把残基比对切成多个 block，方便前端显示。

    参数：
        seq1:
            Structure 1 的比对残基序列。

        match_line:
            US-align 的 match line。
            ':' 和 '.' 表示结构对应关系。

        seq2:
            Structure 2 的比对残基序列。

        block_size:
            每个 block 显示多少列。
            默认 60，比较适合网页显示，不容易横向溢出。

        only_aligned_region:
            True：只返回包含 ':' 或 '.' 的 block。
            False：返回完整比对 block。

    关于 start/end：
        struc1Start / struc1End / struc2Start / struc2End
        是根据 US-align 输出序列中的非 gap 字符累计得到的。

        它们可以理解为“US-align 提取序列中的位置”，
        不一定等于 PDB/mmCIF 文件中的原始 residue number。
    """
    blocks: List[Dict] = []

    pos1 = 0
    pos2 = 0

    max_len = max(len(seq1), len(match_line), len(seq2))
    seq1 = seq1.ljust(max_len)
    match_line = match_line.ljust(max_len)
    seq2 = seq2.ljust(max_len)

    for start in range(0, max_len, block_size):
        end = start + block_size

        chunk1 = seq1[start:end]
        chunk_match = match_line[start:end]
        chunk2 = seq2[start:end]

        non_gap_1 = [c for c in chunk1 if c not in {"-", " "}]
        non_gap_2 = [c for c in chunk2 if c not in {"-", " "}]

        # 如果只展示 aligned region，跳过完全没有 ':' 或 '.' 的 block。
        # 但是即使跳过显示，也必须继续累计 pos1 / pos2。
        if only_aligned_region and ":" not in chunk_match and "." not in chunk_match:
            pos1 += len(non_gap_1)
            pos2 += len(non_gap_2)
            continue

        if non_gap_1:
            struc1_start = pos1 + 1
            struc1_end = pos1 + len(non_gap_1)
        else:
            struc1_start = "-"
            struc1_end = "-"

        if non_gap_2:
            struc2_start = pos2 + 1
            struc2_end = pos2 + len(non_gap_2)
        else:
            struc2_start = "-"
            struc2_end = "-"

        blocks.append(
            {
                "struc1Start": struc1_start,
                "struc1End": struc1_end,
                "struc2Start": struc2_start,
                "struc2End": struc2_end,
                "seq1": chunk1.rstrip(),
                "seq2": chunk2.rstrip(),
                "matchLine": chunk_match.rstrip(),
            }
        )

        pos1 += len(non_gap_1)
        pos2 += len(non_gap_2)

    return blocks


def parse_usalign_alignment(raw_output: str, block_size: int = 60) -> Dict:
    """
    解析 US-align 输出中的残基结构比对文本。

    返回字段：
        alignmentSeq1
        alignmentSeq2
        alignmentMatchLine
        wholeAlignmentBlocks
        alignmentBlocks

    如果没有解析到三行比对文本，则返回空字符串和空列表。
    这不应该影响统计值展示。
    """
    triple = extract_alignment_triple(raw_output)

    if triple is None:
        return {
            "alignmentSeq1": "",
            "alignmentSeq2": "",
            "alignmentMatchLine": "",
            "wholeAlignmentBlocks": [],
            "alignmentBlocks": [],
        }

    seq1, match_line, seq2 = triple

    whole_blocks = build_alignment_blocks(
        seq1=seq1,
        match_line=match_line,
        seq2=seq2,
        block_size=block_size,
        only_aligned_region=False,
    )

    aligned_blocks = build_alignment_blocks(
        seq1=seq1,
        match_line=match_line,
        seq2=seq2,
        block_size=block_size,
        only_aligned_region=True,
    )

    return {
        "alignmentSeq1": seq1.rstrip(),
        "alignmentSeq2": seq2.rstrip(),
        "alignmentMatchLine": match_line.rstrip(),
        "wholeAlignmentBlocks": whole_blocks,
        "alignmentBlocks": aligned_blocks,
    }


# ============================================================
# 5. 根据比对结果生成前端提示文字
# ============================================================

# def build_interpretation(metrics: Dict) -> str:
#     """
#     根据 US-align 的统计指标生成简单的生物学解释。

#     重点理解 TM-score：
#         US-align 会返回两个 TM-score：

#         tmScore1：
#             按 Structure 1 长度归一化。

#         tmScore2：
#             按 Structure 2 长度归一化。

#     为什么需要两个 TM-score？
#         如果两个结构长度差异很大，例如一个小结构比对到一个大结构的局部区域，
#         可能出现：
#             tmScore1 很高
#             tmScore2 很低

#         这种情况通常表示：
#             Structure 1 可以很好地匹配 Structure 2 的一部分，
#             但两个完整结构并不是全局相似。

#     注意：
#         这些解释是给前端用户看的启发式解释，
#         不是严格的生物学分类规则。
#     """
#     tm1 = safe_float(metrics.get("tmScore1"))
#     tm2 = safe_float(metrics.get("tmScore2"))
#     rmsd = safe_float(metrics.get("rmsd"))
#     coverage1 = safe_float(metrics.get("coverage1"))
#     coverage2 = safe_float(metrics.get("coverage2"))

#     if tm1 is None or tm2 is None:
#             return "US-align completed, but TM-scores could not be parsed."

#     if tm1 >= 0.5 and tm2 >= 0.5:
#             if rmsd is not None and rmsd <= 3.0:
#                 return "The two structures show strong overall structural similarity."
#             return "The two structures likely share a similar overall fold."

#     if tm1 >= 0.5 and tm2 < 0.5:
#             return "Structure 1 matches a local region of Structure 2."

#     if tm2 >= 0.5 and tm1 < 0.5:
#             return "Structure 2 matches a local region of Structure 1."

#     if tm1 < 0.2 and tm2 < 0.2:
#             return "The two structures show weak structural similarity."

#     if coverage1 is not None and coverage2 is not None:
#             if coverage1 >= 60 and coverage2 <= 50:
#                 return "Structure 1 aligns to a partial region of Structure 2."
#             if coverage2 >= 60 and coverage1 <= 50:
#                 return "Structure 2 aligns to a partial region of Structure 1."

#     if 0.2 <= tm1 < 0.5 and 0.2 <= tm2 < 0.5:
#             if rmsd is not None and rmsd <= 4.0:
#                 return "The structures share a partially similar aligned core."
#             return "The structures show limited partial similarity."

#     return "The structures show limited or partial structural similarity."


def build_status_message(metrics: Dict, has_superposed_file: bool) -> str:
    """
    生成一个简短的运行状态提示。

    statusMessage 和 interpretation 的区别：

        statusMessage：
            说明 US-align 是否运行成功，
            以及是否找到了可用于 3D 可视化的叠合结构文件。

        interpretation：
            根据 TM-score、RMSD、coverage 等指标解释结构相似性。
    """
    tm1 = safe_float(metrics.get("tmScore1"))
    tm2 = safe_float(metrics.get("tmScore2"))

    if tm1 is None or tm2 is None:
        return "US-align completed, but key statistics were not fully parsed. Please check the raw output."

    if not has_superposed_file:
        return "US-align completed, but no superposed structure file was found for 3D visualization. Statistics are still available."

    return "US-align completed successfully. The superposed structure is available for 3D visualization."


# ============================================================
# 6. 保存结果文件到 MEDIA_ROOT
# ============================================================

def ensure_media_job_dir(job_id: str) -> Path:
    """
    为一次结构比对任务创建 media 输出目录。

    输出目录：
        MEDIA_ROOT/structure_align/<job_id>/

    settings.py 中需要设置：
        MEDIA_URL = "/media/"
        MEDIA_ROOT = BASE_DIR / "media"
    """
    media_root = getattr(settings, "MEDIA_ROOT", None)

    if not media_root:
        raise RuntimeError("MEDIA_ROOT is not configured in settings.py.")

    output_dir = Path(media_root) / "structure_align" / job_id
    output_dir.mkdir(parents=True, exist_ok=True)

    return output_dir


def build_media_url(job_id: str, filename: str) -> str:
    """
    根据 job_id 和文件名生成前端可以访问的 media URL。

    示例：
        /media/structure_align/<job_id>/superposed.cif
    """
    media_url = getattr(settings, "MEDIA_URL", "/media/")
    return f"{media_url.rstrip('/')}/structure_align/{job_id}/{filename}"


def save_file_to_media(
    source_path: Path,
    output_filename: str,
    job_id: str,
) -> str:
    """
    把一个文件复制到当前任务的 media 目录，并返回它的 URL。
    """
    if not source_path.exists() or not source_path.is_file():
        raise FileNotFoundError(f"Source file does not exist: {source_path}")

    output_dir = ensure_media_job_dir(job_id)
    output_path = output_dir / output_filename

    shutil.copy2(source_path, output_path)

    logger.info(
        "Saved media file: source=%s output=%s size=%s",
        source_path,
        output_path,
        output_path.stat().st_size if output_path.exists() else "missing",
    )

    return build_media_url(job_id, output_filename)


def find_usalign_superposed_structure(
    tmpdir_path: Path,
    output_prefix: str = USALIGN_OUTPUT_PREFIX,
) -> Optional[Path]:
    """
    在临时目录中查找 US-align 生成的“叠合后的 Structure 1”文件。

    当运行：
        USalign structure_1.cif structure_2.cif -o sup

    US-align 可能生成：
        sup.cif
        sup.pdb
        sup.pml
        sup_all.pml
        ...

    前端 3D 可视化真正需要的是坐标文件：
        sup.cif 或 sup.pdb

    查找顺序：
        1. sup.cif
        2. sup*.cif
        3. sup.pdb
        4. sup*.pdb
    """
    candidate_files: List[Path] = []

    candidate_files.extend(sorted(tmpdir_path.glob(f"{output_prefix}.cif")))
    candidate_files.extend(sorted(tmpdir_path.glob(f"{output_prefix}*.cif")))
    candidate_files.extend(sorted(tmpdir_path.glob(f"{output_prefix}.pdb")))
    candidate_files.extend(sorted(tmpdir_path.glob(f"{output_prefix}*.pdb")))

    seen = set()

    for file_path in candidate_files:
        resolved = str(file_path.resolve())

        if resolved in seen:
            continue

        seen.add(resolved)

        if not file_path.exists() or not file_path.is_file():
            continue

        if file_path.stat().st_size <= 0:
            continue

        ext = file_path.suffix.lower()
        if ext in ALLOWED_STRUCTURE_EXTENSIONS:
            return file_path

    return None


def save_superposed_structure_from_tmpdir(
    tmpdir_path: Path,
    job_id: str,
    output_prefix: str = USALIGN_OUTPUT_PREFIX,
) -> Dict:
    """
    保存 US-align 生成的叠合后 Structure 1 文件。

    US-align 原始文件：
        sup.cif / sup.pdb

    后端保存到 MEDIA_ROOT 后重新命名为：
        superposed.cif / superposed.pdb

    为什么要重命名？
        sup.cif 是 US-align 的默认名字。
        superposed.cif 对前端和用户来说更直观，
        表示这是“叠合后的结构”。

    返回：
        {
            "superposedStructureUrl": "/media/structure_align/<job_id>/superposed.cif",
            "superposedStructureFormat": "cif",
            "superposedStructureOriginalName": "sup.cif"
        }
    """
    source_file = find_usalign_superposed_structure(
        tmpdir_path=tmpdir_path,
        output_prefix=output_prefix,
    )

    if source_file is None:
        logger.warning("No superposed structure file found in tmpdir: %s", tmpdir_path)
        return {
            "superposedStructureUrl": "",
            "superposedStructureFormat": "",
            "superposedStructureOriginalName": "",
        }

    source_ext = source_file.suffix.lower()
    structure_format = get_structure_format_from_ext(source_ext)

    if not structure_format:
        logger.warning("Unsupported superposed structure extension: %s", source_ext)
        return {
            "superposedStructureUrl": "",
            "superposedStructureFormat": "",
            "superposedStructureOriginalName": source_file.name,
        }

    output_name = "superposed.cif" if structure_format == "cif" else "superposed.pdb"
    structure_url = save_file_to_media(source_file, output_name, job_id)

    return {
        "superposedStructureUrl": structure_url,
        "superposedStructureFormat": structure_format,
        "superposedStructureOriginalName": source_file.name,
    }


def save_reference_structure_to_media(
    reference_path: Path,
    reference_ext: str,
    job_id: str,
) -> Dict:
    """
    保存原始 Structure 2 到 MEDIA_ROOT。

    为什么需要保存 Structure 2？
        US-align 使用 -o sup 时，只会输出叠合后的 Structure 1。
        它不会额外输出一份 Structure 2。

        但是前端要显示结构叠合，需要同时加载两个模型：
            model 0：叠合后的 Structure 1
            model 1：原始 Structure 2，作为参考结构

    返回：
        {
            "referenceStructure2Url": "/media/structure_align/<job_id>/reference_structure_2.cif",
            "referenceStructure2Format": "cif"
        }
    """
    if not reference_path.exists() or not reference_path.is_file():
        logger.warning("Reference Structure 2 file does not exist: %s", reference_path)
        return {
            "referenceStructure2Url": "",
            "referenceStructure2Format": "",
        }

    structure_format = get_structure_format_from_ext(reference_ext)

    if not structure_format:
        logger.warning("Unsupported reference Structure 2 extension: %s", reference_ext)
        return {
            "referenceStructure2Url": "",
            "referenceStructure2Format": "",
        }

    output_name = "reference_structure_2.cif" if structure_format == "cif" else "reference_structure_2.pdb"
    reference_url = save_file_to_media(reference_path, output_name, job_id)

    return {
        "referenceStructure2Url": reference_url,
        "referenceStructure2Format": structure_format,
    }


def save_original_structure1_to_media(
    structure1_path: Path,
    structure1_ext: str,
    job_id: str,
) -> Dict:
    """
    保存原始 Structure 1 到 MEDIA_ROOT。

    这个文件不是 3D 叠合显示必需的。

    它主要用于后续扩展下载功能，例如：
        - 下载原始 Structure 1
        - 下载原始 Structure 2
        - 下载叠合后的 Structure 1
        - 下载 US-align 原始输出
    """
    if not structure1_path.exists() or not structure1_path.is_file():
        logger.warning("Original Structure 1 file does not exist: %s", structure1_path)
        return {
            "originalStructure1Url": "",
            "originalStructure1Format": "",
        }

    structure_format = get_structure_format_from_ext(structure1_ext)

    if not structure_format:
        logger.warning("Unsupported original Structure 1 extension: %s", structure1_ext)
        return {
            "originalStructure1Url": "",
            "originalStructure1Format": "",
        }

    output_name = "original_structure_1.cif" if structure_format == "cif" else "original_structure_1.pdb"
    original_url = save_file_to_media(structure1_path, output_name, job_id)

    return {
        "originalStructure1Url": original_url,
        "originalStructure1Format": structure_format,
    }


def save_raw_output_to_media(raw_output: str, job_id: str) -> Dict:
    """
    保存 US-align 原始文本输出到 MEDIA_ROOT。

    这个文件不是必须的，但很适合做：
        Download raw output
        View raw output
    """
    output_dir = ensure_media_job_dir(job_id)
    output_path = output_dir / "usalign_raw_output.txt"

    output_path.write_text(raw_output, encoding="utf-8", errors="replace")

    return {
        "rawOutputUrl": build_media_url(job_id, "usalign_raw_output.txt")
    }


# ============================================================
# 7. 主函数：运行 US-align
# ============================================================

def run_usalign(structure_file_1, structure_file_2) -> Dict:
    """
    运行 US-align，并返回前端页面需要的完整结果。

    settings.py 中需要配置：

        Windows 示例：
            USALIGN_EXE = r"D:\\USalign\\USalign.exe"

        Linux 示例：
            USALIGN_EXE = "/home/jingyunhan/software/USalign/USalign"

        MEDIA_URL = "/media/"
        MEDIA_ROOT = BASE_DIR / "media"

    可选配置：
        STRUCTURE_UPLOAD_MAX_SIZE = 50 * 1024 * 1024
        USALIGN_TIMEOUT = 120
        USALIGN_ALIGNMENT_BLOCK_SIZE = 60
        USALIGN_CLEANUP_MAX_AGE_HOURS = 24
        USALIGN_CLEANUP_ON_RUN = True

    开发环境主 urls.py 需要加：

        from django.conf import settings
        from django.conf.urls.static import static

        if settings.DEBUG:
            urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    前端 3D 可视化应该加载：

        result["superposedStructure1Url"]
            叠合后的 Structure 1，通常显示为蓝色。

        result["referenceStructure2Url"]
            原始 Structure 2，通常显示为红色。

    重要含义：

        superposedStructure1Url：
            来源于 US-align 生成的 sup.cif / sup.pdb，
            后端复制到 media 后重命名为 superposed.cif / superposed.pdb。

        referenceStructure2Url：
            来源于用户上传的第二个结构文件。
            US-align 不会自动生成这个文件，所以后端要自己保存一份。
    """
    # 是否在每次运行前清理旧任务目录。
    # 开发阶段可以 True；正式部署可以改成 False，再用定时任务清理。
    cleanup_on_run = getattr(settings, "USALIGN_CLEANUP_ON_RUN", True)
    if cleanup_on_run:
        cleanup_old_structure_align_jobs(
            max_age_hours=getattr(settings, "USALIGN_CLEANUP_MAX_AGE_HOURS", 24)
        )

    # 获取 US-align 可执行文件路径。
    usalign_exe = getattr(settings, "USALIGN_EXE", "")

    if not usalign_exe:
        raise RuntimeError("USALIGN_EXE is not configured in settings.py.")

    if not os.path.exists(usalign_exe):
        raise RuntimeError(f"US-align executable was not found: {usalign_exe}")

    # 后端校验上传文件。
    ext1 = validate_structure_file(structure_file_1)
    ext2 = validate_structure_file(structure_file_2)

    # 使用临时目录运行 US-align。
    # TemporaryDirectory 会在 with 结束后自动删除临时文件。
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # 把上传文件保存到临时目录。
        #
        # 注意：这里不用用户原始文件名，而是改成 structure_1 / structure_2。
        # 原因：用户文件名可能包含空格、中文、特殊字符。
        # 使用固定文件名可以减少命令行兼容问题。
        input_path_1 = tmpdir_path / f"structure_1{ext1}"
        input_path_2 = tmpdir_path / f"structure_2{ext2}"

        save_uploaded_file(structure_file_1, input_path_1)
        save_uploaded_file(structure_file_2, input_path_2)

        output_prefix = USALIGN_OUTPUT_PREFIX

        # US-align 命令。
        #
        # -o sup 的作用：
        #   输出叠合后的 Structure 1 到 sup.*。
        #
        # 如果输入是 cif，通常生成 sup.cif。
        # 如果输入是 pdb，通常生成 sup.pdb。
        cmd = [
            usalign_exe,
            str(input_path_1),
            str(input_path_2),
            "-o",
            output_prefix,
        ]

        logger.info("Running US-align command: %s", " ".join(cmd))
        logger.info("US-align working directory: %s", tmpdir_path)

        try:
            completed = subprocess.run(
                cmd,
                cwd=str(tmpdir_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=getattr(settings, "USALIGN_TIMEOUT", 120),
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                "US-align timed out. Please try smaller structure files or increase USALIGN_TIMEOUT."
            ) from exc
        except OSError as exc:
            raise RuntimeError(
                f"Failed to execute US-align. Please check USALIGN_EXE: {usalign_exe}"
            ) from exc

        raw_stdout = completed.stdout or ""
        raw_stderr = completed.stderr or ""

        # US-align 的主要结果通常在 stdout。
        # 如果 stderr 有内容，也合并到 raw_output，方便调试。
        raw_output = raw_stdout
        if raw_stderr.strip():
            raw_output = raw_output + "\n\n[stderr]\n" + raw_stderr

        logger.info("US-align return code: %s", completed.returncode)
        logger.debug("US-align stdout:\n%s", raw_stdout)
        logger.debug("US-align stderr:\n%s", raw_stderr)

        # 记录 US-align 在临时目录中生成了哪些文件。
        # 调试时可以确认是否生成了 sup.cif / sup.pdb。
        generated_files = []
        for p in tmpdir_path.iterdir():
            if p.is_file():
                generated_files.append({"name": p.name, "size": p.stat().st_size})

        logger.info("US-align generated files: %s", generated_files)

        if completed.returncode != 0:
            # US-align 运行失败。
            #
            # 这里抛出 RuntimeError，建议在 Django view 里捕获，
            # 然后给前端返回更友好的 JSON 错误信息。
            raise RuntimeError(
                "US-align failed. Please check whether the uploaded files are valid PDB/mmCIF files.\n"
                f"Return code: {completed.returncode}\n"
                f"Output:\n{raw_output}"
            )

        # 解析统计指标。
        metrics = parse_usalign_metrics(raw_output)

        # 解析残基比对文本。
        alignment_data = parse_usalign_alignment(
            raw_output=raw_output,
            block_size=getattr(settings, "USALIGN_ALIGNMENT_BLOCK_SIZE", 60),
        )

        # 为本次任务创建唯一 job_id。
        # 所有 media 文件都会保存在：
        #   MEDIA_ROOT/structure_align/<job_id>/
        job_id = uuid.uuid4().hex

        # 保存原始 Structure 1。
        # 这不是 3D 叠合显示必需的，但适合以后做下载。
        original_structure_1 = save_original_structure1_to_media(
            structure1_path=input_path_1,
            structure1_ext=ext1,
            job_id=job_id,
        )

        # 保存叠合后的 Structure 1。
        #
        # US-align 原始输出：
        #   sup.cif / sup.pdb
        #
        # 后端保存后重命名：
        #   superposed.cif / superposed.pdb
        superposed_structure = save_superposed_structure_from_tmpdir(
            tmpdir_path=tmpdir_path,
            job_id=job_id,
            output_prefix=output_prefix,
        )

        # 保存原始 Structure 2，作为前端 3D 叠合显示中的参考结构。
        reference_structure_2 = save_reference_structure_to_media(
            reference_path=input_path_2,
            reference_ext=ext2,
            job_id=job_id,
        )

        # 保存 US-align 原始输出文本，方便下载或查看。
        raw_output_file = save_raw_output_to_media(raw_output, job_id)

        has_superposed_file = bool(superposed_structure.get("superposedStructureUrl"))

        # 生成前端展示用的提示文字。
        # interpretation = build_interpretation(metrics)
        status_message = build_status_message(metrics, has_superposed_file)

        # 返回给前端的完整结果。
        return {
            "success": True,

            # 当前任务 ID。可用于调试和下载文件定位。
            "jobId": job_id,

            # 用户上传时的原始文件名。
            "structureFile1Name": structure_file_1.name,
            "structureFile2Name": structure_file_2.name,

            # 从 US-align 输出中解析出的结构名称。
            "structure1Name": metrics.get("structure1Name", "-"),
            "structure2Name": metrics.get("structure2Name", "-"),

            # 核心统计指标。
            "structure1Length": metrics.get("structure1Length", "-"),
            "structure2Length": metrics.get("structure2Length", "-"),
            "alignedLength": metrics.get("alignedLength", "-"),
            "rmsd": metrics.get("rmsd", "-"),
            "seqId": metrics.get("seqId", "-"),
            "seqIdPercent": metrics.get("seqIdPercent", "-"),
            "tmScore1": metrics.get("tmScore1", "-"),
            "tmScore2": metrics.get("tmScore2", "-"),
            "coverage1": metrics.get("coverage1", "-"),
            "coverage2": metrics.get("coverage2", "-"),

            # 残基结构比对文本。
            "alignmentSeq1": alignment_data["alignmentSeq1"],
            "alignmentSeq2": alignment_data["alignmentSeq2"],
            "alignmentMatchLine": alignment_data["alignmentMatchLine"],
            "alignmentBlocks": alignment_data["alignmentBlocks"],
            "wholeAlignmentBlocks": alignment_data["wholeAlignmentBlocks"],

            # 原始 Structure 1。
            # 不是前端叠合显示必需字段，但可以用于下载。
            "originalStructure1Url": original_structure_1["originalStructure1Url"],
            "originalStructure1Format": original_structure_1["originalStructure1Format"],

            # 叠合后的 Structure 1。
            # 前端 3D 显示中建议作为蓝色模型加载。
            "superposedStructure1Url": superposed_structure["superposedStructureUrl"],
            "superposedStructureUrl": superposed_structure["superposedStructureUrl"],
            "superposedStructureFormat": superposed_structure["superposedStructureFormat"],
            "superposedStructureOriginalName": superposed_structure["superposedStructureOriginalName"],

            # 原始 Structure 2。
            # 前端 3D 显示中建议作为红色参考模型加载。
            "referenceStructure2Url": reference_structure_2["referenceStructure2Url"],
            "referenceStructure2Format": reference_structure_2["referenceStructure2Format"],

            # 兼容旧前端字段名。
            # 注意：这个 URL 可能指向 .cif 文件，不一定是 .pdb。
            # 保留它只是为了避免旧前端 disabled 判断失效。
            "superposedPdbUrl": superposed_structure["superposedStructureUrl"],

            # 前端提示文字。
            "statusMessage": status_message,
            # "interpretation": interpretation,

            # US-align 原始输出。
            "rawOutput": raw_output,
            "rawOutputUrl": raw_output_file["rawOutputUrl"],

            # 调试信息：US-align 实际生成的文件列表。
            # 正式上线后如果不想暴露这部分，可以删除。
            "generatedFiles": generated_files,
        }
