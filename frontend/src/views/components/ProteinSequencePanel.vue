<template>
  <div class="protein-sequence-panels">
    <div class="panel-card structure-panel">
      <div class="panel-tag">Structure</div>

      <div
        class="structure-inner"
        v-loading="sequenceLoading || structureLoading"
      >
        <div class="structure-viewer-card">
          <div class="viewer-card-title">3Dmol</div>

          <div
            v-if="hasCifStructure"
            class="structure-viewer-tools"
          >
            <button
              type="button"
              title="Reset structure view"
              @click="resetStructureView"
            >
              <el-icon>
                <RefreshRight />
              </el-icon>
            </button>

            <button
              type="button"
              title="Zoom in"
              @click="zoomInStructure"
            >
              <el-icon>
                <ZoomIn />
              </el-icon>
            </button>

            <button
              type="button"
              title="Zoom out"
              @click="zoomOutStructure"
            >
              <el-icon>
                <ZoomOut />
              </el-icon>
            </button>

            <button
              type="button"
              title="Download CIF"
              :disabled="!canDownloadCif"
              @click="handleDownloadCif"
            >
              <el-icon>
                <Download />
              </el-icon>
            </button>
          </div>

          <div class="structure-viewer-shell">
            <div
              ref="structureViewerEl"
              class="structure-viewer"
            />

            <div
              v-if="showStructureEmpty"
              class="structure-empty"
            >
              {{ structureMessage }}
            </div>
          </div>
        </div>

        <div class="structure-empty-space">
          <div
            v-if="hasCifStructure"
            class="structure-meta"
          >
            <div class="structure-confidence-panel">
              <h3>Structure Confidence</h3>

              <div class="plddt-legend-table">
                <div
                  v-for="item in plddtLegend"
                  :key="item.name"
                  class="plddt-legend-row"
                >
                  <div
                    class="plddt-dot"
                    :style="{ backgroundColor: item.color }"
                  />
                  <div class="plddt-name">{{ item.name }}</div>
                  <div class="plddt-rule">{{ item.rule }}</div>
                  <div
                    class="plddt-bar"
                    :style="{ backgroundColor: item.color }"
                  />
                </div>
              </div>

              <div class="confidence-score-grid">
                <div class="confidence-score-card iptm-card">
                  <div class="score-content">
                    <div class="score-label">iPTM</div>
                    <div class="score-value">{{ iptmScore }}</div>
                    <div class="score-help">Interface predicted TM-score</div>
                  </div>
                </div>

                <div class="confidence-score-card ptm-card">
                  <div class="score-content">
                    <div class="score-label">pTM</div>
                    <div class="score-value">{{ ptmScore }}</div>
                    <div class="score-help">Predicted TM-score</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="panel-card sequence-panel">
      <div class="panel-tag">Sequence</div>

      <div
        class="sequence-inner"
        v-loading="sequenceLoading"
      >
        <div class="sequence-tab-header">
          <div class="sequence-tab active">
            Protein
          </div>

          <el-button
            type="primary"
            plain
            circle
            :disabled="!canDownload"
            class="download-button"
            aria-label="Download FASTA"
            @click="handleDownload"
        >
            <el-icon>
            <Download />
            </el-icon>
          </el-button>
        </div>

        <div class="sequence-box">
          {{ proteinSequence }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Download,
  RefreshRight,
  ZoomIn,
  ZoomOut
} from '@element-plus/icons-vue'
import * as $3Dmol from '3dmol'

import request from '@/utils/request'

const props = defineProps({
  sequenceData: {
    type: Object,
    default: () => ({})
  },
  sequenceLoading: {
    type: Boolean,
    default: false
  }
})

const proteinSequence = computed(() => {
  return props.sequenceData?.protein_sequence || 'No protein sequence'
})

const structureViewerEl = ref(null)
const structureLoading = ref(false)
const structureRendered = ref(false)
const structureError = ref('')

let structureViewer = null
let structureRequestToken = 0
let structureInitialView = null

const plddtLegend = [
  {
    name: 'Very high',
    rule: 'pLDDT > 90',
    color: '#4361ee',
    min: 90
  },
  {
    name: 'Confident',
    rule: '90 > pLDDT > 70',
    color: '#45c4dc',
    min: 70
  },
  {
    name: 'Low',
    rule: '70 > pLDDT > 50',
    color: '#f3ed1b',
    min: 50
  },
  {
    name: 'Very low',
    rule: 'pLDDT < 50',
    color: '#ef7d22',
    min: -Infinity
  }
]

const cifFile = computed(() => {
  return props.sequenceData?.cif_file || {}
})

const confidenceSummary = computed(() => {
  return cifFile.value?.confidence_summary || {}
})

const formatConfidenceScore = value => {
  if (value === null || value === undefined || value === '') return '-'

  const score = Number(value)

  return Number.isFinite(score) ? score.toFixed(2) : '-'
}

const iptmScore = computed(() => {
  return formatConfidenceScore(confidenceSummary.value?.iptm)
})

const ptmScore = computed(() => {
  return formatConfidenceScore(confidenceSummary.value?.ptm)
})

const cifUrl = computed(() => {
  const directUrl = String(cifFile.value?.url || '').trim()

  if (directUrl) return directUrl

  const proteinId = String(props.sequenceData?.protein_id || '').trim()

  if (cifFile.value?.exists && proteinId) {
    return `/api/protein/cif/?protein_id=${encodeURIComponent(proteinId)}`
  }

  return ''
})

const hasCifStructure = computed(() => {
  return Boolean(cifFile.value?.exists && cifUrl.value)
})

const structureMessage = computed(() => {
  if (structureError.value) return structureError.value

  if (!props.sequenceData?.protein_id) {
    return 'Select a protein to view its predicted structure.'
  }

  if (cifFile.value?.expected_filename) {
    return `No CIF structure file found: ${cifFile.value.expected_filename}`
  }

  return 'No CIF structure file found for this protein.'
})

const showStructureEmpty = computed(() => {
  return !props.sequenceLoading && !structureLoading.value && (
    !hasCifStructure.value ||
    Boolean(structureError.value) ||
    !structureRendered.value
  )
})

const canDownload = computed(() => {
  return Boolean(
    props.sequenceData?.protein_id &&
    props.sequenceData?.protein_sequence
  )
})

const canDownloadCif = computed(() => {
  return Boolean(
    props.sequenceData?.protein_id &&
    hasCifStructure.value
  )
})

const formatFastaSequence = sequence => {
  return String(sequence || '')
    .replace(/\s+/g, '')
    .match(/.{1,60}/g)
    ?.join('\n') || ''
}

const getPlddtColor = atom => {
  const plddt = Number(atom?.b)

  if (!Number.isFinite(plddt)) return '#a8abb2'

  return plddtLegend.find(item => plddt > item.min)?.color || '#a8abb2'
}

const getStructureViewer = () => {
  if (!structureViewerEl.value) return null

  if (!structureViewer) {
    structureViewer = $3Dmol.createViewer(structureViewerEl.value, {
      backgroundColor: '#ffffff'
    })
  }

  return structureViewer
}

const clearStructureViewer = () => {
  structureRendered.value = false
  structureInitialView = null

  if (!structureViewer) return

  try {
    structureViewer.clear()
    structureViewer.removeAllModels()
    structureViewer.render()
  } catch (error) {
    console.warn('Failed to clear structure viewer:', error)
  }
}

const renderStructure = async () => {
  const currentToken = ++structureRequestToken

  structureError.value = ''
  structureRendered.value = false
  structureInitialView = null

  if (!hasCifStructure.value) {
    clearStructureViewer()
    return
  }

  structureLoading.value = true

  await nextTick()

  const viewer = getStructureViewer()

  if (!viewer) {
    structureError.value = 'Structure viewer is not ready.'
    structureLoading.value = false
    return
  }

  try {
    const res = await request.get(cifUrl.value, {
      responseType: 'text'
    })

    if (currentToken !== structureRequestToken) return

    const cifText = typeof res.data === 'string'
      ? res.data
      : String(res.data || '')

    if (!cifText.trim()) {
      throw new Error('Empty CIF file')
    }

    viewer.clear()
    viewer.removeAllModels()

    const model = viewer.addModel(cifText, 'cif')

    model.setStyle({}, {
      cartoon: {
        colorfunc: getPlddtColor
      }
    })

    viewer.zoomTo()
    viewer.zoom(1.5)
    viewer.render()

    if (typeof viewer.resize === 'function') {
      viewer.resize()
    }

    if (typeof viewer.getView === 'function') {
      const initialView = viewer.getView()
      structureInitialView = Array.isArray(initialView) ? [...initialView] : initialView
    }

    structureRendered.value = true
  } catch (error) {
    console.error('3Dmol structure render failed:', error)
    clearStructureViewer()
    structureError.value = '3Dmol could not load this CIF structure file.'
  } finally {
    if (currentToken === structureRequestToken) {
      structureLoading.value = false
    }
  }
}

const resetStructureView = () => {
  if (!structureViewer || !structureRendered.value) {
    renderStructure()
    return
  }

  if (structureInitialView && typeof structureViewer.setView === 'function') {
    structureViewer.setView(
      Array.isArray(structureInitialView) ? [...structureInitialView] : structureInitialView
    )
  } else {
    structureViewer.zoomTo()
    structureViewer.zoom(1.5)
  }

  if (typeof structureViewer.resize === 'function') {
    structureViewer.resize()
  }

  structureViewer.render()
}

const zoomInStructure = () => {
  if (!structureViewer || !structureRendered.value) return

  structureViewer.zoom(1.25)
  structureViewer.render()
}

const zoomOutStructure = () => {
  if (!structureViewer || !structureRendered.value) return

  structureViewer.zoom(0.8)
  structureViewer.render()
}

watch(
  () => [
    props.sequenceData?.protein_id,
    cifUrl.value,
    props.sequenceLoading
  ],
  () => {
    if (!props.sequenceLoading) {
      renderStructure()
    }
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  structureRequestToken += 1
  clearStructureViewer()
  structureViewer = null
})

const handleDownload = () => {
  const proteinId = String(props.sequenceData?.protein_id || '').trim()
  const sequence = String(props.sequenceData?.protein_sequence || '').trim()

  if (!proteinId || !sequence) {
    ElMessage.warning('No protein sequence to download')
    return
  }

  const organism = String(props.sequenceData?.organism || '').trim()
  const geneId = String(props.sequenceData?.gene_id || '').trim()

  const fastaHeader = [
    `>${proteinId}`,
    organism ? `organism=${organism}` : '',
    geneId ? `gene_id=${geneId}` : ''
  ]
    .filter(Boolean)
    .join(' ')

  const fastaContent = `${fastaHeader}\n${formatFastaSequence(sequence)}\n`

  const blob = new Blob([fastaContent], {
    type: 'text/plain;charset=utf-8;'
  })

  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.setAttribute('download', `${proteinId}.fasta`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  window.URL.revokeObjectURL(url)

  ElMessage.success('Sequence downloaded')
}

const handleDownloadCif = () => {
  const proteinId = String(props.sequenceData?.protein_id || '').trim()
  const downloadUrl = cifUrl.value

  if (!proteinId || !downloadUrl) {
    ElMessage.warning('No CIF file to download')
    return
  }

  const filename = cifFile.value?.filename || `${proteinId}.cif`
  const link = document.createElement('a')

  link.href = downloadUrl
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<style scoped>
.panel-card {
  position: relative;
  width: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  background: #fff;
  box-sizing: border-box;
}

.protein-sequence-panels {
  width: 100%;
}

.structure-panel {
  margin-top: 28px;
  min-height: 620px;
  padding: 88px 28px 28px;
}

.sequence-panel {
  margin-top: 12px;
  padding: 74px 28px 28px;
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

.structure-inner {
  width: 100%;
  min-height: 500px;
  display: grid;
  grid-template-columns: 560px minmax(0, 1fr);
  gap: 28px;
  align-items: start;
}

.structure-viewer-card {
  position: relative;
  width: 560px;
  height: 500px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background: #ffffff;
  overflow: hidden;
  box-sizing: border-box;
}

.viewer-card-title {
  display: inline-flex;
  min-width: 150px;
  height: 32px;
  padding: 0 16px;
  align-items: center;
  justify-content: center;
  background: #c8edf7;
  color: #38546f;
  font-size: 16px;
  font-weight: 700;
  border-radius: 0 0 5px 0;
  box-sizing: border-box;
}

.structure-viewer-tools {
  position: absolute;
  left: 16px;
  top: 66px;
  display: flex;
  flex-direction: column;
  gap: 9px;
  z-index: 10;
}

.structure-viewer-tools button {
  width: 40px;
  height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #d7e4f3;
  border-radius: 6px;
  background: #ffffff;
  color: #2d6cdf;
  font-size: 18px;
  cursor: pointer;
}

.structure-viewer-tools button:disabled {
  color: #a8abb2;
  cursor: not-allowed;
  background: #f5f7fa;
}

.structure-viewer-tools button:hover,
.structure-viewer-tools button:focus {
  background: #eef6ff;
  outline: none;
}

.structure-viewer-shell {
  position: relative;
  width: 100%;
  height: calc(100% - 28px);
  background: #ffffff;
  overflow: hidden;
  box-sizing: border-box;
}

.structure-viewer {
  position: relative;
  width: 100%;
  height: 100%;
  background: #ffffff;
}

.structure-viewer canvas {
  width: 100% !important;
  height: 100% !important;
}

.structure-empty {
  position: absolute;
  left: 50%;
  top: 50%;
  max-width: min(520px, calc(100% - 40px));
  color: #909399;
  font-size: 14px;
  line-height: 1.5;
  text-align: center;
  transform: translate(-50%, -50%);
  z-index: 2;
}

.structure-empty-space {
  min-height: 464px;
  padding: 0;
  box-sizing: border-box;
}

.structure-meta {
  width: 100%;
  min-height: 500px;
  box-sizing: border-box;
}

.structure-confidence-panel {
  width: 100%;
  min-height: 500px;
  padding: 22px 28px 20px;
  border: 1px solid #e0e6ef;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
  box-sizing: border-box;
}

.structure-confidence-panel h3 {
  margin: 0 0 18px;
  color: #0f172a;
  font-size: 20px;
  line-height: 1.2;
  font-weight: 800;
  text-align: center;
}

.plddt-legend-table {
  width: 100%;
  border: 1px solid #e0e6ef;
  border-radius: 8px;
  overflow: hidden;
  background: #ffffff;
  margin-top: 20px;
}

.plddt-legend-row {
  min-height: 58px;
  display: grid;
  grid-template-columns: 28px minmax(92px, 0.7fr) minmax(128px, 0.9fr) minmax(160px, 1.4fr);
  gap: 16px;
  align-items: center;
  padding: 0 22px;
  border-bottom: 1px solid #e7edf5;
  box-sizing: border-box;
}

.plddt-legend-row:last-child {
  border-bottom: none;
}

.plddt-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  justify-self: center;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.14);
}

.plddt-name {
  color: #0f172a;
  font-size: 14px;
  font-weight: 800;
  text-align: center;
}

.plddt-rule {
  color: #64748b;
  font-size: 15px;
  font-weight: 500;
  text-align: center;
}

.plddt-bar {
  width: min(78%, 320px);
  height: 12px;
  border-radius: 999px;
  justify-self: center;
}

.confidence-score-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 22px;
  margin-top: 35px;
}

.confidence-score-card {
  min-height: 88px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px 18px;
  border-radius: 8px;
  background: linear-gradient(135deg, #edf8ff 0%, #f3fbff 100%);
  box-sizing: border-box;
  text-align: center;
}

.score-content {
  min-width: 0;
}

.score-label {
  margin-bottom: 8px;
  color: #0f172a;
  font-size: 15px;
  line-height: 1;
  font-weight: 800;
}

.score-value {
  margin-bottom: 8px;
  color: #1976e8;
  font-size: 24px;
  line-height: 1;
  font-weight: 800;
}

.score-help {
  color: #64748b;
  font-size: 13px;
  line-height: 1.25;
  font-weight: 500;
}

.confidence-note {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 24px;
  color: #64748b;
}

.confidence-note span {
  width: 28px;
  height: 28px;
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #e6f3ff;
  color: #1976e8;
  font-size: 18px;
  font-weight: 800;
}

.confidence-note p {
  margin: 0;
  font-size: 13px;
  line-height: 1.45;
}

.sequence-inner {
  width: 100%;
  margin-top: 0;
}

.sequence-tab-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  border-bottom: 1px solid #dcdfe6;
}

.sequence-tab {
  height: 40px;
  line-height: 40px;
  padding: 0 24px;
  border: 1px solid #dcdfe6;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  background: #ffffff;
  color: #303133;
  font-size: 15px;
  font-weight: 700;
}

.download-button {
  margin-bottom: 6px;
}

.sequence-box {
  min-height: 70px;
  padding: 14px 12px;
  border: 1px solid #dcdfe6;
  border-top: none;
  color: #303133;
  font-size: 15px;
  line-height: 1.45;
  word-break: break-all;
  white-space: pre-wrap;
  background: #ffffff;
  box-sizing: border-box;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  height: 42px;
  min-height: 42px;
  box-sizing: border-box;
  align-items: center;
}

@media (max-width: 768px) {
  .structure-panel,
  .sequence-panel {
    padding-left: 16px;
    padding-right: 16px;
    padding-bottom: 20px;
  }

  .structure-panel {
    min-height: 410px;
    padding-top: 72px;
  }

  .sequence-panel {
    padding-top: 58px;
  }

  .panel-tag {
    font-size: 16px;
    padding: 10px 18px;
  }

  .structure-inner {
    min-height: 320px;
    grid-template-columns: 1fr;
  }

  .structure-viewer-card {
    max-width: 100%;
    width: 100%;
    height: 320px;
  }

  .structure-viewer-tools {
    top: 58px;
  }

  .structure-empty-space {
    display: none;
  }

  .sequence-tab-header {
    align-items: flex-end;
    gap: 12px;
  }

  .download-button {
    margin-bottom: 6px;
  }

  .sequence-box {
    font-size: 14px;
  }
}
</style>
