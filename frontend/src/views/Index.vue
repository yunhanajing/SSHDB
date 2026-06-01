<template>
  <div class="search-page">
    <div class="page-container">
      <!-- Search Panel -->
      <div class="panel-card form-panel">
        <div class="panel-tag">Search</div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          class="search-form"
        >
          <div class="form-grid">
            <!-- Gene -->
            <el-form-item label="Gene" prop="gene" class="grid-item">
              <el-select
                v-model="form.gene"
                class="italic-select"
                placeholder="eg. ACP"
                multiple
                collapse-tags
                :max-collapse-tags="2"
                collapse-tags-tooltip
                clearable
                filterable
                style="width: 100%"
                :loading="geneLoading"
                :teleported="false"
                popper-class="gene-select-popper page-size-dropdown"
              >
                <el-option
                  v-for="item in geneOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>

            <!-- Species：单选，必选 -->
            <el-form-item label="Species" prop="species" class="grid-item">
              <el-select
                v-model="form.species"
                class="italic-select"
                placeholder="eg. Arabidopsis thaliana"
                clearable
                filterable
                style="width: 100%"
                :teleported="false"
                popper-class="gene-select-popper"
                @change="handleSpeciesChange"
                @clear="handleSpeciesClear"
              >
                <el-option
                  v-for="item in speciesOptions"
                  :key="item"
                  :label="item"
                  :value="item"
                />
              </el-select>
            </el-form-item>

            <!-- Genome Version：根据 Species 联动，必选 -->
            <el-form-item
              label="Genome Version"
              prop="conservatory_genome_name"
              class="grid-item"
            >
              <el-select
                v-model="form.conservatory_genome_name"
                placeholder="Select genome version"
                clearable
                filterable
                style="width: 100%"
                :disabled="!form.species"
                :teleported="false"
                popper-class="gene-select-popper"
              >
                <el-option
                  v-for="item in genomeVersionOptions"
                  :key="item.conservatory_genome_name"
                  :label="`${item.genome_version} (${item.conservatory_genome_name})`"
                  :value="item.conservatory_genome_name"
                />
              </el-select>
            </el-form-item>

            <!-- Category -->
            <el-form-item prop="category" class="grid-item optional-item">
              <template #label>
                <span class="label-with-icon">
                  <el-tooltip placement="top" effect="light">
                    <template #content>
                      <div class="category-tooltip">
                        <div><strong>A:</strong> TM-score ≥ 50 and sequence similarity ≥ 50</div>
                        <div><strong>B:</strong> TM-score ≥ 50 and 30 ≤ sequence similarity &lt; 50</div>
                        <div><strong>C:</strong> TM-score ≥ 50 and sequence similarity &lt; 30</div>
                      </div>
                    </template>

                    <el-icon class="info-icon">
                      <QuestionFilled />
                    </el-icon>
                  </el-tooltip>

                  <span>Category</span>
                  <span class="optional-text">(Optional)</span>
                </span>
              </template>

              <el-select
                v-model="form.category"
                placeholder="eg. A"
                clearable
                style="width: 100%"
                multiple
              >
                <el-option
                  v-for="item in categoryOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </div>

          <div class="form-actions">
            <el-button type="primary" plain @click="handleSubmit">Search</el-button>
            <el-button type="danger"  plain @click="handleReset">Reset</el-button>
          </div>
        </el-form>
      </div>

      <!-- Result Panel -->
      <div class="panel-card result-panel">
        <div class="panel-tag">Result</div>

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
                <el-option :value="50" label="50 / page" />
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
                @click="handleDownload"
                :disabled="!filteredTableData.length"
                aria-label="Download"
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
              prop="query_protein_name"
              label="Query Protein Name"
              min-width="240"
              align="center"
              header-align="center"
            />

            <el-table-column
              prop="hit_protein_name"
              label="Hit Protein Name"
              min-width="240"
              align="center"
              header-align="center"
            />

            <el-table-column
              prop="tm_score"
              label="TM-score"
              sortable
              width="150"
              align="center"
              header-align="center"
            >
              <template #default="{ row }">
                <span :class="getTmScoreClass(row.tm_score)">
                  {{ row.tm_score }}
                </span>
              </template>
            </el-table-column>

            <el-table-column
              prop="sequence_similarity"
              label="Sequence Similarity"
              sortable
              width="200"
              align="center"
              header-align="center"
            >
              <template #default="{ row }">
                <span :class="getSequenceSimilarityClass(row)">
                  {{ row.sequence_similarity }}
                </span>
              </template>
            </el-table-column>

            <el-table-column
              prop="query_protein_length"
              label="Query Protein Length"
              width="200"
              align="center"
              header-align="center"
            />

            <el-table-column
              prop="hit_protein_length"
              label="Hit Protein Length"
              width="200"
              align="center"
              header-align="center"
            /> 
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
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { QuestionFilled, Search, Download } from '@element-plus/icons-vue'
import request from '@/utils/request'

const formRef = ref()
const route = useRoute()

const DEFAULT_GENE = 'ACP'
const DEFAULT_SPECIES = 'Arabidopsis thaliana'
const DEFAULT_CONSERVATORY_GENOME_NAME = 'Athaliana'

const form = reactive({
  gene: [DEFAULT_GENE],
  species: DEFAULT_SPECIES,
  conservatory_genome_name: DEFAULT_CONSERVATORY_GENOME_NAME,
  category: []
})

const geneOptions = ref([])
const geneLoading = ref(false)

const speciesGenomeData = ref([])
const speciesOptions = ref([])
const genomeVersionOptions = ref([])

const categoryOptions = [
  { label: 'A  (sequence similarity ≥ 50)', value: 'A' },
  { label: 'B  (30 ≤ sequence similarity < 50)', value: 'B' },
  { label: 'C  (sequence similarity < 30)', value: 'C' }
]

const tableData = ref([])
const tableLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const tableKeyword = ref('')

const rules = {
  gene: [
    {
      required: true,
      type: 'array',
      min: 1,
      message: 'Please select gene',
      trigger: 'change'
    }
  ],
  species: [
    {
      required: true,
      message: 'Please select species',
      trigger: 'change'
    }
  ],
  conservatory_genome_name: [
    {
      required: true,
      message: 'Please select genome version',
      trigger: 'change'
    }
  ]
}

const filteredTableData = computed(() => {
  const keyword = tableKeyword.value.trim().toLowerCase()

  if (!keyword) return tableData.value

  return tableData.value.filter(row =>
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

const fetchGeneOptions = async () => {
  geneLoading.value = true

  try {
    const res = await request.get('/api/genes/unique/')
    geneOptions.value = (res.data.data || []).map(item => ({
      label: item,
      value: item
    }))
  } catch (error) {
    console.error('Failed to fetch gene options:', error)
    geneOptions.value = []
  } finally {
    geneLoading.value = false
  }
}

const fetchSpeciesOptions = async () => {
  try {
    const res = await request.get('/api/species/names/')
    speciesGenomeData.value = res.data.data || []

    speciesOptions.value = speciesGenomeData.value
      .map(item => item.species)
      .filter(Boolean)
      .sort((a, b) => a.localeCompare(b))
  } catch (error) {
    console.error('Failed to fetch species options:', error)
    speciesGenomeData.value = []
    speciesOptions.value = []
    genomeVersionOptions.value = []
  }
}

const handleSpeciesChange = species => {
  form.conservatory_genome_name = ''

  if (!species) {
    genomeVersionOptions.value = []
    return
  }

  const matchedSpecies = speciesGenomeData.value.find(
    item => item.species === species
  )

  genomeVersionOptions.value = matchedSpecies?.genome_versions || []

  if (species === DEFAULT_SPECIES) {
    const defaultGenome = genomeVersionOptions.value.find(
      item => item.conservatory_genome_name === DEFAULT_CONSERVATORY_GENOME_NAME
    )

    if (defaultGenome) {
      form.conservatory_genome_name = DEFAULT_CONSERVATORY_GENOME_NAME
      return
    }
  }

  if (genomeVersionOptions.value.length === 1) {
    form.conservatory_genome_name =
      genomeVersionOptions.value[0].conservatory_genome_name
  }
}

const selectSpeciesFromRoute = () => {
  const routeSpecies = Array.isArray(route.query.species)
    ? route.query.species[0]
    : route.query.species

  if (!routeSpecies) return false

  const matchedSpecies = speciesOptions.value.find(
    item => item.toLowerCase() === String(routeSpecies).toLowerCase()
  )

  if (!matchedSpecies) {
    ElMessage.warning(`Species "${routeSpecies}" not found`)
    return false
  }

  form.species = matchedSpecies
  handleSpeciesChange(matchedSpecies)

  if (!form.conservatory_genome_name && genomeVersionOptions.value.length) {
    form.conservatory_genome_name =
      genomeVersionOptions.value[0].conservatory_genome_name
  }

  return true
}

const handleSpeciesClear = () => {
  form.species = ''
  form.conservatory_genome_name = ''
  genomeVersionOptions.value = []
}

const formatQueryProteinName = value => {
  if (!value) return value

  let name = String(value).trim()

  // 只保留 __ 后面的内容
  if (name.includes('__')) {
    name = name.split('__')[1]
  }

  // 最后加 .p，避免重复加成 .p.p
  if (!name.endsWith('.p')) {
    name = `${name}.p`
  }

  return name
}

const getTmScoreClass = value => {
  const number = parseScoreValue(value)

  if (!Number.isFinite(number)) {
    return ''
  }

  return number < 50 ? 'similarity-warning' : 'similarity-positive'
}

const parseScoreValue = value => {
  return parseFloat(String(value ?? '').replace('%', ''))
}

const getSequenceSimilarityClass = row => {
  const tmScore = parseScoreValue(row?.tm_score)
  const sequenceSimilarity = parseScoreValue(row?.sequence_similarity)

  if (!Number.isFinite(tmScore) || !Number.isFinite(sequenceSimilarity)) {
    return ''
  }

  if (tmScore < 50) {
    return ''
  }

  if (sequenceSimilarity >= 50) return 'similarity-positive'
  if (sequenceSimilarity >= 30) return 'similarity-warning'
  return 'similarity-danger'
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch (error) {
    ElMessage.warning('Please select gene, species and genome version')
    return
  }

  try {
    tableLoading.value = true

    const params = new URLSearchParams()

    form.gene.forEach(item => {
      params.append('gene', item)
    })

    params.append('species', form.species)
    params.append('conservatory_genome_name', form.conservatory_genome_name)

    form.category.forEach(item => {
      params.append('category', item)
    })

    const res = await request.get(
      '/api/search/results/',
      { params }
    )

    tableData.value = (res.data.data || []).map(row => ({
      ...row,
      query_protein_name: formatQueryProteinName(row.query_protein_name)
    }))

    currentPage.value = 1
    tableKeyword.value = ''
  } catch (error) {
    console.error('search failed:', error)
    console.error('response data:', error?.response?.data)
    console.error('response status:', error?.response?.status)

    tableData.value = []
    currentPage.value = 1
    ElMessage.error(error?.response?.data?.message || 'Search failed')
  } finally {
    tableLoading.value = false
  }
}

const handleReset = () => {
  if (!formRef.value) return

  formRef.value.resetFields()

  form.gene = []
  form.species = ''
  form.conservatory_genome_name = ''
  form.category = []

  genomeVersionOptions.value = []

  tableKeyword.value = ''
  tableData.value = []
  currentPage.value = 1
}

const handleDownload = () => {
  if (!filteredTableData.value.length) return
  
  const headers = [
    'query_protein_name',
    'hit_protein_name',
    'tm_score',
    'sequence_similarity',
    'query_protein_length',
    'hit_protein_length'
  ]

  const csvRows = [
    headers.join(','),
    ...filteredTableData.value.map(row =>
      headers.map(key => `"${String(row[key] ?? '').replace(/"/g, '""')}"`).join(',')
    )
  ]

  const blob = new Blob([csvRows.join('\n')], {
    type: 'text/csv;charset=utf-8;'
  })

  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.setAttribute('download', 'search_result.csv')
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  window.URL.revokeObjectURL(url)
}

onMounted(async () => {
  await Promise.all([
    fetchGeneOptions(),
    fetchSpeciesOptions()
  ])

  const geneExists = geneOptions.value.some(item => item.value === DEFAULT_GENE)
  const routeSpeciesSelected = selectSpeciesFromRoute()
  const speciesExists = speciesOptions.value.includes(DEFAULT_SPECIES)

  if (!geneExists) {
    form.gene = []
    ElMessage.warning(`Default gene "${DEFAULT_GENE}" not found`)
  }

  if (routeSpeciesSelected) {
    // Species and genome version have already been initialized from the route.
  } else if (!speciesExists) {
    form.species = ''
    form.conservatory_genome_name = ''
    genomeVersionOptions.value = []
    ElMessage.warning(`Default species "${DEFAULT_SPECIES}" not found`)
  } else {
    handleSpeciesChange(form.species)

    const defaultGenomeExists = genomeVersionOptions.value.some(
      item => item.conservatory_genome_name === DEFAULT_CONSERVATORY_GENOME_NAME
    )

    if (!defaultGenomeExists) {
      form.conservatory_genome_name = ''
      ElMessage.warning(
        `Default genome version "${DEFAULT_CONSERVATORY_GENOME_NAME}" not found`
      )
    }
  }

  if (form.gene.length && form.species && form.conservatory_genome_name) {
    await handleSubmit()
  }
})
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

.panel-card {
  position: relative;
  width: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  background: #fff;
  box-sizing: border-box;
}

.form-panel {
  min-height: 340px;
  padding: 48px 28px 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.result-panel {
  margin-top: 28px;
  padding: 48px 28px 28px;
}

.italic-option {
  font-style: italic;
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

.search-form {
  width: 100%;
  max-width: 1300px;
  margin: 0 auto;
}

.form-grid {
  display: flex;
  justify-content: center;
  gap: 50px;
  flex-wrap: nowrap;
}

.grid-item {
  width: 300px;
  flex: 0 0 300px;
  margin-bottom: 0;
}

.form-actions {
  margin-top: 28px;
  display: flex;
  justify-content: center;
  gap: 14px;
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

.similarity-positive {
  color: #2f8f46;
  font-weight: 600;
}

.similarity-warning {
  color: #d48806;
  font-weight: 600;
}

.similarity-danger {
  color: #d93025;
  font-weight: 600;
}

.pagination-wrap {
  margin-top: 20px;
  display: flex;
  justify-content: flex-start;
}

.label-with-icon {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.optional-text {
  color: #909399;
  font-weight: normal;
}

.info-icon {
  font-size: 14px;
  color: #909399;
  cursor: pointer;
  transform: translateY(-1px);
}

.info-icon:hover {
  color: #409eff;
}

:deep(.el-form-item__label) {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  height: 42px;
  min-height: 42px;
  box-sizing: border-box;
  align-items: center;
}
:deep(.italic-select .el-select__selected-item),
:deep(.italic-select .el-select__placeholder),
:deep(.italic-select .el-tag__content) {
  font-style: italic;
}
:deep(.el-input__inner),
:deep(.el-select__placeholder),
:deep(.el-select__selected-item) {
  line-height: 42px;
}

:deep(.gene-select-popper .el-select-dropdown__wrap) {
  max-height: 135px;
}

:deep(.el-table th.el-table__cell) {
  background: #f8fbff;
  color: #606266;
  font-weight: 700;
}

/* 去掉分页按钮背景 */
:deep(.el-pagination .btn-prev),
:deep(.el-pagination .btn-next),
:deep(.el-pagination .el-pager li) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

/* 当前页不要浅蓝底，只保留蓝字 */
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

/* page size 下拉选中项去浅蓝色背景 */
:deep(.page-size-dropdown .el-select-dropdown__item.is-selected) {
  background-color: transparent !important;
  color: #409eff !important;
  font-weight: 500;
}

:deep(.page-size-dropdown .el-select-dropdown__item.hover),
:deep(.page-size-dropdown .el-select-dropdown__item:hover) {
  background-color: #f5f7fa !important;
}

@media (max-width: 1200px) {
  .form-grid {
    flex-wrap: wrap;
    justify-content: flex-start;
    gap: 24px;
  }

  .grid-item {
    width: calc(50% - 12px);
    flex: 0 0 calc(50% - 12px);
  }
}

@media (max-width: 768px) {
  .search-page {
    padding: 16px;
  }

  .form-panel,
  .result-panel {
    padding-left: 16px;
    padding-right: 16px;
  }

  .form-panel {
    padding-top: 44px;
    padding-bottom: 20px;
  }

  .result-panel {
    padding-top: 44px;
    padding-bottom: 20px;
  }

  .panel-tag {
    font-size: 16px;
    padding: 10px 18px;
  }

  .form-grid {
    flex-direction: column;
  }

  .grid-item {
    width: 100%;
    flex: 0 0 100%;
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
