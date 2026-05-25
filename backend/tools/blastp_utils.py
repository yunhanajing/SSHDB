import os
import re
import tempfile
import subprocess
from pathlib import Path

from django.conf import settings


# ============================================================
# 1. 蛋白序列基础处理
# ============================================================

# 蛋白序列允许的字符
#
# 20 种标准氨基酸：
# A C D E F G H I K L M N P Q R S T V W Y
#
# 常见非标准 / 模糊氨基酸：
# B: Asx，可能是 D 或 N
# Z: Glx，可能是 E 或 Q
# J: Leucine 或 Isoleucine
# X: 任意未知氨基酸
# U: Selenocysteine
# O: Pyrrolysine
#
# *: 终止符。有些蛋白序列会带 *，是否允许取决于业务需求。
#
# 注意：
# 这里不允许 "-"。
# 因为 "-" 通常是比对后的 gap，不应该出现在用户输入的原始蛋白序列中。
AA_PATTERN = re.compile(r"^[ACDEFGHIKLMNPQRSTVWYBXZJUO*]+$", re.I)


def clean_sequence(seq):
    """
    清洗用户输入的蛋白序列。

    处理内容：
    1. 如果 seq 是 None，则转成空字符串
    2. 去掉所有空白字符，包括：
       - 换行符
       - 空格
       - tab
    3. 转成大写

    示例：
    输入：
        "meflit\\n lit"
    输出：
        "MEFLITLIT"
    """
    return re.sub(r"\s+", "", seq or "").upper()


def validate_protein_sequence(seq, name):
    """
    校验蛋白序列是否合法。

    参数：
        seq:
            清洗后的蛋白序列

        name:
            序列名称，用于报错提示，例如 "Sequence 1"

    抛出：
        ValueError:
            1. 序列为空
            2. 序列包含非法字符
    """
    if not seq:
        raise ValueError(f"{name} is required")

    if not AA_PATTERN.match(seq):
        raise ValueError(f"{name} contains invalid amino acid characters")


def write_fasta(path, seq_id, seq):
    """
    将一条蛋白序列写入 FASTA 文件。

    FASTA 格式示例：
        >Sequence_1
        MEFLITLITTFLLLLMPAITSSQYLGNNLLTNRKIFQKQE

    这里每 60 个字符换一行，是常见 FASTA 文件习惯。
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(f">{seq_id}\n")

        for i in range(0, len(seq), 60):
            f.write(seq[i:i + 60] + "\n")


# ============================================================
# 2. 比对结果展示辅助函数
# ============================================================

def build_match_line(seq1, seq2):
    """
    根据两条已经对齐的序列生成中间匹配线。

    规则：
        |  表示两个位置氨基酸完全相同
        .  表示两个位置都是氨基酸，但不相同
        空格 表示至少一方是 gap，也就是 "-"

    示例：
        seq1: MKTLLAIK
              ||| ||||
        seq2: MKT-LAIK
    """
    line = []

    for a, b in zip(seq1, seq2):
        if a == "-" or b == "-":
            line.append(" ")
        elif a == b:
            line.append("|")
        else:
            line.append(".")

    return "".join(line)


def parse_fasta_text(fasta_text):
    """
    解析 FASTA 格式文本。

    MAFFT 的输出默认是 FASTA 格式，例如：

        >Sequence_1
        MEFLITLITTF---
        >Sequence_2
        MEFLITLI-TAAA

    返回：
        {
            "Sequence_1": "MEFLITLITTF---",
            "Sequence_2": "MEFLITLI-TAAA"
        }
    """
    records = {}
    current_id = None
    current_seq = []

    for line in fasta_text.splitlines():
        line = line.strip()

        if not line:
            continue

        if line.startswith(">"):
            # 遇到新的 FASTA header 时，先保存上一条序列
            if current_id is not None:
                records[current_id] = "".join(current_seq)

            # 只取 header 的第一个字段作为 ID
            # 例如：">Sequence_1 some description"
            # 会取 "Sequence_1"
            current_id = line[1:].split()[0]
            current_seq = []
        else:
            current_seq.append(line)

    # 保存最后一条序列
    if current_id is not None:
        records[current_id] = "".join(current_seq)

    return records


# ============================================================
# 3. BLASTP 局部比对
# ============================================================

def build_empty_blastp_result(seq1, seq2):
    """
    构造 BLASTP 无结果时的统一返回结构。

    为什么需要这个函数？
    ----------------
    BLASTP 是局部相似性搜索工具，不是强制全局比对工具。

    即使我们把 e-value 阈值放宽，BLASTP 仍然可能不返回任何 HSP。
    这种情况不应该让整个接口失败。

    前端可以根据：
        hasHit == False

    显示：
        No local alignment found.

    但 MAFFT 的全局比对仍然可以继续展示。
    """
    return {
        "hasHit": False,
        "method": "BLASTP Local",
        "message": "No BLASTP local alignment found.",

        "queryId": "Sequence_1",
        "subjectId": "Sequence_2",

        "alignmentLength": 0,

        "identities": 0,
        "identityPercent": "0.00",

        "mismatches": 0,
        "mismatchPercent": "0.00",

        "gaps": 0,
        "gapPercent": "0.00",
        "gapOpen": 0,

        "rawScore": 0,
        "bitScore": 0,
        "evalue": "-",

        "queryLength": len(seq1),
        "subjectLength": len(seq2),

        "queryCoverage": "0.00",
        "subjectCoverage": "0.00",

        "queryStart": None,
        "queryEnd": None,
        "subjectStart": None,
        "subjectEnd": None,

        "alignedSeq1": "",
        "alignedSeq2": "",
        "matchLine": "",
    }


def run_blastp_alignment(sequence1, sequence2):
    """
    使用本地 blastp 对两条蛋白序列进行局部比对。

    作用定位：
    --------
    BLASTP 在这个页面中只负责：

        1. 局部比对统计值
        2. 最显著的一段局部 alignment 展示
        3. e-value、bit score、raw score 等 BLASTP 特有指标

    不负责：
        完整序列全局展示

    完整序列全局展示交给 MAFFT。

    重要说明：
    --------
    BLASTP 默认会按统计学显著性过滤结果。
    这里通过放宽参数，让 BLASTP 尽量返回弱匹配结果。

    但是：
    BLASTP 仍然不能保证每次都有结果。
    如果无结果，本函数返回 hasHit=False，而不是抛错。
    """

    # 1. 清洗序列
    seq1 = clean_sequence(sequence1)
    seq2 = clean_sequence(sequence2)

    # 2. 校验序列
    validate_protein_sequence(seq1, "Sequence 1")
    validate_protein_sequence(seq2, "Sequence 2")

    # 3. 从 Django settings.py 中读取 blastp.exe 路径
    blastp_exe = getattr(settings, "BLASTP_EXE", "")

    if not blastp_exe or not os.path.exists(blastp_exe):
        raise FileNotFoundError(f"blastp.exe not found: {blastp_exe}")

    # 4. 使用临时目录存放输入文件和输出结果
    #
    # TemporaryDirectory 会在 with 代码块结束后自动删除临时文件。
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        query_fasta = tmpdir_path / "query.fasta"
        subject_fasta = tmpdir_path / "subject.fasta"
        result_tsv = tmpdir_path / "result.tsv"

        # Sequence 1 作为 query
        write_fasta(query_fasta, "Sequence_1", seq1)

        # Sequence 2 作为 subject
        write_fasta(subject_fasta, "Sequence_2", seq2)

        # 5. BLASTP 输出格式
        #
        # outfmt 6 表示 tabular，也就是 TSV 表格。
        #
        # 字段说明：
        #
        # qseqid    query 序列 ID
        # sseqid    subject 序列 ID
        # pident    identity 百分比
        # length    比对长度
        # nident    完全相同的氨基酸数量
        # mismatch  不匹配数量
        # gapopen   gap 开启次数
        # gaps      gap 总数
        # qstart    query 比对起点
        # qend      query 比对终点
        # sstart    subject 比对起点
        # send      subject 比对终点
        # evalue    E-value
        # bitscore  Bit score
        # score     Raw score
        # qlen      query 总长度
        # slen      subject 总长度
        # qseq      query 对齐后的片段
        # sseq      subject 对齐后的片段
        outfmt = (
            "6 "
            "qseqid sseqid pident length nident mismatch gapopen gaps "
            "qstart qend sstart send evalue bitscore score qlen slen qseq sseq"
        )

        # 6. 构造 BLASTP 命令
        cmd = [
            blastp_exe,

            # 显式指定任务类型
            "-task", "blastp",

            # 输入 query 和 subject
            # 使用 -subject 时不需要 makeblastdb
            "-query", str(query_fasta),
            "-subject", str(subject_fasta),

            # 输出格式和输出文件
            "-outfmt", outfmt,
            "-out", str(result_tsv),

            # ------------------------------------------------
            # 下面这些参数用于“尽量返回弱匹配 / 不显著匹配”
            # ------------------------------------------------

            # 默认 e-value 阈值较严格。
            # 这里设置得很大，表示非常弱的局部匹配也允许输出。
            "-evalue", "1000000",

            # 蛋白 BLASTP 的 word size 通常可以设为 2。
            # word size 越小，越容易发现短的弱相似片段。
            "-word_size", "2",

            # 关闭低复杂度区域过滤。
            # 否则部分低复杂度蛋白序列可能被 BLASTP 屏蔽。
            "-seg", "no",

            # 关闭 composition-based statistics。
            # 这样可以减少因为组成校正导致的结果过滤影响。
            "-comp_based_stats", "0",

            # 每个 subject 最多保留 1 个 HSP。
            # 你的页面主要展示一段局部比对，所以保留最主要的一段即可。
            "-max_hsps", "1",

            # 只有一个 subject，这个参数影响不大。
            "-max_target_seqs", "1",
        ]

        # 7. 执行 BLASTP
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        # 如果 BLASTP 程序本身执行失败，例如路径错误、参数错误等，才抛异常。
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr or "blastp execution failed")

        # 8. BLASTP 没有返回任何 HSP
        #
        # 这不是程序错误。
        # 说明 BLASTP 没有找到可输出的局部比对。
        #
        # 前端应显示：
        # No local alignment found.
        #
        # 同时 MAFFT 结果仍然正常展示。
        if not result_tsv.exists() or result_tsv.stat().st_size == 0:
            return build_empty_blastp_result(seq1, seq2)

        # 9. 读取第一条 BLASTP 结果
        #
        # 因为设置了：
        # -max_hsps 1
        # -max_target_seqs 1
        #
        # 所以这里通常只有一行。
        first_line = result_tsv.read_text(encoding="utf-8").strip().splitlines()[0]
        fields = first_line.split("\t")

        if len(fields) < 19:
            raise RuntimeError(f"Unexpected blastp output format: {first_line}")

        (
            qseqid,
            sseqid,
            pident,
            length,
            nident,
            mismatch,
            gapopen,
            gaps,
            qstart,
            qend,
            sstart,
            send,
            evalue,
            bitscore,
            score,
            qlen,
            slen,
            qseq,
            sseq
        ) = fields[:19]

        # 10. 类型转换
        alignment_length = int(length)
        identities = int(nident)
        identity_percent = float(pident)

        mismatches = int(mismatch)
        gap_open = int(gapopen)
        gap_count = int(gaps)

        bit_score = float(bitscore)
        raw_score = int(score)

        query_length = int(qlen)
        subject_length = int(slen)

        # 11. 计算 mismatch 和 gap 百分比
        mismatch_percent = (
            mismatches / alignment_length * 100
            if alignment_length
            else 0
        )

        gap_percent = (
            gap_count / alignment_length * 100
            if alignment_length
            else 0
        )

        # 12. 计算 query / subject coverage
        #
        # 注意：
        # 这里是基于 BLASTP 局部比对长度计算的覆盖率。
        # 它不等于全局比对覆盖率。
        query_coverage = (
            alignment_length / query_length * 100
            if query_length
            else 0
        )

        subject_coverage = (
            alignment_length / subject_length * 100
            if subject_length
            else 0
        )

        # 13. 生成中间匹配线
        match_line = build_match_line(qseq, sseq)

        # 14. 返回 BLASTP 局部比对结果
        return {
            "hasHit": True,
            "method": "BLASTP Local",
            "message": "BLASTP local alignment found.",

            "queryId": qseqid,
            "subjectId": sseqid,

            "alignmentLength": alignment_length,

            "identities": identities,
            "identityPercent": f"{identity_percent:.2f}",

            "mismatches": mismatches,
            "mismatchPercent": f"{mismatch_percent:.2f}",

            "gaps": gap_count,
            "gapPercent": f"{gap_percent:.2f}",
            "gapOpen": gap_open,

            "rawScore": raw_score,
            "bitScore": bit_score,
            "evalue": evalue,

            "queryLength": query_length,
            "subjectLength": subject_length,

            "queryCoverage": f"{query_coverage:.2f}",
            "subjectCoverage": f"{subject_coverage:.2f}",

            "queryStart": int(qstart),
            "queryEnd": int(qend),
            "subjectStart": int(sstart),
            "subjectEnd": int(send),

            "alignedSeq1": qseq,
            "alignedSeq2": sseq,
            "matchLine": match_line,
        }


# ============================================================
# 4. MAFFT 全局比对
# ============================================================
def run_mafft_global_alignment(sequence1, sequence2):
    """
    使用 MAFFT 对两条蛋白序列做全局比对展示。

    作用定位：
    --------
    MAFFT 在这个页面中只负责：

        1. 展示两条完整蛋白序列的全局 alignment
        2. 让用户看到完整序列中 gap 的位置
        3. 作为主要的序列展示结果

    不再负责：
        - alignmentLength
        - identities
        - identityPercent
        - mismatches
        - mismatchPercent
        - gaps
        - gapPercent

    这些统计值不再为 MAFFT 计算。
    页面中的统计值只保留 BLASTP Statistics。
    """

    # 1. 清洗序列
    seq1 = clean_sequence(sequence1)
    seq2 = clean_sequence(sequence2)

    # 2. 校验序列
    validate_protein_sequence(seq1, "Sequence 1")
    validate_protein_sequence(seq2, "Sequence 2")

    # 3. 从 Django settings.py 中读取 MAFFT 路径
    mafft_exe = getattr(settings, "MAFFT_EXE", "")

    if not mafft_exe or not os.path.exists(mafft_exe):
        raise FileNotFoundError(f"MAFFT executable not found: {mafft_exe}")

    # 4. 创建临时 FASTA 输入文件
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        input_fasta = tmpdir_path / "input.fasta"

        with open(input_fasta, "w", encoding="utf-8") as f:
            f.write(">Sequence_1\n")
            for i in range(0, len(seq1), 60):
                f.write(seq1[i:i + 60] + "\n")

            f.write(">Sequence_2\n")
            for i in range(0, len(seq2), 60):
                f.write(seq2[i:i + 60] + "\n")

        # 5. 构造 MAFFT 命令
        cmd = [
            mafft_exe,
            "--auto",
            str(input_fasta),
        ]

        # 6. 执行 MAFFT
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        if completed.returncode != 0:
            raise RuntimeError(completed.stderr or "MAFFT execution failed")

        mafft_output = completed.stdout

        # 7. 解析 MAFFT 输出的 FASTA 文本
        records = parse_fasta_text(mafft_output)

        aligned_seq1 = records.get("Sequence_1", "")
        aligned_seq2 = records.get("Sequence_2", "")

        if not aligned_seq1 or not aligned_seq2:
            raise RuntimeError(f"Unexpected MAFFT output:\n{mafft_output}")

        # 8. 生成中间匹配线
        match_line = build_match_line(aligned_seq1, aligned_seq2)

        # 9. 返回 MAFFT 全局比对结果
        #
        # 这里只返回前端展示 alignment 所需要的数据。
        # 不返回 MAFFT Statistics。
        return {
            "method": "MAFFT Global Alignment",
            "message": "MAFFT global alignment generated.",

            "queryId": "Sequence_1",
            "subjectId": "Sequence_2",

            "queryLength": len(seq1),
            "subjectLength": len(seq2),

            "alignedSeq1": aligned_seq1,
            "alignedSeq2": aligned_seq2,
            "matchLine": match_line,

            "rawFasta": mafft_output,
        }


# ============================================================
# 5. 组合接口：BLASTP + MAFFT
# ============================================================

def run_combined_protein_alignment(sequence1, sequence2):
    """
    同时运行 BLASTP 和 MAFFT。

    页面设计：
    --------
    1. BLASTP Statistics
       用于展示局部比对统计值。
       如果 BLASTP 没有返回结果，就显示：
           No local alignment found.

    2. MAFFT Global Alignment
       用于展示两条完整蛋白序列的全局比对。
       这是主要的完整序列展示模块。

    返回结构：
    --------
    {
        "blastp": {
            ...
        },
        "mafft": {
            ...
        }
    }

    注意：
    ----
    BLASTP 没有结果时，不应该影响 MAFFT。
    所以 run_blastp_alignment 内部已经把“无结果”处理成 hasHit=False。
    """

    blastp_result = run_blastp_alignment(sequence1, sequence2)
    mafft_result = run_mafft_global_alignment(sequence1, sequence2)

    return {
        "blastp": blastp_result,
        "mafft": mafft_result,
    }