<template>
  <div class="sequence-align-page">
    <div class="page-container">
      <!-- Input Panel -->
      <div class="panel-card input-panel">
        <div class="panel-tag">Sequence Alignment</div>

        <div class="input-inner">
          <div class="sequence-input-grid">
            <!-- Sequence 1 -->
            <div class="sequence-input-block">
              <div class="input-title-row">
                <div class="input-title">
                  <span class="required-star">*</span>
                  Sequence 1
                </div>

                <div class="input-actions">
                  <el-button
                    size="small"
                    type="success"
                    plain
                    @click="fillExampleSequence('seq1')"
                  >
                    <el-icon style="margin-right: 8px;">
                      <DocumentCopy />
                    </el-icon>
                    Example
                  </el-button>

                  <el-button
                    size="small"
                    plain
                    type="danger"
                    @click="clearSequence('seq1')"
                  >
                    <el-icon style="margin-right: 8px;">
                      <Delete />
                    </el-icon>
                    Clear
                  </el-button>
                </div>
              </div>

              <el-input
                v-model="sequence1"
                type="textarea"
                :rows="8"
                resize="none"
                placeholder="Please input the first protein sequence in FASTA format..."
                class="sequence-textarea"
                @input="alignmentResult = null"
              />

              <div class="sequence-meta">
                ID: {{ sequenceName1 }} &nbsp;&nbsp; Length: {{ cleanSequence1.length }} aa
              </div>
            </div>

            <!-- Buttons -->
            <div class="compare-center">
              <el-button
                class="swap-button"
                type="primary"
                plain
                size="large"
                :icon="Switch"
                @click="swapSequences"
              />

              <el-button
                type="primary"
                plain
                size="large"
                :loading="alignLoading"
                :disabled="!canAlign"
                @click="handleAlign"
              >
                Align
              </el-button>
            </div>

            <!-- Sequence 2 -->
            <div class="sequence-input-block">
              <div class="input-title-row">
                <div class="input-title">
                  <span class="required-star">*</span>
                  Sequence 2
                </div>

                <div class="input-actions">
                  <el-button
                    size="small"
                    type="success"
                    plain
                    @click="fillExampleSequence('seq2')"
                  >
                    <el-icon style="margin-right: 8px;">
                      <DocumentCopy />
                    </el-icon>
                    Example
                  </el-button>

                  <el-button
                    size="small"
                    plain
                    type="danger"
                    @click="clearSequence('seq2')"
                  >
                    <el-icon style="margin-right: 8px;">
                      <Delete />
                    </el-icon>
                    Clear
                  </el-button>
                </div>
              </div>

              <el-input
                v-model="sequence2"
                type="textarea"
                :rows="8"
                resize="none"
                placeholder="Please input the second protein sequence in FASTA format..."
                class="sequence-textarea"
                @input="alignmentResult = null"
              />

              <div class="sequence-meta">
                ID: {{ sequenceName2 }} &nbsp;&nbsp; Length: {{ cleanSequence2.length }} aa
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- BLASTP Statistics -->
      <div
        v-if="blastpResult"
        class="panel-card summary-panel"
      >
        <div class="panel-tag">BLASTP Statistics</div>

        <div class="summary-inner">
          <div
            v-if="blastpResult.hasHit"
            class="summary-table"
          >
            <div class="summary-cell">
              <div class="summary-label">Alignment Length</div>
              <div class="summary-value">
                {{ blastpResult.alignmentLength }}
              </div>
            </div>

            <div class="summary-cell">
              <div class="summary-label">Identities</div>
              <div class="summary-value identity-text">
                {{ blastpResult.identities }}
                <span>({{ blastpResult.identityPercent }}%)</span>
              </div>
            </div>

            <div class="summary-cell">
              <div class="summary-label">Mismatches</div>
              <div class="summary-value mismatch-text">
                {{ blastpResult.mismatches }}
                <span>({{ blastpResult.mismatchPercent }}%)</span>
              </div>
            </div>

            <div class="summary-cell">
              <div class="summary-label">Gaps</div>
              <div class="summary-value gap-text">
                {{ blastpResult.gaps }}
                <span>({{ blastpResult.gapPercent }}%)</span>
              </div>
            </div>

            <div class="summary-cell">
              <div class="summary-label">E-value</div>
              <div class="summary-value">
                {{ blastpResult.evalue }}
              </div>
            </div>

            <div class="summary-cell">
              <div class="summary-label">Bit Score</div>
              <div class="summary-value">
                {{ blastpResult.bitScore }}
              </div>
            </div>
          </div>

          <div
            v-else
            class="no-hit-box"
          >
            No local alignment found.
          </div>
        </div>
      </div>

      <!-- BLASTP Local Alignment -->
      <div
        v-if="blastpResult"
        class="panel-card result-panel"
      >
        <div class="panel-tag">BLASTP Local Alignment</div>

        <div class="download-area">
          <el-button
            plain
            type="primary"
            :disabled="!blastpResult.hasHit"
            @click="downloadAlignment('blastp')"
          >
            <el-icon style="margin-right: 8px;">
              <Download />
            </el-icon>
            Download BLASTP
          </el-button>
        </div>

        <div class="result-inner">
          <div
            v-if="blastpResult.hasHit"
            class="alignment-view"
          >
            <div
              v-for="(block, blockIndex) in blastpAlignmentBlocks"
              :key="`blastp-${blockIndex}`"
              class="alignment-block"
            >
              <div class="position-row">
                <div class="row-name"></div>
                <div class="row-start"></div>

                <div
                  class="position-track"
                  :style="{ width: `${block.trackWidth}px` }"
                >
                  <span
                    v-for="mark in block.marks"
                    :key="`blastp-mark-${blockIndex}-${mark.index}`"
                    class="position-mark"
                    :style="{ left: mark.left }"
                  >
                    {{ mark.position }}
                  </span>
                </div>

                <div class="row-end"></div>
              </div>

              <div class="alignment-row">
                <div class="row-name">
                  {{ sequenceName1 }}
                </div>

                <div class="row-start">
                  {{ block.seq1Start }}
                </div>

                <div
                  class="sequence-track"
                  :style="{ gridTemplateColumns: `repeat(${block.length}, ${CELL_WIDTH}px)` }"
                >
                  <span
                    v-for="(item, index) in block.seq1"
                    :key="`blastp-seq1-${blockIndex}-${index}`"
                    class="char-cell"
                    :class="item.type"
                  >
                    {{ item.char }}
                  </span>
                </div>

                <div class="row-end">
                  {{ block.seq1End }}
                </div>
              </div>

              <div class="alignment-row">
                <div class="row-name">
                  {{ sequenceName2 }}
                </div>

                <div class="row-start">
                  {{ block.seq2Start }}
                </div>

                <div
                  class="sequence-track"
                  :style="{ gridTemplateColumns: `repeat(${block.length}, ${CELL_WIDTH}px)` }"
                >
                  <span
                    v-for="(item, index) in block.seq2"
                    :key="`blastp-seq2-${blockIndex}-${index}`"
                    class="char-cell"
                    :class="item.type"
                  >
                    {{ item.char }}
                  </span>
                </div>

                <div class="row-end">
                  {{ block.seq2End }}
                </div>
              </div>

              <div class="alignment-row consensus-row">
                <div class="row-name">
                  Consensus
                </div>

                <div class="row-start"></div>

                <div
                  class="sequence-track"
                  :style="{ gridTemplateColumns: `repeat(${block.length}, ${CELL_WIDTH}px)` }"
                >
                  <span
                    v-for="(char, index) in block.consensus"
                    :key="`blastp-consensus-${blockIndex}-${index}`"
                    class="consensus-cell"
                  >
                    {{ char }}
                  </span>
                </div>

                <div class="row-end"></div>
              </div>
            </div>

            <div class="legend-row">
              <div class="legend-item">
                <span class="legend-box identical"></span>
                Identical
              </div>

              <div class="legend-item">
                <span class="legend-box mismatch"></span>
                Mismatch
              </div>

              <div class="legend-item">
                <span class="legend-box gap"></span>
                Gap
              </div>

              <div class="legend-item">
                <span class="legend-symbol">*</span>
                Identical
              </div>

              <div class="legend-item">
                <span class="legend-symbol">.</span>
                Mismatch
              </div>
            </div>
          </div>

          <div
            v-else
            class="no-hit-box"
          >
            BLASTP did not return a local alignment. Please check the MAFFT global alignment below.
          </div>
        </div>
      </div>

      <!-- MAFFT Global Alignment -->
      <div
        v-if="mafftResult"
        class="panel-card result-panel"
      >
        <div class="panel-tag">MAFFT Global Alignment</div>

        <div class="download-area">
          <el-button
            plain
            type="primary"
            @click="downloadAlignment('mafft')"
          >
            <el-icon style="margin-right: 8px;">
              <Download />
            </el-icon>
            Download MAFFT
          </el-button>
        </div>

        <div class="result-inner">
          <div class="alignment-view">
            <div
              v-for="(block, blockIndex) in mafftAlignmentBlocks"
              :key="`mafft-${blockIndex}`"
              class="alignment-block"
            >
              <div class="position-row">
                <div class="row-name"></div>
                <div class="row-start"></div>

                <div
                  class="position-track"
                  :style="{ width: `${block.trackWidth}px` }"
                >
                  <span
                    v-for="mark in block.marks"
                    :key="`mafft-mark-${blockIndex}-${mark.index}`"
                    class="position-mark"
                    :style="{ left: mark.left }"
                  >
                    {{ mark.position }}
                  </span>
                </div>

                <div class="row-end"></div>
              </div>

              <div class="alignment-row">
                <div class="row-name">
                  {{ sequenceName1 }}
                </div>

                <div class="row-start">
                  {{ block.seq1Start }}
                </div>

                <div
                  class="sequence-track"
                  :style="{ gridTemplateColumns: `repeat(${block.length}, ${CELL_WIDTH}px)` }"
                >
                  <span
                    v-for="(item, index) in block.seq1"
                    :key="`mafft-seq1-${blockIndex}-${index}`"
                    class="char-cell"
                    :class="item.type"
                  >
                    {{ item.char }}
                  </span>
                </div>

                <div class="row-end">
                  {{ block.seq1End }}
                </div>
              </div>

              <div class="alignment-row">
                <div class="row-name">
                  {{ sequenceName2 }}
                </div>

                <div class="row-start">
                  {{ block.seq2Start }}
                </div>

                <div
                  class="sequence-track"
                  :style="{ gridTemplateColumns: `repeat(${block.length}, ${CELL_WIDTH}px)` }"
                >
                  <span
                    v-for="(item, index) in block.seq2"
                    :key="`mafft-seq2-${blockIndex}-${index}`"
                    class="char-cell"
                    :class="item.type"
                  >
                    {{ item.char }}
                  </span>
                </div>

                <div class="row-end">
                  {{ block.seq2End }}
                </div>
              </div>

              <div class="alignment-row consensus-row">
                <div class="row-name">
                  Consensus
                </div>

                <div class="row-start"></div>

                <div
                  class="sequence-track"
                  :style="{ gridTemplateColumns: `repeat(${block.length}, ${CELL_WIDTH}px)` }"
                >
                  <span
                    v-for="(char, index) in block.consensus"
                    :key="`mafft-consensus-${blockIndex}-${index}`"
                    class="consensus-cell"
                  >
                    {{ char }}
                  </span>
                </div>

                <div class="row-end"></div>
              </div>
            </div>

            <div class="legend-row">
              <div class="legend-item">
                <span class="legend-box identical"></span>
                Identical
              </div>

              <div class="legend-item">
                <span class="legend-box mismatch"></span>
                Mismatch
              </div>

              <div class="legend-item">
                <span class="legend-box gap"></span>
                Gap
              </div>

              <div class="legend-item">
                <span class="legend-symbol">*</span>
                Identical
              </div>

              <div class="legend-item">
                <span class="legend-symbol">.</span>
                Mismatch
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Delete,
  DocumentCopy,
  Download,
  Switch
} from '@element-plus/icons-vue'

import request from '@/utils/request'

const sequence1 = ref('')
const sequence2 = ref('')
const alignLoading = ref(false)

const alignmentResult = ref(null)

const BLOCK_SIZE = 100

/**
 * 每个氨基酸字符格子的宽度。
 * 注意：
 * CSS 里的 .sequence-track gap 是 2px。
 * 所以真实轨道宽度 = block.length * CELL_WIDTH + (block.length - 1) * CELL_GAP
 */
const CELL_WIDTH = 10
const CELL_GAP = 2

const exampleSequence1 = `>Glyma.18G244300
MAASRSTFPLMKYLRVRVDALPRNTPLTLAPNFLIRRFCEEVRGCFLDKSEVTDRVISCVKNFQKVDPSKVNPNAHFQNDLGLDSLDSVEIVMALEEEFGFEIPDNEADKINSIKLAVDFIASHPQAK*`

const exampleSequence2 = `>Medtr6g084940
MYNGAQISDINGPPTGKWTTGLFGCCEEPGNCCFTFCCPRFTFGRNVEIIDQGRTSATQARLIFCLLGCAGLQSVYSYRFRSGLRTLFNLPEEPCIDFCVHYCCTICAICQEYRELKNRGLDPSKGWKANEGKMKTIQVPPQVAMGMTR`

const parseFastaInput = (value, defaultName) => {
  const text = String(value || '').trim()

  if (!text) {
    return {
      name: defaultName,
      sequence: ''
    }
  }

  const lines = text
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(Boolean)

  let name = defaultName
  const sequenceLines = []

  lines.forEach(line => {
    if (line.startsWith('>')) {
      const header = line.replace(/^>/, '').trim()

      if (header) {
        name = header.split(/\s+/)[0]
      }
    } else {
      sequenceLines.push(line)
    }
  })

  const sequence = sequenceLines
    .join('')
    .replace(/\s+/g, '')
    .replace(/[^A-Za-z*]/g, '')
    .toUpperCase()

  return {
    name,
    sequence
  }
}

const parsedSequence1 = computed(() => {
  return parseFastaInput(sequence1.value, 'Sequence_1')
})

const parsedSequence2 = computed(() => {
  return parseFastaInput(sequence2.value, 'Sequence_2')
})

const sequenceName1 = computed(() => parsedSequence1.value.name)
const sequenceName2 = computed(() => parsedSequence2.value.name)

const cleanSequence1 = computed(() => parsedSequence1.value.sequence)
const cleanSequence2 = computed(() => parsedSequence2.value.sequence)

const canAlign = computed(() => {
  return cleanSequence1.value.length > 0 && cleanSequence2.value.length > 0
})

const blastpResult = computed(() => {
  return alignmentResult.value?.blastp || null
})

const mafftResult = computed(() => {
  return alignmentResult.value?.mafft || null
})

const fillExampleSequence = type => {
  if (type === 'seq1') {
    sequence1.value = exampleSequence1
  }

  if (type === 'seq2') {
    sequence2.value = exampleSequence2
  }

  alignmentResult.value = null
}

const clearSequence = type => {
  if (type === 'seq1') {
    sequence1.value = ''
  }

  if (type === 'seq2') {
    sequence2.value = ''
  }

  alignmentResult.value = null
}

const swapSequences = () => {
  const temp = sequence1.value

  sequence1.value = sequence2.value
  sequence2.value = temp

  alignmentResult.value = null
}

const getPairType = (a, b) => {
  if (a === '-' || b === '-') return 'gap'
  if (a === b) return 'identical'
  return 'mismatch'
}

const getConsensusChar = (a, b) => {
  if (a === '-' || b === '-') return ' '
  if (a === b) return '*'
  return '.'
}

const normalizeBlastpResult = result => {
  return {
    hasHit: Boolean(result?.hasHit),
    method: result?.method || 'BLASTP Local',
    message: result?.message || '',

    alignmentLength: result?.alignmentLength || 0,

    identities: result?.identities || 0,
    identityPercent: result?.identityPercent || '0.00',

    mismatches: result?.mismatches || 0,
    mismatchPercent: result?.mismatchPercent || '0.00',

    gaps: result?.gaps || 0,
    gapPercent: result?.gapPercent || '0.00',
    gapOpen: result?.gapOpen || 0,

    rawScore: result?.rawScore || result?.score || 0,
    bitScore: result?.bitScore || 0,
    score: result?.rawScore || result?.score || result?.bitScore || 0,
    evalue: result?.evalue || '-',

    alignedSeq1: result?.alignedSeq1 || '',
    alignedSeq2: result?.alignedSeq2 || '',
    matchLine: result?.matchLine || '',

    queryStart: result?.queryStart || 1,
    queryEnd: result?.queryEnd || 0,
    subjectStart: result?.subjectStart || 1,
    subjectEnd: result?.subjectEnd || 0,

    queryLength: result?.queryLength || cleanSequence1.value.length,
    subjectLength: result?.subjectLength || cleanSequence2.value.length,

    queryCoverage: result?.queryCoverage || '0.00',
    subjectCoverage: result?.subjectCoverage || '0.00'
  }
}

const normalizeMafftResult = result => {
  return {
    method: result?.method || 'MAFFT Global Alignment',
    message: result?.message || '',

    alignmentLength: result?.alignmentLength || 0,

    identities: result?.identities || 0,
    identityPercent: result?.identityPercent || '0.00',

    mismatches: result?.mismatches || 0,
    mismatchPercent: result?.mismatchPercent || '0.00',

    gaps: result?.gaps || 0,
    gapPercent: result?.gapPercent || '0.00',

    alignedSeq1: result?.alignedSeq1 || '',
    alignedSeq2: result?.alignedSeq2 || '',
    matchLine: result?.matchLine || '',

    queryStart: result?.queryStart || 1,
    subjectStart: result?.subjectStart || 1,

    queryLength: result?.queryLength || cleanSequence1.value.length,
    subjectLength: result?.subjectLength || cleanSequence2.value.length,

    rawFasta: result?.rawFasta || ''
  }
}

const handleAlign = async () => {
  if (!canAlign.value) {
    ElMessage.warning('Please input two sequences')
    return
  }

  try {
    alignLoading.value = true
    alignmentResult.value = null

    const res = await request.post(
      '/tools/sequence/align/',
      {
        sequence1: cleanSequence1.value,
        sequence2: cleanSequence2.value,
        sequenceName1: sequenceName1.value,
        sequenceName2: sequenceName2.value
      }
    )

    const result = res.data?.data || res.data

    if (!result) {
      ElMessage.error('Invalid alignment response')
      return
    }

    if (!result.blastp || !result.mafft) {
      ElMessage.error('Invalid alignment response: missing blastp or mafft result')
      return
    }

    alignmentResult.value = {
      blastp: normalizeBlastpResult(result.blastp),
      mafft: normalizeMafftResult(result.mafft)
    }

    if (!alignmentResult.value.blastp.hasHit) {
      ElMessage.warning('BLASTP local alignment was not found, but MAFFT global alignment was generated')
    } else {
      ElMessage.success('Alignment completed')
    }
  } catch (error) {
    alignmentResult.value = null

    console.error('alignment failed:', error)

    ElMessage.error(
      error?.response?.data?.error ||
      error?.response?.data?.message ||
      error?.response?.data?.detail ||
      'Alignment failed'
    )
  } finally {
    alignLoading.value = false
  }
}

/**
 * 计算某个字符格子中心点的横向位置。
 *
 * 例如：
 * 第 1 个字符中心点 = CELL_WIDTH / 2
 * 第 5 个字符中心点 = 4 * (CELL_WIDTH + CELL_GAP) + CELL_WIDTH / 2
 *
 * 这样顶部刻度会准确落在对应字符的上方，
 * 不会因为 block 只有 5 个字符就跑到整行最右侧。
 */
const getCellCenterLeft = positionInBlock => {
  return `${(positionInBlock - 1) * (CELL_WIDTH + CELL_GAP) + CELL_WIDTH / 2}px`
}

/**
 * 构建可视化 block。
 *
 * 顶部 marks：
 *   显示 alignment column position。
 *
 * 左侧 start / 右侧 end：
 *   显示两条序列在原始序列中的真实位置。
 *
 * 关键修改：
 *   1. 每个 block 增加 length。
 *   2. 每个 block 增加 trackWidth。
 *   3. marks 的 left 使用 px，而不是百分比。
 *   4. sequence-track 的列数由 block.length 决定，不再固定 100 列。
 */
const buildAlignmentBlocks = result => {
  if (!result) return []

  const seq1 = result.alignedSeq1 || ''
  const seq2 = result.alignedSeq2 || ''

  if (!seq1 || !seq2) return []

  const blocks = []

  let seq1RealPosition = (result.queryStart || 1) - 1
  let seq2RealPosition = (result.subjectStart || 1) - 1

  for (let start = 0; start < seq1.length; start += BLOCK_SIZE) {
    const end = Math.min(start + BLOCK_SIZE, seq1.length)

    const seq1Part = seq1.slice(start, end)
    const seq2Part = seq2.slice(start, end)

    const blockLength = seq1Part.length
    const trackWidth = blockLength * CELL_WIDTH + Math.max(blockLength - 1, 0) * CELL_GAP

    const seq1Items = []
    const seq2Items = []
    const consensus = []

    let seq1BlockStart = null
    let seq2BlockStart = null

    let seq1BlockEnd = seq1RealPosition
    let seq2BlockEnd = seq2RealPosition

    for (let index = 0; index < blockLength; index += 1) {
      const char1 = seq1Part[index]
      const char2 = seq2Part[index]
      const type = getPairType(char1, char2)

      if (char1 !== '-') {
        seq1RealPosition += 1

        if (seq1BlockStart === null) {
          seq1BlockStart = seq1RealPosition
        }

        seq1BlockEnd = seq1RealPosition
      }

      if (char2 !== '-') {
        seq2RealPosition += 1

        if (seq2BlockStart === null) {
          seq2BlockStart = seq2RealPosition
        }

        seq2BlockEnd = seq2RealPosition
      }

      seq1Items.push({
        char: char1,
        type
      })

      seq2Items.push({
        char: char2,
        type
      })

      consensus.push(getConsensusChar(char1, char2))
    }

      const markPositions = []

      for (let marker = 10; marker < blockLength; marker += 10) {
        markPositions.push({
          index: marker,
          position: start + marker,
          left: getCellCenterLeft(marker),
          isEndMark: false
        })
      }

      /**
       * 只有最后一个 block 不足 10 个字符时，才额外显示终点刻度。
       * 例如最后只剩 5 个字符时显示 5。
       * 如果刚好是 100 个字符，就不额外显示 100，避免和右侧 end position 冲突。
       */
      if (blockLength < 10) {
        markPositions.push({
          index: blockLength,
          position: end,
          left: getCellCenterLeft(blockLength),
          isEndMark: true
        })
      }

    blocks.push({
      seq1: seq1Items,
      seq2: seq2Items,
      consensus,

      seq1Start: seq1BlockStart || '',
      seq2Start: seq2BlockStart || '',

      seq1End: seq1BlockEnd || '',
      seq2End: seq2BlockEnd || '',

      marks: markPositions,

      length: blockLength,
      trackWidth
    })
  }

  return blocks
}

const blastpAlignmentBlocks = computed(() => {
  if (!blastpResult.value || !blastpResult.value.hasHit) return []

  return buildAlignmentBlocks(blastpResult.value)
})

const mafftAlignmentBlocks = computed(() => {
  if (!mafftResult.value) return []

  return buildAlignmentBlocks(mafftResult.value)
})

const buildDownloadText = type => {
  let result = null
  let title = ''

  if (type === 'blastp') {
    result = blastpResult.value
    title = 'BLASTP Local Alignment'
  }

  if (type === 'mafft') {
    result = mafftResult.value
    title = 'MAFFT Global Alignment'
  }

  if (!result) return ''

  if (type === 'blastp' && !result.hasHit) {
    return [
      title,
      '',
      'No local alignment found.'
    ].join('\n')
  }

  return [
    title,
    '',
    `${sequenceName1.value}:`,
    result.alignedSeq1 || '',
    '',
    'Consensus:',
    result.matchLine || '',
    '',
    `${sequenceName2.value}:`,
    result.alignedSeq2 || ''
  ].join('\n')
}

const downloadAlignment = type => {
  const content = buildDownloadText(type)

  if (!content) {
    ElMessage.warning('No alignment result to download')
    return
  }

  const blob = new Blob([content], {
    type: 'text/plain;charset=utf-8'
  })

  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url

  if (type === 'blastp') {
    link.download = 'blastp_local_alignment_result.txt'
  } else if (type === 'mafft') {
    link.download = 'mafft_global_alignment_result.txt'
  } else {
    link.download = 'sequence_alignment_result.txt'
  }

  link.click()

  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.sequence-align-page {
  width: 100%;
  min-height: 100vh;
  padding: 24px;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
  background: #f5faff;
}

.required-star {
  color: #f56c6c;
  margin-right: 4px;
  font-weight: 700;
}

.page-container {
  width: 100%;
  max-width: 1600px;
}

.panel-card {
  position: relative;
  width: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  background: #ffffff;
  box-sizing: border-box;
}

.panel-tag {
  position: absolute;
  top: 16px;
  left: -10px;
  background: #b2e6f5;
  color: #ffffff;
  font-size: 18px;
  line-height: 1;
  padding: 12px 22px;
  border-radius: 0 4px 4px 0;
  font-weight: 600;
  z-index: 2;
}

.panel-tag::before {
  content: "";
  position: absolute;
  left: 0;
  bottom: -10px;
  width: 0;
  height: 0;
  border-top: 10px solid #a1d0dd;
  border-left: 10px solid transparent;
}

.input-panel {
  margin-top: 28px;
  padding: 64px 28px 28px;
}

.input-inner {
  width: 100%;
}

.sequence-input-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 120px minmax(0, 1fr);
  gap: 30px;
  align-items: center;
}

.sequence-input-block {
  min-width: 0;
}

.input-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.input-title {
  color: #303133;
  font-size: 15px;
  font-weight: bold;
  margin-top: 10px;
}

.input-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sequence-textarea :deep(.el-textarea__inner) {
  font-family: Consolas, Monaco, "Courier New", monospace;
  font-size: 15px;
  line-height: 1.8;
  color: #303133;
  border-radius: 6px;
}

.sequence-meta {
  margin-top: 10px;
  color: #606266;
  font-size: 12px;
}

.compare-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 22px;
}

.summary-panel {
  margin-top: 24px;
  padding: 60px 28px 28px;
}

.summary-inner {
  width: 100%;
  margin-top: 15px;
}

.summary-table {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  overflow: hidden;
}

.summary-cell {
  min-height: 86px;
  padding: 16px 12px;
  border-right: 1px solid #e4e7ed;
  background: #fbfdff;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.summary-cell:last-child {
  border-right: none;
}

.summary-label {
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.summary-value {
  color: #303133;
  font-size: 18px;
  font-weight: 700;
}

.identity-text {
  color: #21a121;
}

.mismatch-text {
  color: #e66a50;
}

.gap-text {
  color: #7b55c7;
}

.result-panel {
  margin-top: 24px;
  padding: 64px 28px 28px;
}

.download-area {
  position: absolute;
  top: 30px;
  right: 28px;
}

.result-inner {
  width: 100%;
  overflow-x: auto;
  margin-top: 15px;
}

.alignment-view {
  min-width: 0;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 28px 24px 18px;
  box-sizing: border-box;
  background: #ffffff;
}

.alignment-block {
  margin-bottom: 34px;
}

.alignment-block:last-child {
  margin-bottom: 18px;
}

/**
 * 关键修改：
 * 原来是 3 列：名字+start / sequence / end
 * 现在是 4 列：名字 / start / sequence / end
 *
 * 这样两个序列的 start 数字不再跟着名字长度移动，
 * 会稳定在同一列，因此自然处于同一水平位置。
 */
.position-row,
.alignment-row {
  display: grid;
  grid-template-columns: 170px 48px auto 58px;
  align-items: center;
  gap: 8px;
}

.position-row {
  height: 26px;
  color: #606266;
  font-size: 12px;
}

.position-track {
  position: relative;
  height: 26px;
}

.position-mark {
  position: absolute;
  top: 0;
  transform: translateX(-50%);
}

.row-name {
  color: #303133;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.row-start {
  color: #606266;
  font-size: 13px;
  text-align: right;
}

.row-end {
  color: #303133;
  font-size: 14px;
  text-align: right;
}

/**
 * 关键修改：
 * 不再写 grid-template-columns: repeat(100, minmax(10px, 1fr));
 * 因为最后一个 block 可能只有 5 个字符。
 *
 * 现在列数由模板中的 block.length 动态控制：
 * :style="{ gridTemplateColumns: `repeat(${block.length}, ${CELL_WIDTH}px)` }"
 */
.sequence-track {
  display: grid;
  gap: 2px;
  width: max-content;
}

.char-cell,
.consensus-cell {
  height: 22px;
  min-width: 10px;
  border-radius: 2px;
  font-family: Consolas, Monaco, "Courier New", monospace;
  font-size: 13px;
  line-height: 22px;
  text-align: center;
  box-sizing: border-box;
}

.char-cell.identical {
  background: #c9efc0;
  color: #303133;
}

.char-cell.mismatch {
  background: #f8b8b2;
  color: #303133;
}

.char-cell.gap {
  background: #d9d9d9;
  color: #303133;
}

.consensus-row {
  margin-top: 4px;
}

.consensus-cell {
  background: transparent;
  color: #303133;
}

.legend-row {
  display: flex;
  align-items: center;
  gap: 26px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
  color: #606266;
  font-size: 14px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-box {
  width: 16px;
  height: 16px;
  border-radius: 2px;
  display: inline-block;
  flex-shrink: 0;
}

.legend-box.identical {
  background: #c9efc0;
}

.legend-box.mismatch {
  background: #f8b8b2;
}

.legend-box.gap {
  background: #d9d9d9;
}

.legend-symbol {
  width: 16px;
  text-align: center;
  color: #303133;
  font-family: Consolas, Monaco, "Courier New", monospace;
  font-weight: 700;
  display: inline-block;
}

.no-hit-box {
  width: 100%;
  padding: 28px;
  border: 1px dashed #dcdfe6;
  border-radius: 6px;
  background: #fbfdff;
  color: #606266;
  font-size: 15px;
  line-height: 1.8;
  box-sizing: border-box;
}

@media (max-width: 1200px) {
  .sequence-input-grid {
    grid-template-columns: 1fr;
  }

  .compare-center {
    flex-direction: row;
    justify-content: center;
  }

  .summary-table {
    grid-template-columns: repeat(2, 1fr);
  }

  .summary-cell:nth-child(2n) {
    border-right: none;
  }
}

@media (max-width: 768px) {
  .sequence-align-page {
    padding: 16px;
  }

  .input-panel,
  .summary-panel,
  .result-panel {
    padding-left: 16px;
    padding-right: 16px;
  }

  .panel-tag {
    font-size: 16px;
    padding: 10px 18px;
  }

  .summary-table {
    grid-template-columns: 1fr;
  }

  .summary-cell {
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
  }

  .summary-cell:last-child {
    border-bottom: none;
  }

  .input-title-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .download-area {
    position: static;
    display: flex;
    justify-content: flex-end;
    margin-bottom: 16px;
  }

  .position-row,
  .alignment-row {
    grid-template-columns: 150px 48px auto 58px;
  }
}
</style>
