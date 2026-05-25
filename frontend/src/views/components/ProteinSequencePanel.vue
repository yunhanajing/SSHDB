<template>
  <div class="panel-card sequence-panel">
    <div class="panel-tag">Sequence</div>

    <div class="sequence-inner" v-loading="sequenceLoading">
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
</template>

<script setup>
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'

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

const canDownload = computed(() => {
  return Boolean(
    props.sequenceData?.protein_id &&
    props.sequenceData?.protein_sequence
  )
})

const formatFastaSequence = sequence => {
  return String(sequence || '')
    .replace(/\s+/g, '')
    .match(/.{1,60}/g)
    ?.join('\n') || ''
}

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

.sequence-panel {
  margin-top: 28px;
  padding: 48px 28px 28px;
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

.sequence-inner {
  width: 100%;
  margin-top: 28px;
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
  .sequence-panel {
    padding-left: 16px;
    padding-right: 16px;
    padding-top: 44px;
    padding-bottom: 20px;
  }

  .panel-tag {
    font-size: 16px;
    padding: 10px 18px;
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
