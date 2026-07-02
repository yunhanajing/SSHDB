<template>
  <div class="structure-align-page">
    <div class="page-container">
      <!-- =====================================================
           1. 上传文件区域
           - 上传两个结构文件
           - 支持 .pdb / .cif / .mmcif
           - Example 按钮分别加载示例文件
           - Clear 按钮分别清除单个文件
      ====================================================== -->
      <div class="panel-card input-panel">
        <div class="panel-tag">Structure Alignment</div>

        <p class="section-desc">
          Compare two protein structures and visualize the superposition result.
        </p>

        <div class="input-inner">
          <div class="structure-input-grid">
            <!-- ================= Structure File 1 ================= -->
            <div class="upload-block">
              <div class="input-title-row">
                <div class="input-title">
                  <span class="required-star">*</span>
                  Structure File 1
                </div>

                <div class="input-actions">
                  <el-button
                    size="small"
                    type="success"
                    plain
                    @click="loadExampleFile(1)"
                  >
                    <el-icon style="margin-right: 8px;">
                      <DocumentCopy />
                    </el-icon>
                    Example
                  </el-button>

                  <el-button
                    size="small"
                    type="danger"
                    plain
                    @click="removeFile(1)"
                  >
                    <el-icon style="margin-right: 8px;">
                      <Delete />
                    </el-icon>
                    Clear
                  </el-button>
                </div>
              </div>

              <label
                class="drop-zone"
                @dragover.prevent
                @drop.prevent="handleDrop($event, 1)"
              >
                <input
                  ref="fileInput1"
                  type="file"
                  accept=".pdb,.cif,.mmcif"
                  hidden
                  @change="handleFileChange($event, 1)"
                />

                <el-icon class="upload-filled-icon">
                  <UploadFilled />
                </el-icon>

                <div class="upload-main-text">
                  Drag &amp; drop a file here, or click to browse
                </div>

                <div class="upload-sub-text">
                  Supported formats: .pdb, .cif, .mmCIF
                </div>
              </label>

              <div
                v-if="structureFile1"
                class="uploaded-file-row"
              >
                <div class="uploaded-file-left">
                  <span class="uploaded-file-icon">
                    <el-icon>
                      <DocumentChecked />
                    </el-icon>
                  </span>

                  <div class="uploaded-file-info">
                    <div class="uploaded-file-name">
                      {{ structureFile1.name }}
                    </div>

                    <div class="uploaded-file-size">
                      {{ formatFileSize(structureFile1.size) }}
                    </div>
                  </div>
                </div>

                <div class="uploaded-file-actions">
                  <button
                    type="button"
                    class="uploaded-remove-btn"
                    title="Remove file"
                    @click.stop="removeFile(1)"
                  >
                    ×
                  </button>
                </div>
              </div>
            </div>

            <!-- ================= Middle Buttons ================= -->
            <div class="compare-center">
              <el-button
                class="swap-button"
                type="primary"
                plain
                size="large"
                :icon="Switch"
                @click="swapFiles"
              />

              <el-button
                type="primary"
                plain
                size="large"
                :loading="alignLoading"
                :disabled="!canAlign"
                @click="runAlignment"
              >
                Align
              </el-button>
            </div>

            <!-- ================= Structure File 2 ================= -->
            <div class="upload-block">
              <div class="input-title-row">
                <div class="input-title">
                  <span class="required-star">*</span>
                  Structure File 2
                </div>

                <div class="input-actions">
                  <el-button
                    size="small"
                    type="success"
                    plain
                    @click="loadExampleFile(2)"
                  >
                    <el-icon style="margin-right: 8px;">
                      <DocumentCopy />
                    </el-icon>
                    Example
                  </el-button>

                  <el-button
                    size="small"
                    type="danger"
                    plain
                    @click="removeFile(2)"
                  >
                    <el-icon style="margin-right: 8px;">
                      <Delete />
                    </el-icon>
                    Clear
                  </el-button>
                </div>
              </div>

              <label
                class="drop-zone"
                @dragover.prevent
                @drop.prevent="handleDrop($event, 2)"
              >
                <input
                  ref="fileInput2"
                  type="file"
                  accept=".pdb,.cif,.mmcif"
                  hidden
                  @change="handleFileChange($event, 2)"
                />

                <el-icon class="upload-filled-icon">
                  <UploadFilled />
                </el-icon>

                <div class="upload-main-text">
                  Drag &amp; drop a file here, or click to browse
                </div>

                <div class="upload-sub-text">
                  Supported formats: .pdb, .cif, .mmCIF
                </div>
              </label>

              <div
                v-if="structureFile2"
                class="uploaded-file-row"
              >
                <div class="uploaded-file-left">
                  <span class="uploaded-file-icon">
                    <el-icon>
                      <DocumentChecked />
                    </el-icon>
                  </span>

                  <div class="uploaded-file-info">
                    <div class="uploaded-file-name">
                      {{ structureFile2.name }}
                    </div>

                    <div class="uploaded-file-size">
                      {{ formatFileSize(structureFile2.size) }}
                    </div>
                  </div>
                </div>

                <div class="uploaded-file-actions">
                  <button
                    type="button"
                    class="uploaded-remove-btn"
                    title="Remove file"
                    @click.stop="removeFile(2)"
                  >
                    ×
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- =====================================================
           2. 统计值区域
      ====================================================== -->
      <div
        v-if="showStatistics"
        class="panel-card summary-panel"
      >
        <div class="panel-tag">US-align Statistics</div>

        <div class="summary-inner">
          <div class="summary-table structure-summary-table">
            <div class="summary-cell">
              <div class="summary-label">
                TM-score
                <span class="summary-sub blue-text">(Structure 1)</span>
              </div>
              <div class="summary-value">
                {{ formatMetric(result.tmScore1) }}
              </div>
            </div>

            <div class="summary-cell">
              <div class="summary-label">
                TM-score
                <span class="summary-sub red-text">(Structure 2)</span>
              </div>
              <div class="summary-value">
                {{ formatMetric(result.tmScore2) }}
              </div>
            </div>

            <div class="summary-cell">
              <div class="summary-label">RMSD</div>
              <div class="summary-value rmsd-value">
                {{ formatMetric(result.rmsd) }} Å
              </div>
            </div>

            <div class="summary-cell">
              <div class="summary-label">Aligned Length</div>
              <div class="summary-value aligned-value">
                {{ formatMetric(result.alignedLength) }}
              </div>
            </div>

            <!-- <div class="summary-cell">
              <div class="summary-label">Seq_ID</div>
              <div class="summary-value seqid-value">
                {{ formatMetric(result.seqId) }}
              </div>
            </div> -->

            <div class="summary-cell">
              <div class="summary-label">Structure 1 Length</div>
              <div class="summary-value">
                {{ formatMetric(result.structure1Length) }}
              </div>
            </div>

            <div class="summary-cell">
              <div class="summary-label">Structure 2 Length</div>
              <div class="summary-value">
                {{ formatMetric(result.structure2Length) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- =====================================================
           3. 结果区域
           - 左侧使用 3Dmol.js 显示结构叠合结果
           - 右侧显示结构残基比对文本
      ====================================================== -->
      <div
        v-if="showResult"
        class="panel-card result-panel"
      >
        <div class="panel-tag">Structure Alignment Results</div>

        <div class="download-area">
          <el-button
            plain
            type="primary"
            @click="downloadReport"
          >
            <el-icon class="btn-icon">
              <Download />
            </el-icon>
            Download Report
          </el-button>

          <el-button
            plain
            type="primary"
            @click="exportPdb"
          >
            <el-icon class="btn-icon">
              <Download />
            </el-icon>
            Export Structure
          </el-button>

          <el-button
            plain
            type="primary"
            @click="viewRawOutput"
          >
            <el-icon class="btn-icon">
              <Search />
            </el-icon>
            View Raw Output
          </el-button>
        </div>

        <div class="result-inner">
          <div class="structure-result-grid">
            <!-- ================= 3Dmol Superposition ================= -->
            <div class="viewer-card">
              <div class="card-title">3Dmol 3D Superposition</div>

              <div class="viewer-tools">

                <button
                  type="button"
                  title="Reload structure"
                  @click="renderSuperposition"
                >
                  ⟳
                </button>

                <button
                  type="button"
                  title="Zoom in"
                  @click="zoomInViewer"
                >
                  +
                </button>

                <button
                  type="button"
                  title="Zoom out"
                  @click="zoomOutViewer"
                >
                  -
                </button>
              </div>

              <div class="model-viewer-wrapper">
                <div
                  ref="molViewer"
                  class="model-viewer"
                >
                  <div
                    v-if="!result.superposedStructure1Url && !result.superposedStructureUrl && !result.superposedPdbUrl"
                    class="viewer-empty-text"
                  >
                    No superposed structure file was returned by backend.
                  </div>
                </div>
              </div>

              <div class="viewer-legend">
                <span class="legend-item">
                  <i class="legend-color blue-bg"></i>
                  Structure 1 / Superposed model
                </span>

                <span class="legend-item">
                  <i class="legend-color red-bg"></i>
                  Structure 2 / Reference model
                </span>
              </div>
            </div>

            <!-- ================= Alignment Text ================= -->
            <div class="alignment-card">
              <div class="card-title">Alignment Text</div>

              <div class="alignment-tabs">
                <button
                  :class="{ active: activeTab === 'aligned' }"
                  @click="activeTab = 'aligned'"
                >
                  Aligned Region
                </button>

                <button
                  :class="{ active: activeTab === 'text' }"
                  @click="activeTab = 'text'"
                >
                  Raw Output
                </button>
              </div>

              <div class="alignment-box">
                <template v-if="activeTab === 'aligned'">
                  <div
                    v-if="currentAlignmentBlocks.length"
                    class="alignment-block-list"
                  >
                    <div
                      v-for="(block, index) in currentAlignmentBlocks"
                      :key="`aligned-${index}`"
                      class="alignment-block"
                    >
                     <div class="visual-scale-row">
                      <span class="visual-label"></span>
                      <span class="visual-start"></span>
                      <span
                        class="visual-seq-line visual-scale-line"
                        v-html="renderScaleLine(block.seq1.length, block.columnStart)"
                      ></span>
                      <span class="visual-end"></span>
                    </div>

                    <div class="visual-align-row">
                      <span class="visual-label">{{ structure1DisplayName }}</span>
                      <span class="visual-start">{{ block.struc1Start }}</span>
                      <span
                        class="visual-seq-line"
                        v-html="renderStructureSequence(block.seq1, block.matchLine)"
                      ></span>
                      <span class="visual-end">{{ block.struc1End }}</span>
                    </div>

                    <div class="visual-align-row match-row">
                      <span class="visual-label"></span>
                      <span class="visual-start"></span>
                      <span
                        class="visual-seq-line visual-match-line"
                        v-html="renderOriginalMatchLine(block.matchLine)"
                      ></span>
                      <span class="visual-end"></span>
                    </div>

                    <div class="visual-align-row">
                      <span class="visual-label">{{ structure2DisplayName }}</span>
                      <span class="visual-start">{{ block.struc2Start }}</span>
                      <span
                        class="visual-seq-line"
                        v-html="renderStructureSequence(block.seq2, block.matchLine)"
                      ></span>
                      <span class="visual-end">{{ block.struc2End }}</span>
                    </div>
                    </div>
                  </div>

                  <div
                    v-else
                    class="empty-alignment-text"
                  >
                    No aligned residue block was parsed from US-align output.
                  </div>
                </template>

                <pre v-else>{{ rawOutputPreview }}</pre>
              </div>

              <div class="alignment-legend visual-legend">
                <span>
                  <i class="legend-box legend-close"></i>
                  : Distance &lt; 5 Å
                </span>

                <span>
                  <i class="legend-box legend-weak"></i>
                  . Other aligned residue
                </span>

                <span>
                  <i class="legend-box legend-gap"></i>
                  Gap
                </span>
              </div>
<!-- 
              <div class="interpretation-box">
                <span class="info-big"><el-icon><Warning /></el-icon></span>

              <div class="interpretation-text">
                <strong>Interpretation:</strong>
                {{ result.interpretation || fallbackInterpretation }}
              </div>
              </div> -->
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import {
  UploadFilled,
  DocumentCopy,
  Delete,
  Switch,
  DocumentChecked,
  Download,
  Search,
  Warning
} from '@element-plus/icons-vue'

import request from '@/utils/request'

/*
 * 3Dmol.js
 *
 * 安装：
 *   npm install 3dmol
 *
 * 注意：
 * 这里已经完全移除 Mol*。
 * 不再使用：
 *   import { Viewer } from 'molstar/build/viewer/molstar'
 *   import 'molstar/build/viewer/molstar.css'
 */
import * as $3Dmol from '3dmol'

export default {
  name: 'StructureAlignment',

  components: {
    UploadFilled,
    DocumentCopy,
    Delete,
    DocumentChecked,
    Download,
    Search,
    Warning
  },

  data() {
    return {
      structureFile1: null,
      structureFile2: null,

      alignLoading: false,

      showStatistics: false,
      showResult: false,

      activeTab: 'aligned',

      allowedExtensions: ['pdb', 'cif', 'mmcif'],

      exampleFile1Url: '/cif/gmacp__glyma.18g244300_model.cif',
      exampleFile2Url: '/cif/gmacp__lj1g3v2840250_model.cif',

      result: null,

      rawOutputPreview: '',

      /*
       * 3Dmol viewer 实例。
       */
      modelViewer: null,

      Switch
    }
  },

  computed: {
    canAlign() {
      return Boolean(this.structureFile1 && this.structureFile2)
    },

   currentAlignmentBlocks() {
    const blocks = this.result?.alignmentBlocks || []

    const mergedBlock = this.mergeAlignmentBlocks(blocks)

    if (!mergedBlock) return []

    /*
    * 这里改 80 / 100 才会真正生效。
    */
    return this.splitAlignmentBlock(mergedBlock,40)
  },
    /*
     * Alignment Text 左侧 Structure 1 的显示名称。
     * 优先级：
     * 1. 后端返回的 structure1Name
     * 2. 后端返回的 structureFile1Name
     * 3. 前端上传文件名
     * 4. 默认 Structure 1
     */
    structure1DisplayName() {
      return this.getDisplayStructureName(
        this.structureFile1?.name ||
        this.result?.structureFile1Name ||
        this.result?.structure1Name ||
        'Structure 1'
      )
    },

    structure2DisplayName() {
      return this.getDisplayStructureName(
        this.structureFile2?.name ||
        this.result?.structureFile2Name ||
        this.result?.structure2Name ||
        'Structure 2'
      )
    },

    // fallbackInterpretation() {
    //   return 'The structural alignment was completed. Please evaluate TM-score, RMSD, aligned length, and coverage together.'
    // }
  },

  created() {
    this.result = this.getEmptyResult()
  },

  beforeUnmount() {
    this.clearViewer()
  },

  methods: {
    getEmptyResult() {
      return {
        success: false,

        structureFile1Name: '',
        structureFile2Name: '',
        structure1Name: '',
        structure2Name: '',

        tmScore1: '-',
        tmScore2: '-',
        rmsd: '-',
        alignedLength: '-',
        seqId: '-',
        seqIdPercent: '-',

        structure1Length: '-',
        structure2Length: '-',
        coverage1: '-',
        coverage2: '-',

        alignmentSeq1: '',
        alignmentSeq2: '',
        alignmentMatchLine: '',
        alignmentBlocks: [],

        originalStructure1Url: '',
        originalStructure1Format: '',

        superposedStructure1Url: '',
        superposedStructureUrl: '',
        superposedStructureFormat: 'cif',

        referenceStructure2Url: '',
        referenceStructure2Format: 'cif',

        superposedPdbUrl: '',

        interpretation: '',
        rawOutput: ''
      }
    },
    mergeAlignmentBlocks(blocks) {
      if (!blocks || !blocks.length) return null

      const firstBlock = blocks[0]

      return {
        ...firstBlock,

        /*
        * 把后端已经分开的多个 alignment block 重新拼成一个完整 alignment。
        */
        seq1: blocks.map(block => block.seq1 || '').join(''),
        seq2: blocks.map(block => block.seq2 || '').join(''),
        matchLine: blocks.map(block => block.matchLine || '').join(''),

        /*
        * 起始坐标使用第一个 block 的起点。
        * 后续 end 坐标会在 splitAlignmentBlock() 里重新计算。
        */
        struc1Start: firstBlock.struc1Start || 1,
        struc2Start: firstBlock.struc2Start || 1
      }
    },
    /*
     * 将文件名或路径转换成页面显示名称。
     *
     * 例如：
     * /path/to/1crn.pdb  -> 1crn
     * C:\data\1ubq.cif   -> 1ubq
     * proteinA.mmcif     -> proteinA
     */
    getDisplayStructureName(name) {
      if (!name) return '-'

      const fileName = String(name)
        .split('/')
        .pop()
        .split('\\')
        .pop()

      return fileName.replace(/\.(pdb|cif|mmcif)$/i, '')
    },

    splitAlignmentBlock(block, columnsPerLine = 50) {
    if (!block) return []

    const seq1 = block.seq1 || ''
    const seq2 = block.seq2 || ''
    const matchLine = block.matchLine || ''

    const maxLength = Math.max(seq1.length, seq2.length, matchLine.length)
    const result = []

    let currentStruc1Pos = Number(block.struc1Start) || 1
    let currentStruc2Pos = Number(block.struc2Start) || 1

    for (let start = 0; start < maxLength; start += columnsPerLine) {
      const end = start + columnsPerLine

      const seq1Chunk = seq1.slice(start, end)
      const seq2Chunk = seq2.slice(start, end)
      const matchChunk = matchLine.slice(start, end)

      const seq1ResidueCount = seq1Chunk.replace(/-/g, '').length
      const seq2ResidueCount = seq2Chunk.replace(/-/g, '').length

      const struc1Start = seq1ResidueCount > 0 ? currentStruc1Pos : ''
      const struc2Start = seq2ResidueCount > 0 ? currentStruc2Pos : ''

      const struc1End =
        seq1ResidueCount > 0
          ? currentStruc1Pos + seq1ResidueCount - 1
          : ''

      const struc2End =
        seq2ResidueCount > 0
          ? currentStruc2Pos + seq2ResidueCount - 1
          : ''

      result.push({
        ...block,
        seq1: seq1Chunk,
        seq2: seq2Chunk,
        matchLine: matchChunk,

        struc1Start,
        struc1End,
        struc2Start,
        struc2End,

        columnStart: start + 1,
        columnEnd: Math.min(end, maxLength)
      })

      currentStruc1Pos += seq1ResidueCount
      currentStruc2Pos += seq2ResidueCount
    }

    return result
  },

    getFileExtension(fileName) {
      if (!fileName || !fileName.includes('.')) return ''

      return fileName
        .split('.')
        .pop()
        .toLowerCase()
    },

    isAllowedStructureFile(file) {
      if (!file || !file.name) return false

      const extension = this.getFileExtension(file.name)

      return this.allowedExtensions.includes(extension)
    },

    validateStructureFile(file) {
      if (!file) return false

      if (!this.isAllowedStructureFile(file)) {
        this.$message.error(
          'Invalid file format. Please upload .pdb, .cif, or .mmcif files only.'
        )

        return false
      }

      return true
    },

    /*
     * 3Dmol 支持的格式名称。
     *
     * 对于 .cif / .mmcif，使用 cif。
     * 对于 .pdb，使用 pdb。
     */
    get3DmolFormat(formatOrUrl) {
      if (!formatOrUrl) return 'cif'

      const value = String(formatOrUrl).toLowerCase()

      if (value.includes('pdb') || value.endsWith('.pdb')) {
        return 'pdb'
      }

      if (
        value.includes('cif') ||
        value.includes('mmcif') ||
        value.endsWith('.cif') ||
        value.endsWith('.mmcif')
      ) {
        return 'cif'
      }

      return 'cif'
    },

    setStructureFile(file, index) {
      if (!this.validateStructureFile(file)) return

      if (index === 1) {
        this.structureFile1 = file

        if (this.$refs.fileInput1) {
          this.$refs.fileInput1.value = ''
        }
      } else {
        this.structureFile2 = file

        if (this.$refs.fileInput2) {
          this.$refs.fileInput2.value = ''
        }
      }

      this.resetResultState()
    },

    handleFileChange(event, index) {
      const file = event.target.files && event.target.files[0]

      if (!file) return

      this.setStructureFile(file, index)
    },

    handleDrop(event, index) {
      const file = event.dataTransfer.files && event.dataTransfer.files[0]

      if (!file) return

      this.setStructureFile(file, index)
    },

    async loadExampleFile(index) {
      try {
        const url = index === 1 ? this.exampleFile1Url : this.exampleFile2Url

        const response = await fetch(url)

        if (!response.ok) {
          throw new Error(`Failed to load example file: ${url}`)
        }

        const blob = await response.blob()
        const fileName = decodeURIComponent(url.split('/').pop())

        const file = new File([blob], fileName, {
          type: blob.type || 'chemical/x-cif'
        })

        this.setStructureFile(file, index)
      } catch (error) {
        console.error(error)
        this.$message.error('Failed to load example file.')
      }
    },

    removeFile(index) {
      if (index === 1) {
        this.structureFile1 = null

        if (this.$refs.fileInput1) {
          this.$refs.fileInput1.value = ''
        }
      } else {
        this.structureFile2 = null

        if (this.$refs.fileInput2) {
          this.$refs.fileInput2.value = ''
        }
      }

      this.resetResultState()
    },

    swapFiles() {
      const temp = this.structureFile1

      this.structureFile1 = this.structureFile2
      this.structureFile2 = temp

      this.resetResultState()
    },

    clearAll() {
      this.structureFile1 = null
      this.structureFile2 = null

      if (this.$refs.fileInput1) {
        this.$refs.fileInput1.value = ''
      }

      if (this.$refs.fileInput2) {
        this.$refs.fileInput2.value = ''
      }

      this.resetResultState()
    },

    resetResultState() {
      this.showStatistics = false
      this.showResult = false
      this.result = this.getEmptyResult()
      this.rawOutputPreview = ''
      this.clearViewer()
    },

    async runAlignment() {
      if (!this.structureFile1 || !this.structureFile2) {
        this.$message.warning('Please upload both structure files.')
        return
      }

      if (
        !this.validateStructureFile(this.structureFile1) ||
        !this.validateStructureFile(this.structureFile2)
      ) {
        return
      }

      try {
        this.alignLoading = true
        this.showStatistics = false
        this.showResult = false
        this.clearViewer()

        const formData = new FormData()

        formData.append('file1', this.structureFile1)
        formData.append('file2', this.structureFile2)

        const res = await request.post(
          '/tools/structure/align/',
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          }
        )

        const data = res.data?.data || res.data

        if (data.success === false) {
          throw new Error(data.message || 'Structure alignment failed.')
        }

        this.result = {
          ...this.getEmptyResult(),

          success: data.success ?? true,

          structureFile1Name: data.structureFile1Name || '',
          structureFile2Name: data.structureFile2Name || '',
          structure1Name: data.structure1Name || '',
          structure2Name: data.structure2Name || '',

          tmScore1: data.tmScore1 ?? '-',
          tmScore2: data.tmScore2 ?? '-',
          rmsd: data.rmsd ?? '-',
          alignedLength: data.alignedLength ?? '-',
          seqId: data.seqId ?? '-',
          seqIdPercent: data.seqIdPercent ?? '-',

          structure1Length: data.structure1Length ?? '-',
          structure2Length: data.structure2Length ?? '-',
          coverage1: data.coverage1 ?? '-',
          coverage2: data.coverage2 ?? '-',

          alignmentSeq1: data.alignmentSeq1 || '',
          alignmentSeq2: data.alignmentSeq2 || '',
          alignmentMatchLine: data.alignmentMatchLine || '',
          alignmentBlocks: data.alignmentBlocks || [],

          originalStructure1Url: data.originalStructure1Url || '',
          originalStructure1Format: data.originalStructure1Format || '',

          superposedStructure1Url:
            data.superposedStructure1Url ||
            data.superposedStructureUrl ||
            data.superposedPdbUrl ||
            '',

          superposedStructureUrl:
            data.superposedStructureUrl ||
            data.superposedStructure1Url ||
            data.superposedPdbUrl ||
            '',

          superposedStructureFormat:
            data.superposedStructureFormat ||
            data.superposedStructure1Format ||
            'cif',

          referenceStructure2Url: data.referenceStructure2Url || '',
          referenceStructure2Format:
            data.referenceStructure2Format ||
            data.structure2Format ||
            data.superposedStructureFormat ||
            'cif',

          superposedPdbUrl:
            data.superposedPdbUrl ||
            data.superposedStructure1Url ||
            data.superposedStructureUrl ||
            '',

          interpretation: data.interpretation || '',
          rawOutput: data.rawOutput || ''
        }

        this.rawOutputPreview = this.result.rawOutput

        this.showStatistics = true
        this.showResult = true

        this.$nextTick(() => {
          this.renderSuperposition()
        })

        this.$message.success('Structure alignment completed.')
      } catch (error) {
        console.error(error)

        this.$message.error(
          error?.response?.data?.error ||
          error?.response?.data?.message ||
          error?.response?.data?.detail ||
          error?.message ||
          'Structure alignment failed.'
        )
      } finally {
        this.alignLoading = false
      }
    },

    getFullMediaUrl(url) {
      if (!url) return ''

      if (url.startsWith('http://') || url.startsWith('https://')) {
        return url
      }

      const normalizedUrl = url.startsWith('/') ? url : `/${url}`

      return normalizedUrl
    },

    /*
     * 使用 3Dmol.js 加载结构叠合结果。
     *
     * 推荐后端返回：
     *   superposedStructure1Url：US-align 输出的已叠合 Structure 1
     *   referenceStructure2Url：参考结构 Structure 2
     *
     * 如果后端只返回 superposedStructure1Url，也能显示一个模型。
     */
    async renderSuperposition() {
      const structure1Url =
        this.result?.superposedStructure1Url ||
        this.result?.superposedStructureUrl ||
        this.result?.superposedPdbUrl

      const structure2Url = this.result?.referenceStructure2Url

      if (!structure1Url) {
        console.warn('No superposed Structure 1 URL returned by backend.')
        return
      }

      if (!this.$refs.molViewer) {
        console.warn('3Dmol viewer DOM is not ready.')
        return
      }

      try {
        this.clearViewer()

        const viewerElement = this.$refs.molViewer

        this.modelViewer = $3Dmol.createViewer(viewerElement, {
          backgroundColor: '#ffffff'
        })

        const fullStructure1Url = this.getFullMediaUrl(structure1Url)

        const format1 = this.get3DmolFormat(
          this.result.superposedStructureFormat || fullStructure1Url
        )

        const response1 = await fetch(fullStructure1Url)

        if (!response1.ok) {
          throw new Error(`Failed to fetch Structure 1: ${fullStructure1Url}`)
        }

        const structureText1 = await response1.text()

        const model1 = this.modelViewer.addModel(structureText1, format1)

        model1.setStyle({}, {
          cartoon: {
            color: 'blue'
          }
        })

        if (structure2Url) {
          const fullStructure2Url = this.getFullMediaUrl(structure2Url)

          const format2 = this.get3DmolFormat(
            this.result.referenceStructure2Format || fullStructure2Url
          )

          const response2 = await fetch(fullStructure2Url)

          if (!response2.ok) {
            throw new Error(`Failed to fetch Structure 2: ${fullStructure2Url}`)
          }

          const structureText2 = await response2.text()

          const model2 = this.modelViewer.addModel(structureText2, format2)

          model2.setStyle({}, {
            cartoon: {
              color: 'red'
            }
          })
        }

        /*
         * 设置默认视角。
         * zoomTo()：自动居中并让结构完整进入视野。
         * zoom(1.15)：在自动视角基础上稍微放大一点。
         */
        this.modelViewer.zoomTo()
        this.modelViewer.zoom(1.15)
        this.modelViewer.render()
      } catch (error) {
        console.error('3Dmol render error:', error)
        this.$message.warning('3Dmol viewer could not load the result file.')
      }
    },

    clearViewer() {
      if (this.modelViewer) {
        try {
          this.modelViewer.clear()
          this.modelViewer.removeAllModels()
          this.modelViewer.render()
        } catch (error) {
          console.warn('Failed to clear 3Dmol viewer:', error)
        }
      }

      this.modelViewer = null

      if (this.$refs.molViewer) {
        this.$refs.molViewer.innerHTML = ''
      }
    },

    resetViewer() {
      if (!this.modelViewer) return

      try {
        this.modelViewer.zoomTo()
        this.modelViewer.zoom(1.15)
        this.modelViewer.render()
      } catch (error) {
        console.warn('Failed to reset 3Dmol camera:', error)
      }
    },

    zoomToViewer() {
      this.resetViewer()
    },

    zoomInViewer() {
      if (!this.modelViewer) return

      try {
        this.modelViewer.zoom(1.2)
        this.modelViewer.render()
      } catch (error) {
        console.warn('Failed to zoom in 3Dmol viewer:', error)
      }
    },

    zoomOutViewer() {
      if (!this.modelViewer) return

      try {
        this.modelViewer.zoom(0.8)
        this.modelViewer.render()
      } catch (error) {
        console.warn('Failed to zoom out 3Dmol viewer:', error)
      }
    },

    escapeHtml(value) {
      if (value === null || value === undefined) return ''

      return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;')
    },
    renderScaleLine(length, columnStart = 1) {
      if (!length) return ''

      return Array.from({ length }, (_, index) => {
        const columnNumber = Number(columnStart || 1) + index

        if (columnNumber % 10 === 0) {
          return `
            <span class="scale-cell">
              <span class="scale-number">${columnNumber}</span>
            </span>
          `
        }

        return '<span class="scale-cell">&nbsp;</span>'
      }).join('')
    },
    renderStructureSequence(seq, matchLine) {
      if (!seq) return ''

      return seq
        .split('')
        .map((char, index) => {
          const safeChar = char === ' ' ? '&nbsp;' : this.escapeHtml(char)
          const mark = matchLine?.[index]

          if (char === '-') {
            return `<span class="aa-cell aa-gap">-</span>`
          }

          /*
          * ':' = residue pairs with d < 5.0 Å
          * 用绿色背景
          */
          if (mark === ':') {
            return `<span class="aa-cell aa-close">${safeChar}</span>`
          }

          /*
          * '.' = other aligned residues
          * 用粉红色背景
          */
          if (mark === '.') {
            return `<span class="aa-cell aa-weak">${safeChar}</span>`
          }

          /*
          * 没有 ':' 或 '.' 的非 gap 残基
          */
          return `<span class="aa-cell aa-neutral">${safeChar}</span>`
        })
        .join('')
    },

    renderOriginalMatchLine(matchLine) {
      if (!matchLine) return ''

      return matchLine
        .split('')
        .map(char => {
          if (char === ':') {
            return `<span class="match-cell match-close">:</span>`
          }

          if (char === '.') {
            return `<span class="match-cell match-weak">.</span>`
          }

          return `<span class="match-cell">&nbsp;</span>`
        })
        .join('')
    },
    renderSequence(seq, matchLine) {
      if (!seq) return ''

      return seq
        .split('')
        .map((char, index) => {
          const safeChar = char === ' ' ? '&nbsp;' : this.escapeHtml(char)
          const mark = matchLine?.[index]

          if (char === '-') {
            return `<span class="match-gap">-</span>`
          }

          if (mark === ':') {
            return `<span class="seq-blue">${safeChar}</span>`
          }

          if (mark === '.') {
            return `<span class="seq-orange">${safeChar}</span>`
          }

          return `<span class="seq-red">${safeChar}</span>`
        })
        .join('')
    },

    renderMatchLine(matchLine) {
      if (!matchLine) return ''

      return matchLine
        .split('')
        .map(char => {
          if (char === ':') {
            return `<span class="mark-green">:</span>`
          }

          if (char === '.') {
            return `<span class="mark-yellow">.</span>`
          }

          if (char === '-') {
            return `<span class="match-gap">-</span>`
          }

          return '&nbsp;'
        })
        .join('')
    },

    downloadReport() {
      const report = [
        'US-align Structure Alignment Report',
        '',
        `Structure File 1: ${this.result.structureFile1Name || '-'}`,
        `Structure File 2: ${this.result.structureFile2Name || '-'}`,
        '',
        `TM-score Structure 1: ${this.result.tmScore1}`,
        `TM-score Structure 2: ${this.result.tmScore2}`,
        `RMSD: ${this.result.rmsd} Å`,
        `Aligned Length: ${this.result.alignedLength}`,
        `Seq_ID: ${this.result.seqId}`,
        `Seq_ID %: ${this.result.seqIdPercent}%`,
        `Structure 1 Length: ${this.result.structure1Length}`,
        `Structure 2 Length: ${this.result.structure2Length}`,
        `Structure 1 Coverage: ${this.result.coverage1}%`,
        `Structure 2 Coverage: ${this.result.coverage2}%`,
        '',
        // `Interpretation: ${this.result.interpretation || this.fallbackInterpretation}`,
        '',
        'Raw Output:',
        this.result.rawOutput || ''
      ].join('\n')

      const blob = new Blob([report], {
        type: 'text/plain;charset=utf-8'
      })

      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')

      link.href = url
      link.download = 'usalign_report.txt'
      link.click()

      URL.revokeObjectURL(url)
    },

    exportPdb() {
      const structureUrl =
        this.result?.superposedStructure1Url ||
        this.result?.superposedStructureUrl ||
        this.result?.superposedPdbUrl

      if (!structureUrl) {
        this.$message.warning('No superposed structure file is available.')
        return
      }

      const url = this.getFullMediaUrl(structureUrl)
      const link = document.createElement('a')

      const format = this.get3DmolFormat(
        this.result.superposedStructureFormat || structureUrl
      )

      const extension = format === 'pdb' ? 'pdb' : 'cif'

      link.href = url
      link.download = `superposed_structure.${extension}`
      link.click()
    },

    viewRawOutput() {
      this.activeTab = 'text'
    },

    formatMetric(value) {
      if (value === null || value === undefined || value === '') {
        return '-'
      }

      return value
    },

    formatFileSize(size) {
      if (!size) return '0 B'

      const mb = size / 1024 / 1024

      if (mb >= 1) {
        return `${mb.toFixed(1)} MB`
      }

      const kb = size / 1024

      return `${kb.toFixed(1)} KB`
    }
  }
}
</script>

<style scoped>
.structure-align-page {
  width: 100%;
  min-height: 100vh;
  padding: 24px;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
  background: #f5faff;
  color: #1f2937;
  font-family: Arial, Helvetica, sans-serif;
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

.summary-panel {
  margin-top: 24px;
  padding: 60px 28px 28px;
}

.result-panel {
  margin-top: 24px;
  padding: 64px 28px 28px;
}

.section-desc {
  margin-top: 8px;
  color: #324b6b;
  font-size: 14px;
}

.input-inner {
  width: 100%;
}

.structure-input-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 120px minmax(0, 1fr);
  gap: 30px;
  align-items: center;
}

.upload-block {
  min-width: 0;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background: #ffffff;
  padding: 16px;
  box-sizing: border-box;
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
}

.required-star {
  color: #f56c6c;
  margin-right: 4px;
  font-weight: 700;
}

.input-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.drop-zone {
  display: block;
  min-height: 138px;
  padding: 36px 20px 30px;
  border: 1px dashed #8bbcff;
  border-radius: 6px;
  background: #ffffff;
  text-align: center;
  cursor: pointer;
  box-sizing: border-box;
  transition: all 0.2s ease;
}

.drop-zone:hover {
  border-color: #409eff;
  background: #f5fbff;
}

.upload-filled-icon {
  color: #a1d0dd;
  font-size: 32px;
  line-height: 0.5;
}

.upload-main-text {
  margin-top: 10px;
  color: #324b6b;
  font-size: 15px;
  line-height: 1.5;
}

.upload-sub-text {
  margin-top: 4px;
  color: #606266;
  font-size: 13px;
}

.uploaded-file-row {
  margin-top: 12px;
  min-height: 58px;
  padding: 10px 14px;
  border: 1px solid #e0e6ef;
  border-radius: 6px;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
}

.uploaded-file-left {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.uploaded-file-icon {
  width: 30px;
  height: 30px;
  color: #a1d0dd;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-sizing: border-box;
}

.uploaded-file-icon :deep(.el-icon) {
  width: 28px;
  height: 28px;
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.uploaded-file-icon :deep(svg) {
  width: 28px;
  height: 28px;
  display: block;
}

.uploaded-file-info {
  min-width: 0;
}

.uploaded-file-name {
  color: #303133;
  font-size: 15px;
  font-weight: 700;
  line-height: 1.2;
  max-width: 360px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.uploaded-file-size {
  margin-top: 3px;
  color: #606266;
  font-size: 13px;
  line-height: 1.2;
}

.uploaded-file-actions {
  display: flex;
  align-items: center;
  gap: 28px;
  flex-shrink: 0;
}

.uploaded-remove-btn {
  border: none;
  background: transparent;
  color: #606266;
  font-size: 30px;
  line-height: 1;
  cursor: pointer;
}

.uploaded-remove-btn:hover {
  color: #f56c6c;
}

.compare-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 22px;
}

.summary-inner {
  width: 100%;
  margin-top: 15px;
}

.summary-table {
  display: grid;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  overflow: hidden;
}

.structure-summary-table {
  grid-template-columns: repeat(6, 1fr);
}

.summary-cell {
  min-height: 86px;
  padding: 16px 12px;
  border-right: 1px solid #e4e7ed;
  border-bottom: 1px solid #e4e7ed;
  background: #fbfdff;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 6px;
  text-align: center;
}

.summary-label {
  color: #303133;
  font-size: 15px;
  font-weight: 700;
  white-space: nowrap;
}

.summary-sub {
  font-size: 13px;
  font-weight: 700;
}

.summary-value {
  color: #303133;
  font-size: 20px;
  font-weight: 700;
  margin-top: 5px;
}

.rmsd-value {
  color: #5ccd97;
}

.aligned-value {
  color: #8acfd6;
}

.seqid-value {
  color: #ac72af;
}

.blue-text {
  color: #0969e8;
}

.red-text {
  color: #e11d1d;
}

.download-area {
  position: absolute;
  top: 26px;
  right: 28px;
  display: flex;
  gap: 10px;
}

.result-inner {
  width: 100%;
  overflow-x: auto;
  margin-top: 15px;
}

.structure-result-grid {
  display: grid;
  /*
   * 左侧 3Dmol 占 40%
   * 右侧 Alignment Text 占 60%
   * 这样序列比对文本会有更大的横向空间，不容易挤在一起。
   */
  grid-template-columns: minmax(360px, 0.8fr) minmax(720px, 1.4fr);
  gap: 20px;
  align-items: stretch;
}

.viewer-card,
.alignment-card {
  position: relative;
  min-height: 520px;
  border: 1px solid #e4e7ed;
  margin-left: 0;
  border-radius: 6px;
  background: #ffffff;
  overflow: hidden;
  box-sizing: border-box;
}

.card-title {
  display: inline-block;
  min-width: 150px;
  padding: 8px 16px;
  background: #c8edf7;
  color: #38546f;
  font-size: 15px;
  font-weight: 700;
  border-radius: 0 0 5px 0;
}

.viewer-tools {
  position: absolute;
  left: 18px;
  top: 75px;
  display: flex;
  flex-direction: column;
  gap: 7px;
  z-index: 10;
}

.viewer-tools button,
.viewer-top-actions button {
  width: 34px;
  height: 34px;
  border: 1px solid #cddbea;
  border-radius: 6px;
  background: #ffffff;
  color: #2d6cdf;
  cursor: pointer;
}

.viewer-tools button:hover,
.viewer-top-actions button:hover {
  background: #eef6ff;
}

.viewer-top-actions {
  position: absolute;
  right: 18px;
  top: 22px;
  display: flex;
  gap: 10px;
  z-index: 10;
}

/* =========================
   3Dmol Viewer
========================= */

.model-viewer-wrapper {
  position: relative;
  width: 100%;
  height: 420px;
  margin-top: 14px;
  background: #ffffff;
  overflow: hidden;
}

.model-viewer {
  position: relative;
  width: 100%;
  height: 100%;
  background: #ffffff;
}

.model-viewer canvas {
  width: 100% !important;
  height: 100% !important;
}

.viewer-empty-text {
  position: absolute;
  left: 50%;
  top: 50%;
  color: #909399;
  font-size: 14px;
  transform: translate(-50%, -50%);
  z-index: 2;
}

.viewer-legend {
  position: absolute;
  left: 20px;
  bottom: 24px;
  display: flex;
  gap: 24px;
  color: #0969e8;
  font-size: 14px;
  font-weight: 700;
  flex-wrap: wrap;
  z-index: 5;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 14px;
  height: 14px;
  display: inline-block;
}

.blue-bg {
  background: #0b6ff3;
}

.red-bg {
  background: #e51e1e;
}

.axis-box {
  position: absolute;
  right: 45px;
  bottom: 35px;
  width: 80px;
  height: 70px;
  font-weight: 700;
  pointer-events: none;
}

.axis-y {
  position: absolute;
  left: 34px;
  top: 0;
  color: #0fa43b;
}

.axis-x {
  position: absolute;
  right: 4px;
  bottom: 8px;
  color: #e51e1e;
}

.axis-z {
  position: absolute;
  left: 0;
  bottom: 0;
  color: #0b6ff3;
}

.alignment-card {
  padding-bottom: 14px;
}

.alignment-tabs {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 16px 0;
  border-bottom: 1px solid #e0e8f1;
}

.alignment-tabs button {
  padding: 10px 6px;
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: #415977;
  font-size: 14px;
  cursor: pointer;
}

.alignment-tabs button.active {
  color: #0969e8;
  border-bottom-color: #0969e8;
  font-weight: 700;
}

.color-scheme {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #415977;
  font-size: 13px;
}

.color-scheme select {
  height: 32px;
  border: 1px solid #ccd9e6;
  border-radius: 6px;
  background: #ffffff;
  color: #2d3c52;
}

.alignment-box {
  margin: 0 14px;
  margin-top: 8px;
  padding: 18px 16px;
  min-height: 320px;
  max-height: 420px;
  border: 1px solid #dce6ef;
  border-radius: 7px;
  background: #ffffff;
  overflow: auto;
}

.alignment-block-list {
  min-width: max-content;
}

.btn-icon {
  margin-right: 6px;
}

.alignment-box pre {
  margin: 0;
  color: #111827;
  font-size: 14px;
  line-height: 1.65;
  font-family: Consolas, Monaco, "Courier New", monospace;
  white-space: pre;
}

.alignment-block {
  margin-bottom: 24px;
  font-family: Consolas, Monaco, "Courier New", monospace;
}

.alignment-row {
  display: grid;
  grid-template-columns: 120px 48px minmax(520px, 1fr) 48px;
  align-items: center;
  column-gap: 10px;
  white-space: nowrap;
  line-height: 1.8;
}
.line-label {
  color: #111827;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
}

.seq-pos {
  color: #111827;
  font-weight: 700;
}

.seq-text {
  font-family: Consolas, Monaco, "Courier New", monospace;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.seq-blue {
  color: #0969e8;
  font-weight: 700;
}

.seq-red {
  color: #e11d1d;
  font-weight: 700;
}

.seq-orange {
  color: #f97316;
  font-weight: 700;
}

.mark-green {
  color: #16a34a;
  font-weight: 700;
}

.mark-yellow {
  color: #eab308;
  font-weight: 700;
}

.match-gap {
  color: #64748b;
  font-weight: 700;
}

.empty-alignment-text {
  color: #606266;
  font-size: 14px;
  padding: 20px 0;
}

.alignment-legend {
  display: flex;
  justify-content: space-around;
  gap: 16px;
  flex-wrap: wrap;
  padding: 10px 16px;
  color: #52687f;
  font-size: 13px;
  margin-top: 10px;
}

/* .interpretation-box {
  margin: 20px 14px 0;
  padding: 12px 16px;
  border: 1px solid #a9d1ff;
  border-radius: 7px;
  background: #f0f8ff;
  color: #294565;

  display: flex;
  align-items: center;
  justify-content: center;

  gap: 12px;
  line-height: 1.55;
  font-size: 14px;
  text-align: center;
}

.interpretation-text {
  text-align: center;
}
.info-big {
  color: #0969e8;
  font-size: 22px;
} */

@media (max-width: 1200px) {
  .structure-input-grid {
    grid-template-columns: 1fr;
  }

  .compare-center {
    flex-direction: row;
    justify-content: center;
  }

  .structure-summary-table {
    grid-template-columns: repeat(2, 1fr);
  }

  .summary-cell {
    border-right: 1px solid #e4e7ed;
    border-bottom: 1px solid #e4e7ed;
  }

  .summary-cell:nth-child(2n) {
    border-right: none;
  }

  .summary-cell:nth-last-child(-n + 5) {
    border-bottom: 1px solid #e4e7ed;
  }

  .summary-cell:last-child {
    border-bottom: none;
  }

  .structure-result-grid {
    grid-template-columns: 1fr;
  }

  .model-viewer-wrapper {
    height: 460px;
  }
}
.visual-alignment-block {
  margin-bottom: 30px;
  font-family: Consolas, Monaco, "Courier New", monospace;
}

.visual-scale-row,
.visual-align-row {
  display: grid;
  grid-template-columns: 80px 50px max-content 50px;
  align-items: center;
  column-gap: 15px;
  white-space: nowrap;
  line-height: 1.6;
}

.visual-label {
  color: #111827;
  font-weight: 700;
  font-family: Arial, Helvetica, sans-serif;
  overflow: hidden;
  text-overflow: ellipsis;
}

.visual-start,
.visual-end {
  color: #4b5563;
  font-weight: 700;
  text-align: right;
  font-family: Consolas, Monaco, "Courier New", monospace;
}

.visual-seq-line {
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
  font-family: Consolas, Monaco, "Courier New", monospace;
}

.visual-scale-line {
  height: 24px;
  align-items: flex-end;
}

:deep(.scale-cell) {
  position: relative;
  width: 16px;
  height: 22px;
  margin-right: 1px;
  display: inline-flex;
  align-items: flex-end;
  justify-content: center;
  box-sizing: border-box;
}

:deep(.scale-number) {
  position: absolute;
  left: 50%;
  bottom: 0;
  transform: translateX(-50%);
  color: #6b7280;
  font-size: 12px;
  font-weight: 600;
  font-family: Arial, Helvetica, sans-serif;
}
:deep(.aa-cell) {
  width: 16px;
  height: 24px;
  margin-right: 1px;
  border-radius: 3px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #111827;
  font-size: 14px;
  font-weight: 700;
  box-sizing: border-box;
}

/* ':' 对应的残基，绿色 */
:deep(.aa-close) {
  background: #c9f5c4;
}

/* '.' 对应的残基，粉红色 */
:deep(.aa-weak) {
  background: #f9b9b3;
}

/* gap '-'，灰色 */
:deep(.aa-gap) {
  background: #d9d9d9;
  color: #374151;
}

/* 无 ':' 或 '.' 的普通残基，浅灰色 */
:deep(.aa-neutral) {
  background: #eeeeee;
}

/* 中间 match line 的每个符号格子 */
:deep(.match-cell) {
  width: 16px;
  height: 20px;
  margin-right: 1px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #111827;
  font-size: 14px;
  font-weight: 700;
  box-sizing: border-box;
}

/* match line 中 ':' 的颜色 */
:deep(.match-close) {
  color: #16a34a;
}

/* match line 中 '.' 的颜色 */
:deep(.match-weak) {
  color: #ef4444;
}

.match-row {
  margin-top: 4px;
  margin-bottom: 4px;
}
.visual-legend {
  justify-content: flex-start;
  border-top: 1px solid #e5e7eb;
  margin: 16px 14px 0;
  padding-top: 14px;
}

.visual-legend span {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.legend-box {
  width: 18px;
  height: 18px;
  border-radius: 3px;
  display: inline-block;
}

.legend-close {
  background: #c9f5c4;
}

.legend-weak {
  background: #f9b9b3;
}

.legend-gap {
  background: #d9d9d9;
}
@media (max-width: 768px) {
  .structure-align-page {
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

  .input-title-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .drop-zone {
    min-height: 130px;
    padding: 30px 16px;
  }

  .download-area {
    position: static;
    display: flex;
    justify-content: flex-end;
    flex-wrap: wrap;
    margin-bottom: 16px;
  }

  .structure-summary-table {
    grid-template-columns: 1fr;
  }

  .summary-cell {
    border-right: none !important;
    border-bottom: 1px solid #e4e7ed !important;
  }

  .summary-cell:last-child {
    border-bottom: none !important;
  }

  .uploaded-file-name {
    max-width: 180px;
  }

  .alignment-tabs {
    flex-wrap: wrap;
  }

  .color-scheme {
    width: 100%;
    margin-left: 0;
    padding-bottom: 8px;
  }

  .model-viewer-wrapper {
    height: 420px;
  }

  .viewer-tools {
    top: 65px;
  }
}
</style>
