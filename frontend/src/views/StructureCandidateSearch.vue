<template>
  <div class="candidate-page">
    <div class="page-container">
      <section class="panel-card search-card">
        <div class="panel-title">Search</div>

        <el-form
          ref="searchFormRef"
          :model="searchForm"
          label-position="top"
          class="search-form"
        >
          <el-row :gutter="24">
            <!-- Query Species -->
            <el-col :xs="24" :sm="12" :md="8" class="search-col">
              <el-form-item prop="querySpecies" class="search-item species-item">
                <template #label>
                  <span class="required-star">*</span>
                  <span>Query Species</span>
                </template>

                <el-select
                  v-model="searchForm.querySpecies"
                  filterable
                  clearable
                  :loading="speciesLoading"
                  placeholder="Select query species"
                  class="search-control"
                  popper-class="species-select-popper"
                  @change="handleQuerySpeciesChange"
                  @clear="handleQuerySpeciesClear"
                >
                  <el-option
                    v-for="item in speciesOptions"
                    :key="`query-${item.value}`"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>

            <!-- Query Genome Version -->
            <el-col :xs="24" :sm="12" :md="8" class="search-col">
              <el-form-item prop="queryGenomeName" class="search-item genome-item">
                <template #label>
                  <span class="required-star">*</span>
                  <span>Query Genome Version</span>
                </template>

                <el-select
                  v-model="searchForm.queryGenomeName"
                  filterable
                  clearable
                  :disabled="!searchForm.querySpecies"
                  placeholder="Select genome version"
                  class="search-control"
                  popper-class="species-select-popper"
                >
                  <el-option
                    v-for="item in queryGenomeOptions"
                    :key="`query-genome-${item.conservatory_genome_name}`"
                    :label="item.genome_version"
                    :value="item.conservatory_genome_name"
                  />
                </el-select>
              </el-form-item>
            </el-col>

            <!-- Protein ID -->
            <el-col :xs="24" :sm="12" :md="8" class="search-col">
              <el-form-item prop="proteinId" class="required-label search-item protein-item">
                <template #label>
                  <span class="required-star">*</span>
                  <span>Protein ID</span>
                </template>

                <el-input
                  v-model="searchForm.proteinId"
                  clearable
                  placeholder="eg. NP_001310781.1"
                  class="search-control protein-control"
                />
              </el-form-item>
            </el-col>

            <!-- Target Species -->
            <el-col :xs="24" :sm="12" :md="8" class="search-col">
              <el-form-item prop="targetSpecies" class="search-item species-item">
                <template #label>
                  <span class="required-star">*</span>
                  <span>Target Species</span>
                </template>

                <el-select
                  v-model="searchForm.targetSpecies"
                  filterable
                  clearable
                  :loading="speciesLoading"
                  placeholder="Select target species"
                  class="search-control"
                  popper-class="species-select-popper"
                  @change="handleTargetSpeciesChange"
                  @clear="handleTargetSpeciesClear"
                >
                  <el-option
                    v-for="item in speciesOptions"
                    :key="`target-${item.value}`"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>

            <!-- Target Genome Version -->
            <el-col :xs="24" :sm="12" :md="8" class="search-col">
              <el-form-item prop="targetGenomeName" class="search-item genome-item">
                <template #label>
                  <span class="required-star">*</span>
                  <span>Target Genome Version</span>
                </template>

                <el-select
                  v-model="searchForm.targetGenomeName"
                  filterable
                  clearable
                  :disabled="!searchForm.targetSpecies"
                  placeholder="Select genome version"
                  class="search-control"
                  popper-class="species-select-popper"
                >
                  <el-option
                    v-for="item in targetGenomeOptions"
                    :key="`target-genome-${item.conservatory_genome_name}`"
                    :label="item.genome_version"
                    :value="item.conservatory_genome_name"
                  />
                </el-select>
              </el-form-item>
            </el-col>

            <!-- Cosine Similarity Range -->
            <el-col :xs="24" :sm="12" :md="8" class="search-col">
              <el-form-item prop="similarityRange" class="search-item range-item">
                <template #label>
                  <span class="required-star">*</span>
                  <span>Cosine Similarity Range</span>
                  <el-tooltip
                    content="Only positive cosine similarity results are kept. Select a range from 0% to 100%."
                    placement="top"
                    effect="light"
                  >
                    <el-icon class="tip-icon">
                      <QuestionFilled />
                    </el-icon>
                  </el-tooltip>
                </template>

                <div class="range-box">
                  <el-select
                    v-model="searchForm.similarityMin"
                    placeholder="Min"
                    class="range-select"
                    @change="handleSimilarityMinChange"
                  >
                    <el-option
                      v-for="item in similarityOptions"
                      :key="`min-${item}`"
                      :label="`${item}%`"
                      :value="item"
                    />
                  </el-select>

                  <span class="range-to">to</span>

                  <el-select
                    v-model="searchForm.similarityMax"
                    placeholder="Max"
                    class="range-select"
                  >
                    <el-option
                      v-for="item in maxSimilarityOptions"
                      :key="`max-${item}`"
                      :label="`${item}%`"
                      :value="item"
                    />
                  </el-select>
                </div>
              </el-form-item>
            </el-col>
          </el-row>

          <div class="button-row">
            <el-button
              class="search-btn"
              :loading="tableLoading"
              @click="handleSearch"
            >
              Search
            </el-button>

            <el-button class="reset-btn" @click="handleReset">
              Reset
            </el-button>
          </div>
        </el-form>
      </section>

      <section class="panel-card result-card">
        <div class="panel-title">Candidate Proteins</div>

        <div class="table-toolbar">
          <div class="toolbar-left">
            <span class="total-text">
              Total:
              <strong>{{ filteredTableData.length }}</strong>
            </span>

            <el-select
              v-model="pageSize"
              class="page-size-select"
              @change="handlePageSizeChange"
            >
              <el-option :label="'10 / page'" :value="10" />
              <el-option :label="'20 / page'" :value="20" />
              <el-option :label="'50 / page'" :value="50" />
            </el-select>
          </div>

          <div class="toolbar-right">
            <el-input
              v-model="tableKeyword"
              placeholder="Search in table"
              clearable
              class="table-search-input"
            >
              <template #prefix>
                <el-icon>
                  <Search />
                </el-icon>
              </template>
            </el-input>

            <el-tooltip content="Download TSV" placement="top">
              <el-button
                class="download-btn"
                circle
                :disabled="!filteredTableData.length"
                @click="handleDownload"
              >
                <el-icon>
                  <Download />
                </el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </div>

        <el-table
          v-loading="tableLoading"
          element-loading-text="Calculation may take some time. Please wait."
          :data="pagedTableData"
          border
          stripe
          empty-text="No data"
          class="candidate-table"
          :header-cell-style="headerCellStyle"
          :cell-style="bodyCellStyle"
          @sort-change="handleSortChange"
        >
          <el-table-column
            label="Rank"
            width="100"
            align="center"
          >
            <template #default="{ $index }">
              {{ getDisplayIndex($index) }}
            </template>
          </el-table-column>

          <el-table-column
            prop="query_protein_id"
            label="Query Protein ID"
            min-width="180"
            align="center"
          />

          <el-table-column
            prop="query_species"
            label="Query Species"
            min-width="190"
            align="center"
          >
            <template #default="{ row }">
              {{ row.query_species || '-' }}
            </template>
          </el-table-column>

          <el-table-column
            prop="target_protein_id"
            label="Target Protein ID"
            min-width="210"
            align="center"
            sortable="custom"
          />

          <el-table-column
            prop="target_species"
            label="Target Species"
            min-width="190"
            align="center"
          >
            <template #default="{ row }">
              {{ row.target_species || '-' }}
            </template>
          </el-table-column>

          <el-table-column
            prop="cosine_similarity_percent"
            label="TM-score"
            min-width="150"
            align="center"
            sortable="custom"
          >
            <template #default="{ row }">
              <span :class="getSimilarityClass(row)">
                {{ formatNumber(row.cosine_similarity_percent, 4) }}%
              </span>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-row">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="filteredTableData.length"
            layout="prev, pager, next, jumper"
          />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import {
  Search,
  Download,
  QuestionFilled
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const DEFAULT_PROTEIN_ID = 'Glyma_01G000100'

const DEFAULT_QUERY_SPECIES = 'Glycine max'
const DEFAULT_QUERY_GENOME_NAME = 'Glycine_max_Wm82v6'

const DEFAULT_TARGET_SPECIES = 'Oryza sativa'
const DEFAULT_TARGET_GENOME_NAME = 'osa1_r7'

const DEFAULT_SIMILARITY_MIN = 0
const DEFAULT_SIMILARITY_MAX = 100

const searchFormRef = ref(null)

const searchForm = reactive({
  querySpecies: DEFAULT_QUERY_SPECIES,
  queryGenomeName: DEFAULT_QUERY_GENOME_NAME,
  proteinId: DEFAULT_PROTEIN_ID,
  targetSpecies: DEFAULT_TARGET_SPECIES,
  targetGenomeName: DEFAULT_TARGET_GENOME_NAME,
  similarityMin: DEFAULT_SIMILARITY_MIN,
  similarityMax: DEFAULT_SIMILARITY_MAX
})

const speciesGenomeData = ref([])
const speciesOptions = ref([])
const queryGenomeOptions = ref([])
const targetGenomeOptions = ref([])
const speciesLoading = ref(false)

const tableKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const tableLoading = ref(false)
const tableData = ref([])
const resultMeta = ref(null)

const sortState = reactive({
  prop: '',
  order: ''
})

const similarityOptions = Array.from(
  { length: 21 },
  (_, index) => index * 5
)

const maxSimilarityOptions = computed(() => {
  return similarityOptions.filter((item) => item >= searchForm.similarityMin)
})

const filteredTableData = computed(() => {
  const keyword = tableKeyword.value.trim().toLowerCase()

  let data = tableData.value.filter((item) => {
    if (!isPositiveSimilarity(item)) return false

    if (!keyword) return true

    return Object.values(item).some((value) =>
      String(value ?? '').toLowerCase().includes(keyword)
    )
  })

  if (sortState.prop && sortState.order) {
    const direction = sortState.order === 'ascending' ? 1 : -1

    data = [...data].sort((a, b) => {
      const av = a[sortState.prop]
      const bv = b[sortState.prop]

      if (typeof av === 'number' && typeof bv === 'number') {
        return (av - bv) * direction
      }

      return String(av ?? '').localeCompare(String(bv ?? '')) * direction
    })
  }

  return data
})

const pagedTableData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredTableData.value.slice(start, end)
})

watch(tableKeyword, () => {
  currentPage.value = 1
})

const fetchSpeciesOptions = async () => {
  speciesLoading.value = true

  try {
    const res = await request.get('/api/species/names/')
    const rows = res.data.data || []

    speciesGenomeData.value = rows
      .map((speciesItem) => ({
        species: speciesItem.species,
        genome_versions: speciesItem.genome_versions || []
      }))
      .filter((item) => item.species)

    speciesOptions.value = speciesGenomeData.value
      .map((item) => ({
        label: item.species,
        value: item.species
      }))
      .sort((a, b) => a.label.localeCompare(b.label))

    initDefaultGenomes()
  } catch (error) {
    console.error('Failed to fetch species options:', error)
    speciesGenomeData.value = []
    speciesOptions.value = []
    queryGenomeOptions.value = []
    targetGenomeOptions.value = []
    ElMessage.error('Failed to load species options')
  } finally {
    speciesLoading.value = false
  }
}

const findSpeciesItem = (species) => {
  return speciesGenomeData.value.find((item) => item.species === species)
}

const initGenomeForSpecies = ({
  species,
  defaultGenomeName,
  setSpecies,
  setGenomeName,
  setGenomeOptions
}) => {
  const speciesItem = findSpeciesItem(species)

  if (speciesItem) {
    setSpecies(speciesItem.species)
    setGenomeOptions(speciesItem.genome_versions || [])

    const defaultGenome = (speciesItem.genome_versions || []).find(
      (item) => item.conservatory_genome_name === defaultGenomeName
    )

    if (defaultGenome) {
      setGenomeName(defaultGenome.conservatory_genome_name)
      return
    }

    if ((speciesItem.genome_versions || []).length) {
      setGenomeName(speciesItem.genome_versions[0].conservatory_genome_name)
      return
    }
  }

  const firstSpecies = speciesGenomeData.value[0]
  const firstGenome = firstSpecies?.genome_versions?.[0]

  if (firstSpecies && firstGenome) {
    setSpecies(firstSpecies.species)
    setGenomeOptions(firstSpecies.genome_versions || [])
    setGenomeName(firstGenome.conservatory_genome_name)
  }
}

const initDefaultGenomes = () => {
  initGenomeForSpecies({
    species: DEFAULT_QUERY_SPECIES,
    defaultGenomeName: DEFAULT_QUERY_GENOME_NAME,
    setSpecies: (value) => {
      searchForm.querySpecies = value
    },
    setGenomeName: (value) => {
      searchForm.queryGenomeName = value
    },
    setGenomeOptions: (value) => {
      queryGenomeOptions.value = value
    }
  })

  initGenomeForSpecies({
    species: DEFAULT_TARGET_SPECIES,
    defaultGenomeName: DEFAULT_TARGET_GENOME_NAME,
    setSpecies: (value) => {
      searchForm.targetSpecies = value
    },
    setGenomeName: (value) => {
      searchForm.targetGenomeName = value
    },
    setGenomeOptions: (value) => {
      targetGenomeOptions.value = value
    }
  })
}

const handleQuerySpeciesChange = (species) => {
  searchForm.queryGenomeName = ''
  resultMeta.value = null
  tableData.value = []
  currentPage.value = 1

  if (!species) {
    queryGenomeOptions.value = []
    return
  }

  const matchedSpecies = findSpeciesItem(species)
  queryGenomeOptions.value = matchedSpecies?.genome_versions || []

  if (queryGenomeOptions.value.length === 1) {
    searchForm.queryGenomeName =
      queryGenomeOptions.value[0].conservatory_genome_name
  }
}

const handleQuerySpeciesClear = () => {
  searchForm.querySpecies = ''
  searchForm.queryGenomeName = ''
  queryGenomeOptions.value = []
  resultMeta.value = null
  tableData.value = []
  currentPage.value = 1
}

const handleTargetSpeciesChange = (species) => {
  searchForm.targetGenomeName = ''
  resultMeta.value = null
  tableData.value = []
  currentPage.value = 1

  if (!species) {
    targetGenomeOptions.value = []
    return
  }

  const matchedSpecies = findSpeciesItem(species)
  targetGenomeOptions.value = matchedSpecies?.genome_versions || []

  if (targetGenomeOptions.value.length === 1) {
    searchForm.targetGenomeName =
      targetGenomeOptions.value[0].conservatory_genome_name
  }
}

const handleTargetSpeciesClear = () => {
  searchForm.targetSpecies = ''
  searchForm.targetGenomeName = ''
  targetGenomeOptions.value = []
  resultMeta.value = null
  tableData.value = []
  currentPage.value = 1
}

const validateSearchForm = () => {
  if (!searchForm.querySpecies) {
    ElMessage.warning('Please select a query species.')
    return false
  }

  if (!searchForm.queryGenomeName) {
    ElMessage.warning('Please select a query genome version.')
    return false
  }

  if (!searchForm.proteinId.trim()) {
    ElMessage.warning('Please enter a protein ID.')
    return false
  }

  if (!searchForm.targetSpecies) {
    ElMessage.warning('Please select a target species.')
    return false
  }

  if (!searchForm.targetGenomeName) {
    ElMessage.warning('Please select a target genome version.')
    return false
  }

  if (searchForm.similarityMin < 0 || searchForm.similarityMax > 100) {
    ElMessage.warning('Similarity range must be between 0% and 100%.')
    return false
  }

  if (searchForm.similarityMin > searchForm.similarityMax) {
    ElMessage.warning('Minimum similarity cannot be greater than maximum similarity.')
    return false
  }

  return true
}

const handleSearch = async () => {
  if (!validateSearchForm()) return

  try {
    tableLoading.value = true
    ElMessage.info('Search request submitted. Calculation may take some time.')

    const res = await request.get('/search/protein-embedding/', {
      params: {
        protein_id: searchForm.proteinId.trim(),

        // query_species 后端接收 conservatory_genome_name
        query_species: searchForm.queryGenomeName,

        // target_species 后端接收 conservatory_genome_name
        target_species: searchForm.targetGenomeName,

        similarity_min: searchForm.similarityMin,
        similarity_max: searchForm.similarityMax
      }
    })

    tableData.value = (res.data.data || []).filter(isPositiveSimilarity)
    resultMeta.value = res.data.meta || null
    tableKeyword.value = ''
    currentPage.value = 1
    sortState.prop = ''
    sortState.order = ''

    ElMessage.success(`Search completed. ${tableData.value.length} hits.`)
  } catch (error) {
    console.error('protein embedding search failed:', error)
    console.error('response data:', error?.response?.data)
    console.error('response status:', error?.response?.status)

    tableData.value = []
    resultMeta.value = null
    currentPage.value = 1

    ElMessage.error(error?.response?.data?.message || 'Search failed')
  } finally {
    tableLoading.value = false
  }
}

const handleReset = () => {
  searchForm.querySpecies = ''
  searchForm.queryGenomeName = ''
  searchForm.proteinId = ''
  searchForm.targetSpecies = ''
  searchForm.targetGenomeName = ''
  searchForm.similarityMin = DEFAULT_SIMILARITY_MIN
  searchForm.similarityMax = DEFAULT_SIMILARITY_MAX

  queryGenomeOptions.value = []
  targetGenomeOptions.value = []
  tableKeyword.value = ''
  currentPage.value = 1
  sortState.prop = ''
  sortState.order = ''
  tableData.value = []
  resultMeta.value = null
}

const handlePageSizeChange = () => {
  currentPage.value = 1
}

const handleSimilarityMinChange = () => {
  if (searchForm.similarityMax < searchForm.similarityMin) {
    searchForm.similarityMax = searchForm.similarityMin
  }
}

const handleSortChange = ({ prop, order }) => {
  sortState.prop = prop
  sortState.order = order
  currentPage.value = 1
}

const getDisplayIndex = (index) => {
  return (currentPage.value - 1) * pageSize.value + index + 1
}

const escapeTsvValue = (value) => {
  return String(value ?? '').replace(/[\t\r\n]+/g, ' ')
}

const formatNumber = (value, digits = 4) => {
  const number = Number(value)

  if (!Number.isFinite(number)) {
    return ''
  }

  return number.toFixed(digits)
}

const isPositiveSimilarity = (item) => {
  const score = Number(item?.cosine_similarity)

  if (Number.isFinite(score)) {
    return score > 1e-7
  }

  const percent = Number(item?.cosine_similarity_percent)
  return Number.isFinite(percent) && percent > 0.00001
}

const getSimilarityClass = (item) => {
  const percent = Number(item?.cosine_similarity_percent)
  const score = Number(item?.cosine_similarity)
  const number = Number.isFinite(percent) ? percent : score * 100

  if (!Number.isFinite(number)) {
    return ''
  }

  if (number < 50) return 'similarity-warning'
  if (number > 0.00001) return 'similarity-positive'
  return 'similarity-non-positive'
}

const handleDownload = () => {
  if (!filteredTableData.value.length) return

  const header = [
    'rank',
    'query_species',
    'query_genome_version',
    'query_species_id',
    'query_protein_id',
    'target_species',
    'target_genome_version',
    'target_species_id',
    'target_protein_id',
    'cosine_similarity_percent'
  ]

  const rows = filteredTableData.value.map((item) => [
    item.rank,
    item.query_species,
    item.query_genome_version,
    item.query_species_id,
    item.query_protein_id,
    item.target_species,
    item.target_genome_version,
    item.target_species_id,
    item.target_protein_id,
    item.cosine_similarity_percent
  ])

  const tsvContent = [header, ...rows]
    .map((row) => row.map(escapeTsvValue).join('\t'))
    .join('\n')

  const blob = new Blob([tsvContent], {
    type: 'text/tab-separated-values;charset=utf-8;'
  })

  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  const proteinId = searchForm.proteinId.trim() || 'protein'
  const queryGenomeName = searchForm.queryGenomeName || 'query'
  const targetGenomeName = searchForm.targetGenomeName || 'target'

  link.href = url
  link.download = `${proteinId}_${queryGenomeName}_vs_${targetGenomeName}.tsv`
  link.click()

  URL.revokeObjectURL(url)
}

const headerCellStyle = () => {
  return {
    background: '#f5f8fc',
    color: '#404b5a',
    fontWeight: 600,
    height: '44px'
  }
}

const bodyCellStyle = () => {
  return {
    color: '#526070',
    height: '44px'
  }
}

onMounted(() => {
  fetchSpeciesOptions()
})
</script>

<style scoped>
.candidate-page {
  width: 100%;
  padding: 24px;
  background: #f7fbff;
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
  background: #ffffff;
  border: 1px solid #dfe7f0;
  border-radius: 6px;
  box-shadow: 0 4px 14px rgba(55, 80, 110, 0.12);
  box-sizing: border-box;
}

.search-card {
  padding: 92px 40px 46px;
  margin-bottom: 28px;
  min-height: 270px;
}

.result-card {
  padding: 58px 30px 28px;
}

.panel-title {
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

.panel-title::before {
  content: '';
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
}

.search-col {
  display: flex;
  justify-content: center;
}

.search-control {
  width: 100%;
  max-width: 320px;
}

.protein-control {
  max-width: 320px;
}

.search-item {
  align-items: center;
  width: 100%;
  max-width: 320px;
}

.required-star {
  color: #ff4d4f;
  margin-right: 4px;
}

.tip-icon {
  margin-left: 6px;
  color: #9aa7b7;
  cursor: pointer;
  transform: translateY(2px);
}

.range-box {
  display: flex;
  align-items: center;
  width: 100%;
  max-width: 320px;
}

.range-select {
  flex: 1;
  min-width: 0;
}

.range-to {
  width: 32px;
  text-align: center;
  color: #566271;
}

.button-row {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 16px;
}

.search-btn {
  width: 112px;
  height: 38px;
  color: #2f86ff;
  border-color: #acd1ff;
  background: #f2f7ff;
}

.search-btn:hover {
  color: #ffffff;
  background: #409eff;
  border-color: #409eff;
}

.reset-btn {
  width: 98px;
  height: 38px;
  color: #f56c6c;
  border-color: #ffb8b8;
  background: #fff7f7;
}

.reset-btn:hover {
  color: #ffffff;
  background: #f56c6c;
  border-color: #f56c6c;
}

.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
  gap: 16px;
  margin-top: 28px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toolbar-left {
  flex-wrap: wrap;
}

.total-text {
  font-size: 17px;
  color: #202936;
  font-weight: 600;
}

.total-text strong {
  color: #2f86ff;
}

.page-size-select {
  width: 118px;
}

.table-search-input {
  width: 260px;
}

.download-btn {
  color: #409eff;
  border-color: #acd1ff;
  background: #f7fbff;
}

.download-btn:hover {
  color: #ffffff;
  background: #409eff;
  border-color: #409eff;
}

.candidate-table {
  width: 100%;
  font-size: 14px;
}

.similarity-positive {
  color: #2f8f46;
  font-weight: 600;
}

.similarity-warning {
  color: #d48806;
  font-weight: 600;
}

.similarity-non-positive {
  color: #6f7782;
  font-weight: 600;
}

.pagination-row {
  display: flex;
  justify-content: flex-start;
  margin-top: 22px;
}

:deep(.el-form-item__label) {
  color: #252c36;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 8px;
}

.search-item :deep(.el-form-item__label) {
  justify-content: flex-start;
  text-align: left;
  width: 100%;
  margin-right: auto;
  margin-left: auto;
}

.protein-item :deep(.el-form-item__label),
.species-item :deep(.el-form-item__label),
.genome-item :deep(.el-form-item__label),
.range-item :deep(.el-form-item__label) {
  max-width: 320px;
}

.search-item :deep(.el-form-item__content) {
  justify-content: center;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  min-height: 38px;
  border-radius: 4px;
  box-shadow: 0 0 0 1px #dce4ef inset;
}

:deep(.el-input__wrapper:hover),
:deep(.el-select__wrapper:hover) {
  box-shadow: 0 0 0 1px #b8d7ff inset;
}

:deep(.el-table) {
  border-radius: 2px;
  overflow: hidden;
}

:deep(.el-table__cell) {
  border-color: #e7edf5 !important;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: #fafafa;
}

.pagination-row :deep(.el-pagination button),
.pagination-row :deep(.el-pager li),
.pagination-row :deep(.el-pager li.is-active) {
  background: transparent;
  border: none;
  box-shadow: none;
}

.pagination-row :deep(.el-pagination .el-input__inner) {
  background-color: transparent !important;
  text-align: center;
}

.pagination-row :deep(.el-pagination__jump .el-input) {
  width: 30px;
}

.pagination-row :deep(.el-pagination__jump .el-input__wrapper) {
  min-height: 30px !important;
  height: 30px !important;
  padding: 0 2px !important;
}

@media (max-width: 1200px) {
  .search-control,
  .protein-control,
  .range-box {
    max-width: 300px;
  }

  .protein-item :deep(.el-form-item__label),
  .species-item :deep(.el-form-item__label),
  .genome-item :deep(.el-form-item__label),
  .range-item :deep(.el-form-item__label) {
    max-width: 300px;
  }
}

@media (max-width: 768px) {
  .candidate-page {
    padding: 16px;
  }

  .search-card {
    padding: 78px 24px 36px;
  }

  .result-card {
    padding: 58px 18px 24px;
  }

  .table-toolbar {
    align-items: flex-start;
    flex-direction: column;
    gap: 14px;
  }

  .toolbar-right {
    width: 100%;
  }

  .table-search-input {
    width: 100%;
  }
}

@media (max-width: 576px) {
  .button-row {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .search-btn,
  .reset-btn {
    width: 100%;
  }

  .range-box {
    gap: 8px;
    max-width: none;
  }

  .range-select {
    width: calc((100% - 34px) / 2);
  }

  .search-control {
    max-width: none;
  }

  .range-to {
    width: 26px;
  }

  .toolbar-left,
  .toolbar-right {
    flex-wrap: wrap;
  }
}
</style>
