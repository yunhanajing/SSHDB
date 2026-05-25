<template>
  <div class="search-page">
    <div class="page-container">
      <GeneSearch
        v-if="showGeneSearch"
        @search="handleGeneSearch"
        @reset="handleReset"
      />

      <GeneTable
        v-if="showResultPanel"
        :table-data="tableData"
        :table-loading="tableLoading"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

import GeneSearch from './components/GeneSearch.vue'
import GeneTable from './components/GeneTable.vue'

const route = useRoute()

const tableData = ref([])
const tableLoading = ref(false)
const showResultPanel = ref(false)

const fromHome = computed(() => route.query.from === 'home')
const queryType = computed(() => String(route.query.type || ''))
const keyword = computed(() => String(route.query.keyword || '').trim())

const showGeneSearch = computed(() => {
  return !fromHome.value
})

const parseGeneIds = value => {
  return String(value)
    .split(/[\n,;，；\s]+/)
    .map(item => item.trim())
    .filter(Boolean)
}

const formatProteinId = value => {
  if (!value) return value

  let proteinId = String(value).trim()

  if (!proteinId.endsWith('.p')) {
    proteinId = `${proteinId}.p`
  }

  return proteinId
}

const formatGeneName = value => {
  if (!value) return value

  return String(value)
    .trim()
    .replace(/Gm|Lj|Pv|Mt/gi, '')
}

const formatProteinInfoRows = rows => {
  return (rows || []).map(row => {
    const rawProteinId = row.protein_id

    return {
      ...row,

      // 原始 protein_id 保留，不加 .p
      // 用于进入详情页和查询序列
      protein_id: rawProteinId,

      // 只用于前端表格展示
      protein_id_display: formatProteinId(rawProteinId),

      // gene / gene_id 去除 Gm、Lj、Pv、Mt
      gene: formatGeneName(row.gene),
      gene_id: formatGeneName(row.gene_id)
    }
  })
}

const fetchByGene = async geneIdList => {
  const params = new URLSearchParams()

  geneIdList.forEach(item => {
    const cleanItem = String(item)
      .trim()
      .replace(/[,，;；]+$/g, '')

    if (cleanItem) {
      params.append('gene_id', cleanItem)
    }
  })

  const res = await request.get(
    '/api/protein/info/',
    { params }
  )

  return formatProteinInfoRows(res.data.data || [])
}

const fetchByOrganism = async organism => {
  const params = new URLSearchParams()

  const cleanOrganism = String(organism)
    .trim()
    .replace(/[,，;；]+$/g, '')

  if (cleanOrganism) {
    params.append('organism', cleanOrganism)
  }

  const res = await request.get(
    '/api/protein/info/',
    { params }
  )

  return formatProteinInfoRows(res.data.data || [])
}

const handleGeneSearch = async geneIdList => {
  if (!geneIdList.length) {
    ElMessage.warning('Please input gene ID')
    return
  }

  try {
    tableLoading.value = true

    tableData.value = await fetchByGene(geneIdList)
    showResultPanel.value = true

    // 保存当前搜索结果，供详情页 Back 回来恢复
    saveGeneSearchState()
  } catch (error) {
    console.error('gene search failed:', error)
    console.error('response data:', error?.response?.data)
    console.error('response status:', error?.response?.status)

    tableData.value = []
    showResultPanel.value = true

    ElMessage.error(error?.response?.data?.message || 'Search failed')
  } finally {
    tableLoading.value = false
  }
}

const runHomeSearch = async () => {
  // 从 Home 页跳转过来的搜索
  if (fromHome.value) {
    if (!keyword.value) {
      tableData.value = []
      showResultPanel.value = false
      ElMessage.warning('Missing search keyword')
      return
    }

    try {
      tableLoading.value = true

      if (queryType.value === 'gene') {
        const geneIdList = parseGeneIds(keyword.value)
        tableData.value = await fetchByGene(geneIdList)
      } else if (queryType.value === 'organism') {
        tableData.value = await fetchByOrganism(keyword.value)
      } else {
        tableData.value = []
        ElMessage.warning('Unknown search type')
      }

      showResultPanel.value = true
      saveGeneSearchState()
    } catch (error) {
      console.error('home search failed:', error)
      console.error('response data:', error?.response?.data)
      console.error('response status:', error?.response?.status)

      tableData.value = []
      showResultPanel.value = true

      ElMessage.error(error?.response?.data?.message || 'Search failed')
    } finally {
      tableLoading.value = false
    }

    return
  }

  // 只有从蛋白详情页返回时，才恢复 table
  const fromProteinDetail = sessionStorage.getItem('fromProteinDetail')

  if (fromProteinDetail === '1') {
    const restored = restoreGeneSearchState()

    sessionStorage.removeItem('fromProteinDetail')

    if (!restored) {
      tableData.value = []
      showResultPanel.value = false
    }

    return
  }

  // 普通进入 Gene Search 页面：只展示搜索框
  tableData.value = []
  showResultPanel.value = false
}

const saveGeneSearchState = () => {
  sessionStorage.setItem(
    'geneSearchState',
    JSON.stringify({
      tableData: tableData.value,
      showResultPanel: showResultPanel.value
    })
  )
}

const restoreGeneSearchState = () => {
  const cached = sessionStorage.getItem('geneSearchState')

  if (!cached) return false

  try {
    const parsed = JSON.parse(cached)

    tableData.value = Array.isArray(parsed.tableData)
      ? parsed.tableData
      : []

    showResultPanel.value = Boolean(parsed.showResultPanel)

    return true
  } catch (error) {
    return false
  }
}

const handleReset = () => {
  tableData.value = []
  showResultPanel.value = false
  sessionStorage.removeItem('geneSearchState')
  sessionStorage.removeItem('fromProteinDetail')
}

onMounted(() => {
  runHomeSearch()
})

watch(
  () => route.query,
  () => {
    runHomeSearch()
  }
)
</script>

<style scoped>
.search-page {
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

@media (max-width: 768px) {
  .search-page {
    padding: 16px;
  }
}
</style>
