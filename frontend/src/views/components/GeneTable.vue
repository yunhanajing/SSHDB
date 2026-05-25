<template>
  <div class="panel-card result-panel">
    <div class="panel-tag">Gene Table</div>

    <div class="result-inner">
      <div class="result-toolbar">
        <div class="result-toolbar-left">
          <div class="result-count">
            Total: <span>{{ filteredTotal }}</span>
          </div>

          <el-select
            v-model="pageSize"
            class="page-size-select"
            popper-class="page-size-dropdown"
          >
            <el-option :value="10" label="10 / page" />
            <el-option :value="20" label="20 / page" />
          </el-select>
        </div>

        <div class="result-toolbar-right">
          <el-input
            v-model="tableKeyword"
            placeholder="Search in table"
            clearable
            class="table-search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <el-button
            type="primary"
            plain
            circle
            :disabled="!filteredTableData.length"
            aria-label="Download"
            @click="handleDownload"
          >
            <el-icon><Download /></el-icon>
          </el-button>
        </div>
      </div>

      <div class="table-wrapper">
        <el-table
          v-loading="tableLoading"
          :data="pagedTableData"
          border
          stripe
          style="width: 100%"
          empty-text="No data"
        >
        <el-table-column
        prop="protein_id_display"
        label="Protein Name"
        min-width="220"
        align="center"
        header-align="center"
        >
        <template #default="{ row }">
            <el-link
            v-if="row.protein_id"
            type="primary"
            :underline="false"
            class="protein-id-link"
            @click="handleProteinClick(row)"
            >
            {{ row.protein_id_display || row.protein_id }}
            </el-link>

            <span v-else>-</span>
        </template>
        </el-table-column>

         <el-table-column
            prop="gene_id"
            label="Gene Name"
            min-width="160"
            align="center"
            header-align="center"
            >
            <template #default="{ row }">
                <span class="italic-text">{{ row.gene_id || '-' }}</span>
            </template>
            </el-table-column>

            <el-table-column
            prop="organism"
            label="Organism"
            min-width="220"
            align="center"
            header-align="center"
            >
            <template #default="{ row }">
                <span class="italic-text">{{ row.organism || '-' }}</span>
            </template>
            </el-table-column>
        </el-table>
      </div>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          layout="prev, pager, next, jumper"
          :total="filteredTotal"
          :background="false"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Download } from '@element-plus/icons-vue'

const props = defineProps({
  tableData: {
    type: Array,
    default: () => []
  },
  tableLoading: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()

const currentPage = ref(1)
const pageSize = ref(10)
const tableKeyword = ref('')

const handleProteinClick = row => {
  if (!row?.protein_id) return

  sessionStorage.setItem('fromProteinDetail', '1')

  // 保存当前点击的蛋白行数据，供详情页展示更多字段
  sessionStorage.setItem(
    'selectedProteinData',
    JSON.stringify(row)
  )

  router.push({
    path: '/protein/detail',
    query: {
      protein_id: row.protein_id
    }
  })
}

const filteredTableData = computed(() => {
  const keyword = tableKeyword.value.trim().toLowerCase()

  if (!keyword) return props.tableData

  return props.tableData.filter(row =>
    Object.values(row).some(value =>
      String(value ?? '').toLowerCase().includes(keyword)
    )
  )
})

const filteredTotal = computed(() => filteredTableData.value.length)

const pagedTableData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredTableData.value.slice(start, end)
})

watch(tableKeyword, () => {
  currentPage.value = 1
})

watch(pageSize, () => {
  currentPage.value = 1
})

watch(
  () => props.tableData,
  () => {
    currentPage.value = 1
    tableKeyword.value = ''
  }
)

const handleDownload = () => {
  if (!filteredTableData.value.length) return

  const headers = [
    'protein_id_display',
    'organism',
    'gene_id'
  ]

  const csvRows = [
    headers.join(','),
    ...filteredTableData.value.map(row =>
      headers
        .map(key => `"${String(row[key] ?? '').replace(/"/g, '""')}"`)
        .join(',')
    )
  ]

  const blob = new Blob([csvRows.join('\n')], {
    type: 'text/csv;charset=utf-8;'
  })

  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.setAttribute('download', 'protein_gene_info.csv')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  window.URL.revokeObjectURL(url)
}
</script>

<style scoped>
.italic-text {
  font-style: italic;
}

.protein-id-link {
  text-decoration: underline;
  cursor: pointer;
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

.result-panel {
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

.result-inner {
  width: 100%;
  margin-top: 28px;
}

.result-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
  gap: 16px;
}

.result-toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.result-toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 300px;
}

.result-count {
  font-size: 16px;
  color: #303133;
  font-weight: 600;
  white-space: nowrap;
}

.result-count span {
  color: #409eff;
}

.page-size-select {
  width: 120px;
}

.table-search-input {
  width: 260px;
}

.table-wrapper {
  width: 100%;
  overflow-x: auto;
}

.pagination-wrap {
  margin-top: 20px;
  display: flex;
  justify-content: flex-start;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  height: 42px;
  min-height: 42px;
  box-sizing: border-box;
  align-items: center;
}

:deep(.el-input__inner),
:deep(.el-select__placeholder),
:deep(.el-select__selected-item) {
  line-height: 42px;
}

:deep(.el-table th.el-table__cell) {
  background: #f8fbff;
  color: #303133;
  font-weight: 700;
}

:deep(.el-pagination .btn-prev),
:deep(.el-pagination .btn-next),
:deep(.el-pagination .el-pager li) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

:deep(.el-pagination .el-pager li.is-active) {
  background: transparent !important;
  color: #409eff !important;
}

:deep(.el-pagination .el-input__inner) {
  background-color: transparent !important;
  text-align: center;
}

:deep(.el-pagination__jump .el-input) {
  width: 30px;
}

:deep(.el-pagination__jump .el-input__wrapper) {
  min-height: 30px !important;
  height: 30px !important;
  padding: 0 2px !important;
}

:deep(.page-size-dropdown .el-select-dropdown__item.is-selected) {
  background-color: transparent !important;
  color: #409eff !important;
  font-weight: 500;
}

:deep(.page-size-dropdown .el-select-dropdown__item.hover),
:deep(.page-size-dropdown .el-select-dropdown__item:hover) {
  background-color: #f5f7fa !important;
}

@media (max-width: 768px) {
  .result-panel {
    padding-left: 16px;
    padding-right: 16px;
    padding-top: 44px;
    padding-bottom: 20px;
  }

  .panel-tag {
    font-size: 16px;
    padding: 10px 18px;
  }

  .result-toolbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .result-toolbar-left,
  .result-toolbar-right {
    width: 100%;
    align-items: stretch;
  }

  .table-search-input,
  .page-size-select {
    width: 100%;
  }

  .pagination-wrap {
    justify-content: flex-start;
    overflow-x: auto;
  }
}
</style>
