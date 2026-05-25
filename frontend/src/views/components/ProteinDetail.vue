<template>
  <div class="protein-detail-page">
    <div class="page-container">
      <div class="page-header">
        <el-button
          size="large"
          plain
          type="primary"
          @click="goBack"
        >
          <el-icon>
            <CaretLeft />
          </el-icon>
          <span>Back</span>
        </el-button>
      </div>

      <div class="panel-card detail-panel">
        <div class="panel-tag">Protein Table</div>

        <div class="detail-inner">
          <div
            v-loading="detailLoading"
            class="vertical-detail-table"
          >
            <el-empty
              v-if="!proteinTableData.length"
              description="No data"
            />

            <template v-else>
              <div
                v-for="row in proteinTableData"
                :key="row.protein_id || row.gene_id"
                class="vertical-detail-card"
              >
                <div class="vertical-detail-row">
                  <div class="vertical-detail-label">Protein Name</div>
                  <div class="vertical-detail-value">
                   {{ formatProteinName(row.protein_id) || '-' }}
                  </div>
                </div>

                <div class="vertical-detail-row">
                  <div class="vertical-detail-label">Protein Class</div>
                  <div class="vertical-detail-value">
                    {{ row.protein_class || '-' }}
                  </div>
                </div>

                <div class="vertical-detail-row">
                  <div class="vertical-detail-label">Amino Acids</div>
                  <div class="vertical-detail-value">
                    {{ row.amino_acids || '-' }}
                  </div>
                </div>

                <div class="vertical-detail-row">
                <div class="vertical-detail-label">Gene Name</div>
                <div class="vertical-detail-value italic-text">
                  {{ formatGeneName(row.gene_id) || '-' }}
                </div>
                </div>

                <div class="vertical-detail-row">
                <div class="vertical-detail-label">Organism</div>
                <div class="vertical-detail-value italic-text">
                    {{ row.organism || '-' }}
                </div>
                </div>

                <div class="vertical-detail-row">
                  <div class="vertical-detail-label">Domain</div>
                  <div class="vertical-detail-value">
                    <el-link
                      v-if="row.domain"
                      type="primary"
                      :underline="false"
                      class="domain-link"
                      @click="handleDomainClick(row)"
                    >
                      {{ row.domain }}
                    </el-link>

                    <span v-else>-</span>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>

      <ProteinSequencePanel
        :sequence-data="proteinData"
        :sequence-loading="detailLoading"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { CaretLeft } from '@element-plus/icons-vue'
import request from '@/utils/request'

import ProteinSequencePanel from './ProteinSequencePanel.vue'

const route = useRoute()
const router = useRouter()

const proteinData = ref({})
const detailLoading = ref(false)

const formatProteinName = value => {
  if (!value) return value

  const name = String(value).trim()

  return name.endsWith('.p') ? name : `${name}.p`
}

const formatGeneName = value => {
  if (!value) return value

  return String(value)
    .trim()
    .replace(/(^|_)(Gm|Lj|Pv|Mt)/gi, '$1')
}

const proteinId = computed(() => {
  return String(
    route.params.proteinId ||
    route.query.protein_id ||
    ''
  ).trim()
})

const proteinTableData = computed(() => {
  if (!proteinData.value || !Object.keys(proteinData.value).length) {
    return []
  }

  return [
    {
      protein_id: proteinData.value.protein_id || proteinId.value || '',
      protein_class: proteinData.value.protein_class || '',
      amino_acids: proteinData.value.amino_acids || '',
      gene_id: proteinData.value.gene_id || '',
      organism: proteinData.value.organism || '',
      domain: proteinData.value.domain || ''
    }
  ]
})

const getCachedProteinData = () => {
  const cached = sessionStorage.getItem('selectedProteinData')

  if (!cached) return {}

  try {
    const parsed = JSON.parse(cached)

    if (parsed?.protein_id === proteinId.value) {
      return parsed
    }

    return {}
  } catch (error) {
    return {}
  }
}

const fetchProteinDetail = async id => {
  const res = await request.get(
    '/api/protein/sequence/',
    {
      params: {
        protein_id: id
      }
    }
  )

  return res.data.data || {}
}

const loadProteinDetail = async () => {
  if (!proteinId.value) {
    proteinData.value = {}
    ElMessage.warning('Missing protein ID')
    return
  }

  const cachedRow = getCachedProteinData()

  try {
    detailLoading.value = true

    const detail = await fetchProteinDetail(proteinId.value)

    proteinData.value = {
      ...cachedRow,
      ...detail,
      protein_id: proteinId.value
    }
  } catch (error) {
    console.error('fetch protein detail failed:', error)
    console.error('response data:', error?.response?.data)
    console.error('response status:', error?.response?.status)

    proteinData.value = {
      ...cachedRow,
      protein_id: proteinId.value
    }

    ElMessage.error(error?.response?.data?.message || 'Failed to load protein detail')
  } finally {
    detailLoading.value = false
  }
}

const handleDomainClick = row => {
  if (!row?.domain) return

  const domain = String(row.domain).trim()

  const match = domain.match(/IPR\d+/)

  if (!match) {
    ElMessage.warning('Invalid InterPro domain ID')
    return
  }

  const interProId = match[0]
  const url = `https://www.ebi.ac.uk/interpro/entry/InterPro/${interProId}/`

  window.open(url, '_blank')
}

const goBack = () => {
  sessionStorage.setItem('fromProteinDetail', '1')

  if (window.history.length > 1) {
    router.back()
  } else {
    router.push({
      name: 'gene-info'
    })
  }
}

onMounted(() => {
  loadProteinDetail()
})

watch(
  () => [
    route.params.proteinId,
    route.query.protein_id
  ],
  () => {
    loadProteinDetail()
  }
)
</script>

<style scoped>
.italic-text {
  font-style: italic;
}
.protein-detail-page {
  width: 100%;
  padding: 24px;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
}

.page-container {
  width: 100%;
  max-width: 1600px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
  font-size: 15px;
  font-weight: 700;
}

.panel-card {
  position: relative;
  width: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  background: #fff;
  box-sizing: border-box;
}

.detail-panel {
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

.detail-inner {
  width: 100%;
  margin-top: 28px;
}

.vertical-detail-table {
  width: 100%;
  min-height: 80px;
}

.vertical-detail-card {
  width: 100%;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #ffffff;
  overflow: hidden;
  box-sizing: border-box;
}

.vertical-detail-row {
  display: flex;
  width: 100%;
  border-bottom: 1px solid #ebeef5;
  box-sizing: border-box;
}

.vertical-detail-row:last-child {
  border-bottom: none;
}

.vertical-detail-label {
  width: 180px;
  flex-shrink: 0;
  padding: 14px 16px;
  background: #f8fbff;
  color: #303133;
  font-size: 15px;
  font-weight: 700;
  box-sizing: border-box;
}

.vertical-detail-value {
  flex: 1;
  padding: 14px 16px;
  font-size: 15px;
  color: #606266;
  word-break: break-all;
  box-sizing: border-box;
}

.domain-link {
  text-decoration: underline;
  cursor: pointer;
}

@media (max-width: 768px) {
  .protein-detail-page {
    padding: 16px;
  }

  .detail-panel {
    padding-left: 16px;
    padding-right: 16px;
    padding-top: 44px;
    padding-bottom: 20px;
  }

  .panel-tag {
    font-size: 16px;
    padding: 10px 18px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .vertical-detail-row {
    flex-direction: column;
  }

  .vertical-detail-label {
    width: 100%;
    border-bottom: 1px solid #ebeef5;
  }
}
</style>
