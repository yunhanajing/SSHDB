<template>
  <div class="download-page">
    <div class="page-container">
      <section class="panel-card filter-panel">
        <div class="panel-tag">Summary</div>
        <section class="summary-grid" aria-label="Download summary">
          <article class="summary-card">
            <el-icon><FolderOpened /></el-icon>
            <div>
              <span>Genome resources</span>
              <strong>300+</strong>
            </div>
          </article>
          <article class="summary-card">
            <el-icon><FolderOpened /></el-icon>
            <div>
              <span>CIF models</span>
              <strong>840 +</strong>
            </div>
          </article>
          <article class="summary-card">
            <el-icon><FolderOpened /></el-icon>
            <div>
              <span>Npy files</span>
              <strong>{{ npyFiles.length }}</strong>
            </div>
          </article>
          <article class="summary-card">
            <el-icon><FolderOpened /></el-icon>
            <div>
              <span>Homology results</span>
              <strong>{{ homologyFiles.length }}</strong>
            </div>
          </article>

          <article class="summary-card">
            <el-icon><FolderOpened /></el-icon>
            <div>
              <span>SNF-related Genes</span>
              <strong>{{ snfFiles.length }}</strong>
            </div>
          </article>
        </section>
      </section>

      <section class="panel-card data-panel">
        <div class="panel-tag">Files</div>

        <el-tabs v-model="activeTab" class="download-tabs">
          <el-tab-pane label="Genome Resources" name="genome">
            <div class="table-toolbar">
              <div class="genome-toolbar-left">
                <div class="result-count">
                  Total: <span>{{ filteredGenomeFiles.length }}</span>
                </div>

                <el-select
                  v-model="genomePageSize"
                  class="page-size-select"
                  popper-class="page-size-dropdown"
                >
                  <el-option :value="10" label="10 / page" />
                  <el-option :value="20" label="20 / page" />
                  <el-option :value="50" label="50 / page" />
                  <el-option :value="100" label="100 / page" />
                </el-select>
              </div>

              <div class="genome-toolbar-right">
                <el-input
                  v-model="genomeFilters.species"
                  clearable
                  placeholder="Search species"
                  class="genome-search-input"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>

                <el-input
                  v-model="genomeFilters.genomeVersion"
                  clearable
                  placeholder="Search genome version"
                  class="genome-search-input"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>

                <el-button
                  type="primary"
                  plain
                  class="download-filtered-button"
                  :disabled="!filteredGenomeFiles.length"
                  @click="downloadFiles(filteredGenomeFiles)"
                >
                  Download filtered
                </el-button>
              </div>
            </div>

            <resource-table
              v-loading="genomeLoading"
              :files="pagedGenomeFiles"
              empty-text="No genome files are configured yet"
            />

            <div class="pagination-wrap">
              <el-pagination
                v-model:current-page="genomeCurrentPage"
                :page-size="genomePageSize"
                layout="prev, pager, next, jumper"
                :total="filteredGenomeFiles.length"
                :background="false"
              />
            </div>
          </el-tab-pane>

          <el-tab-pane label="Structure CIF Files" name="cif">
            <div class="table-toolbar">
              <div class="genome-toolbar-left">
                <div class="result-count">
                  Total: <span>{{ filteredCifFiles.length }}</span>
                </div>

                <el-select
                  v-model="cifPageSize"
                  class="page-size-select"
                  popper-class="page-size-dropdown"
                >
                  <el-option :value="10" label="10 / page" />
                  <el-option :value="20" label="20 / page" />
                  <el-option :value="50" label="50 / page" />
                  <el-option :value="100" label="100 / page" />
                </el-select>
              </div>

              <div class="genome-toolbar-right">
                <el-input
                  v-model="cifFilters.proteinId"
                  clearable
                  placeholder="Search protein ID"
                  class="genome-search-input"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>

                <el-button
                  type="primary"
                  plain
                  class="download-filtered-button"
                  :disabled="!filteredCifFiles.length"
                  @click="downloadFiles(filteredCifFiles)"
                >
                  Download filtered
                </el-button>
              </div>
            </div>

            <cif-resource-table
              v-loading="cifLoading"
              :files="pagedCifFiles"
              empty-text="No CIF files found"
            />

            <div class="pagination-wrap">
              <el-pagination
                v-model:current-page="cifCurrentPage"
                :page-size="cifPageSize"
                layout="prev, pager, next, jumper"
                :total="filteredCifFiles.length"
                :background="false"
              />
            </div>
          </el-tab-pane>

          <el-tab-pane label="Npy files" name="npy">
            <div class="table-toolbar">
              <div class="genome-toolbar-left">
                <div class="result-count">
                  Total: <span>{{ filteredNpyFiles.length }}</span>
                </div>

                <el-select
                  v-model="npyPageSize"
                  class="page-size-select"
                  popper-class="page-size-dropdown"
                >
                  <el-option :value="10" label="10 / page" />
                  <el-option :value="20" label="20 / page" />
                  <el-option :value="50" label="50 / page" />
                  <el-option :value="100" label="100 / page" />
                </el-select>
              </div>

              <div class="genome-toolbar-right">
                <el-input
                  v-model="npyFilters.species"
                  clearable
                  placeholder="Search species"
                  class="genome-search-input"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>

                <el-input
                  v-model="npyFilters.genomeVersion"
                  clearable
                  placeholder="Search genome version"
                  class="genome-search-input"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>

                <el-button
                  type="primary"
                  plain
                  class="download-filtered-button"
                  :disabled="!filteredNpyFiles.length"
                  @click="downloadFiles(filteredNpyFiles)"
                >
                  Download filtered
                </el-button>
              </div>
            </div>

            <npy-resource-table
              v-loading="npyLoading"
              :files="pagedNpyFiles"
              empty-text="No NPY files are configured yet"
            />

            <div class="pagination-wrap">
              <el-pagination
                v-model:current-page="npyCurrentPage"
                :page-size="npyPageSize"
                layout="prev, pager, next, jumper"
                :total="filteredNpyFiles.length"
                :background="false"
              />
            </div>
          </el-tab-pane>

          <el-tab-pane label="Homology results" name="homology">
            <div class="table-toolbar">
              <div class="genome-toolbar-left">
                <div class="result-count">
                  Total: <span>{{ filteredHomologyFiles.length }}</span>
                </div>

                <el-select
                  v-model="homologyPageSize"
                  class="page-size-select"
                  popper-class="page-size-dropdown"
                >
                  <el-option :value="10" label="10 / page" />
                  <el-option :value="20" label="20 / page" />
                  <el-option :value="50" label="50 / page" />
                  <el-option :value="100" label="100 / page" />
                </el-select>
              </div>

              <div class="genome-toolbar-right">
                <el-input
                  v-model="homologyFilters.species"
                  clearable
                  placeholder="Search species"
                  class="genome-search-input"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>

                <el-input
                  v-model="homologyFilters.genomeVersion"
                  clearable
                  placeholder="Search genome version"
                  class="genome-search-input"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>

                <el-button
                  type="primary"
                  plain
                  class="download-filtered-button"
                  :disabled="!filteredHomologyFiles.length"
                  @click="downloadFiles(filteredHomologyFiles)"
                >
                  Download filtered
                </el-button>
              </div>
            </div>

            <homology-resource-table
              v-loading="homologyLoading"
              :files="pagedHomologyFiles"
              empty-text="No homology result files are configured yet"
            />

            <div class="pagination-wrap">
              <el-pagination
                v-model:current-page="homologyCurrentPage"
                :page-size="homologyPageSize"
                layout="prev, pager, next, jumper"
                :total="filteredHomologyFiles.length"
                :background="false"
              />
            </div>
          </el-tab-pane>

          <el-tab-pane label="SNF-related Genes" name="snf">
            <div class="table-toolbar">
              <div class="genome-toolbar-left">
                <div class="result-count">
                  Total: <span>{{ snfFiles.length }}</span>
                </div>
              </div>
            </div>

            <snf-resource-table
              v-loading="snfLoading"
              :files="snfFiles"
              empty-text="No SNF-related gene files are configured yet"
            />
          </el-tab-pane>
        </el-tabs>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, reactive, ref, watch } from 'vue'
import { ElButton, ElMessage, ElTable, ElTableColumn } from 'element-plus'
import { FolderOpened, Search } from '@element-plus/icons-vue'
import request from '@/utils/request'

const ResourceTable = defineComponent({
  name: 'ResourceTable',
  props: {
    files: {
      type: Array,
      default: () => []
    },
    emptyText: {
      type: String,
      default: 'No files found'
    }
  },
  setup(props) {
    return () => h(
      ElTable,
      {
        data: props.files,
        border: true,
        stripe: true,
        emptyText: props.emptyText,
        style: 'width: 100%'
      },
      () => [
        h(ElTableColumn, { prop: 'species', label: 'Species', minWidth: 190 }),
        h(ElTableColumn, { prop: 'genomeVersion', label: 'Genome Version', minWidth: 170 }),
        h(ElTableColumn, { prop: 'filename', label: 'Filename', minWidth: 280 }),
        h(
          ElTableColumn,
          { prop: 'type', label: 'Type', width: 150, align: 'center' },
          {
            default: ({ row }) => h('span', { class: 'resource-type-button' }, row.type)
          }
        ),
        h(ElTableColumn, { prop: 'format', label: 'Format', width: 110, align: 'center' }),
        h(ElTableColumn, { prop: 'sizeLabel', label: 'Size', width: 120, align: 'center' }),
        h(ElTableColumn, { prop: 'updatedAt', label: 'Updated', width: 130, align: 'center' }),
        h(
          ElTableColumn,
          { label: 'Action', width: 140, align: 'center' },
          {
            default: ({ row }) => {
              const buttonProps = {
                tag: 'a',
                type: 'primary',
                plain: true,
                size: 'small',
                class: 'resource-download-button',
                href: row.url
              }

              if (row.download !== false) {
                buttonProps.download = row.download || row.filename
              }

              return h(
                ElButton,
                buttonProps,
                () => 'Download'
              )
            }
          }
        )
      ]
    )
  }
})

const CifResourceTable = defineComponent({
  name: 'CifResourceTable',
  props: {
    files: {
      type: Array,
      default: () => []
    },
    emptyText: {
      type: String,
      default: 'No CIF files found'
    }
  },
  setup(props) {
    return () => h(
      ElTable,
      {
        data: props.files,
        border: true,
        stripe: true,
        emptyText: props.emptyText,
        style: 'width: 100%'
      },
      () => [
        h(ElTableColumn, { prop: 'proteinId', label: 'Protein ID', minWidth: 220 }),
        h(ElTableColumn, { prop: 'filename', label: 'Filename', minWidth: 280 }),
        h(ElTableColumn, { prop: 'sizeLabel', label: 'Size', width: 120, align: 'center' }),
        h(ElTableColumn, { prop: 'updatedAt', label: 'Updated', width: 130, align: 'center' }),
        h(ElTableColumn, { prop: 'format', label: 'Format', width: 110, align: 'center' }),
        h(
          ElTableColumn,
          { label: 'Action', width: 140, align: 'center' },
          {
            default: ({ row }) => {
              const buttonProps = {
                tag: 'a',
                type: 'primary',
                plain: true,
                size: 'small',
                class: 'resource-download-button',
                href: row.url
              }

              if (row.download !== false) {
                buttonProps.download = row.download || row.filename
              }

              return h(
                ElButton,
                buttonProps,
                () => 'Download'
              )
            }
          }
        )
      ]
    )
  }
})

const NpyResourceTable = defineComponent({
  name: 'NpyResourceTable',
  props: {
    files: {
      type: Array,
      default: () => []
    },
    emptyText: {
      type: String,
      default: 'No NPY files found'
    }
  },
  setup(props) {
    return () => h(
      ElTable,
      {
        data: props.files,
        border: true,
        stripe: true,
        emptyText: props.emptyText,
        style: 'width: 100%'
      },
      () => [
        h(ElTableColumn, { prop: 'species', label: 'Species', minWidth: 190 }),
        h(ElTableColumn, { prop: 'genomeVersion', label: 'Genome Version', minWidth: 170 }),
        h(
          ElTableColumn,
          { prop: 'type', label: 'Type', width: 130, align: 'center' },
          {
            default: ({ row }) => h('span', { class: 'resource-type-button' }, row.type)
          }
        ),
        h(ElTableColumn, { prop: 'filename', label: 'Filename', minWidth: 280 }),
        h(ElTableColumn, { prop: 'sizeLabel', label: 'Size', width: 120, align: 'center' }),
        h(ElTableColumn, { prop: 'updatedAt', label: 'Date', width: 130, align: 'center' }),
        h(
          ElTableColumn,
          { label: 'Action', width: 140, align: 'center' },
          {
            default: ({ row }) => {
              const buttonProps = {
                tag: 'a',
                type: 'primary',
                plain: true,
                size: 'small',
                class: 'resource-download-button',
                href: row.url
              }

              if (row.download !== false) {
                buttonProps.download = row.download || row.filename
              }

              return h(
                ElButton,
                buttonProps,
                () => 'Download'
              )
            }
          }
        )
      ]
    )
  }
})

const HomologyResourceTable = NpyResourceTable

const SnfResourceTable = defineComponent({
  name: 'SnfResourceTable',
  props: {
    files: {
      type: Array,
      default: () => []
    },
    emptyText: {
      type: String,
      default: 'No SNF-related gene files found'
    }
  },
  setup(props) {
    return () => h(
      ElTable,
      {
        data: props.files,
        border: true,
        stripe: true,
        emptyText: props.emptyText,
        style: 'width: 100%'
      },
      () => [
        h(ElTableColumn, { prop: 'filename', label: 'Filename', minWidth: 360 }),
        h(ElTableColumn, { prop: 'sizeLabel', label: 'Size', width: 120, align: 'center' }),
        h(ElTableColumn, { prop: 'updatedAt', label: 'Date', width: 130, align: 'center' }),
        h(
          ElTableColumn,
          { label: 'Action', width: 140, align: 'center' },
          {
            default: ({ row }) => {
              const buttonProps = {
                tag: 'a',
                type: 'primary',
                plain: true,
                size: 'small',
                class: 'resource-download-button',
                href: row.url
              }

              if (row.download !== false) {
                buttonProps.download = row.download || row.filename
              }

              return h(
                ElButton,
                buttonProps,
                () => 'Download'
              )
            }
          }
        )
      ]
    )
  }
})

const activeTab = ref('genome')

const genomeFiles = ref([])
const genomeLoading = ref(false)
const genomeCurrentPage = ref(1)
const genomePageSize = ref(10)
const genomeFilters = reactive({
  species: '',
  genomeVersion: ''
})

const cifFiles = ref([])
const cifLoading = ref(false)
const cifCurrentPage = ref(1)
const cifPageSize = ref(10)
const cifFilters = reactive({
  proteinId: ''
})

const npyFiles = ref([])
const npyLoading = ref(false)
const npyCurrentPage = ref(1)
const npyPageSize = ref(10)
const npyFilters = reactive({
  species: '',
  genomeVersion: ''
})

const homologyFiles = ref([])
const homologyLoading = ref(false)
const homologyCurrentPage = ref(1)
const homologyPageSize = ref(10)
const homologyFilters = reactive({
  species: '',
  genomeVersion: ''
})

const snfFiles = ref([])
const snfLoading = ref(false)

function normalizeGenomeResourceFile(item) {
  return {
    species: item.species || '',
    genomeVersion:
      item.genomeVersion ||
      item.genome_version ||
      item.conservatory_genome_name ||
      '',
    conservatoryGenomeName:
      item.conservatoryGenomeName ||
      item.conservatory_genome_name ||
      '',
    type: item.type || '',
    format: item.format || '',
    bytes: item.bytes || 0,
    sizeLabel: item.sizeLabel || item.size_label || '-',
    updatedAt: item.updatedAt || item.updated_at || '-',
    filename: item.filename || '',
    url: item.url || '',
    download: false
  }
}

function normalizeCifResourceFile(item) {
  return {
    proteinId: item.proteinId || item.protein_id || '',
    filename: item.filename || '',
    bytes: item.bytes || 0,
    sizeLabel: item.sizeLabel || item.size_label || '-',
    updatedAt: item.updatedAt || item.updated_at || '-',
    format: item.format || 'CIF',
    url: item.url || '',
    download: false
  }
}

function normalizeNpyResourceFile(item) {
  return {
    species: item.species || '',
    genomeVersion:
      item.genomeVersion ||
      item.genome_version ||
      item.conservatory_genome_name ||
      '',
    conservatoryGenomeName:
      item.conservatoryGenomeName ||
      item.conservatory_genome_name ||
      '',
    type: item.type || '',
    bytes: item.bytes || 0,
    sizeLabel: item.sizeLabel || item.size_label || '-',
    updatedAt: item.updatedAt || item.updated_at || '-',
    filename: item.filename || '',
    url: item.url || '',
    download: false
  }
}

function normalizeHomologyResourceFile(item) {
  return {
    species: item.species || '',
    genomeVersion:
      item.genomeVersion ||
      item.genome_version ||
      item.conservatory_genome_name ||
      '',
    conservatoryGenomeName:
      item.conservatoryGenomeName ||
      item.conservatory_genome_name ||
      '',
    type: item.type || 'results',
    bytes: item.bytes || 0,
    sizeLabel: item.sizeLabel || item.size_label || '-',
    updatedAt: item.updatedAt || item.updated_at || '-',
    filename: item.filename || '',
    url: item.url || '',
    download: false
  }
}

function normalizeSnfResourceFile(item) {
  return {
    bytes: item.bytes || 0,
    sizeLabel: item.sizeLabel || item.size_label || '-',
    updatedAt: item.updatedAt || item.updated_at || '-',
    filename: item.filename || '',
    url: item.url || '',
    download: false
  }
}

const filteredGenomeFiles = computed(() => filterGenomeFiles(genomeFiles.value))
const pagedGenomeFiles = computed(() => {
  const start = (genomeCurrentPage.value - 1) * genomePageSize.value
  const end = start + genomePageSize.value

  return filteredGenomeFiles.value.slice(start, end)
})
const filteredCifFiles = computed(() => filterCifFiles(cifFiles.value))
const pagedCifFiles = computed(() => {
  const start = (cifCurrentPage.value - 1) * cifPageSize.value
  const end = start + cifPageSize.value

  return filteredCifFiles.value.slice(start, end)
})
const filteredNpyFiles = computed(() => filterNpyFiles(npyFiles.value))
const pagedNpyFiles = computed(() => {
  const start = (npyCurrentPage.value - 1) * npyPageSize.value
  const end = start + npyPageSize.value

  return filteredNpyFiles.value.slice(start, end)
})
const filteredHomologyFiles = computed(() => filterHomologyFiles(homologyFiles.value))
const pagedHomologyFiles = computed(() => {
  const start = (homologyCurrentPage.value - 1) * homologyPageSize.value
  const end = start + homologyPageSize.value

  return filteredHomologyFiles.value.slice(start, end)
})

function includesKeyword(value, keyword) {
  if (!keyword) return true
  return String(value ?? '').toLowerCase().includes(keyword)
}

function filterGenomeFiles(files) {
  const speciesKeyword = genomeFilters.species.trim().toLowerCase()
  const genomeKeyword = genomeFilters.genomeVersion.trim().toLowerCase()

  return files.filter(item => {
    const matchesSpecies = includesKeyword(item.species, speciesKeyword)
    const matchesGenome = includesKeyword(item.genomeVersion, genomeKeyword)

    return matchesSpecies && matchesGenome
  })
}

function filterCifFiles(files) {
  const proteinKeyword = cifFilters.proteinId.trim().toLowerCase()

  return files.filter(item => includesKeyword(item.proteinId, proteinKeyword))
}

function filterNpyFiles(files) {
  const speciesKeyword = npyFilters.species.trim().toLowerCase()
  const genomeKeyword = npyFilters.genomeVersion.trim().toLowerCase()

  return files.filter(item => {
    const matchesSpecies = includesKeyword(item.species, speciesKeyword)
    const matchesGenome = includesKeyword(item.genomeVersion, genomeKeyword)

    return matchesSpecies && matchesGenome
  })
}

function filterHomologyFiles(files) {
  const speciesKeyword = homologyFilters.species.trim().toLowerCase()
  const genomeKeyword = homologyFilters.genomeVersion.trim().toLowerCase()

  return files.filter(item => {
    const matchesSpecies = includesKeyword(item.species, speciesKeyword)
    const matchesGenome = includesKeyword(item.genomeVersion, genomeKeyword)

    return matchesSpecies && matchesGenome
  })
}

watch(
  () => [genomeFilters.species, genomeFilters.genomeVersion, genomePageSize.value],
  () => {
    genomeCurrentPage.value = 1
  }
)

watch(
  () => [cifFilters.proteinId, cifPageSize.value],
  () => {
    cifCurrentPage.value = 1
  }
)

watch(
  () => [npyFilters.species, npyFilters.genomeVersion, npyPageSize.value],
  () => {
    npyCurrentPage.value = 1
  }
)

watch(
  () => [homologyFilters.species, homologyFilters.genomeVersion, homologyPageSize.value],
  () => {
    homologyCurrentPage.value = 1
  }
)

function downloadFiles(files) {
  if (!files.length) {
    ElMessage.warning('No files available for the current filters')
    return
  }

  files.forEach((file, index) => {
    window.setTimeout(() => {
      const link = document.createElement('a')
      link.href = file.url
      if (file.download !== false) {
        link.download = file.download || file.filename
      }
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }, index * 150)
  })
}

function formatFileSize(bytes) {
  if (!bytes) return '0 B'

  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex += 1
  }

  return `${size.toFixed(size >= 10 || unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`
}

async function fetchGenomeFiles() {
  genomeLoading.value = true

  try {
    const res = await request.get('/api/genome/files/')
    genomeFiles.value = (res.data.data || []).map(normalizeGenomeResourceFile)
  } catch (error) {
    console.error('Failed to fetch genome resources:', error)
    genomeFiles.value = []
    ElMessage.error(
      error?.response?.data?.message || 'Failed to load genome resources'
    )
  } finally {
    genomeLoading.value = false
  }
}

async function fetchCifFiles() {
  cifLoading.value = true

  try {
    const res = await request.get('/api/protein/cif/files/')
    cifFiles.value = (res.data.data || []).map(normalizeCifResourceFile)
  } catch (error) {
    console.error('Failed to fetch CIF resources:', error)
    cifFiles.value = []
    ElMessage.error(
      error?.response?.data?.message || 'Failed to load CIF resources'
    )
  } finally {
    cifLoading.value = false
  }
}

async function fetchNpyFiles() {
  npyLoading.value = true

  try {
    const res = await request.get('/api/npy/files/')
    npyFiles.value = (res.data.data || []).map(normalizeNpyResourceFile)
  } catch (error) {
    console.error('Failed to fetch NPY resources:', error)
    npyFiles.value = []
    ElMessage.error(
      error?.response?.data?.message || 'Failed to load NPY resources'
    )
  } finally {
    npyLoading.value = false
  }
}

async function fetchHomologyFiles() {
  homologyLoading.value = true

  try {
    const res = await request.get('/api/homology/files/')
    homologyFiles.value = (res.data.data || []).map(normalizeHomologyResourceFile)
  } catch (error) {
    console.error('Failed to fetch homology resources:', error)
    homologyFiles.value = []
    ElMessage.error(
      error?.response?.data?.message || 'Failed to load homology resources'
    )
  } finally {
    homologyLoading.value = false
  }
}

async function fetchSnfFiles() {
  snfLoading.value = true

  try {
    const res = await request.get('/api/snf/files/')
    snfFiles.value = (res.data.data || []).map(normalizeSnfResourceFile)
  } catch (error) {
    console.error('Failed to fetch SNF-related gene resources:', error)
    snfFiles.value = []
    ElMessage.error(
      error?.response?.data?.message || 'Failed to load SNF-related gene resources'
    )
  } finally {
    snfLoading.value = false
  }
}

onMounted(() => {
  fetchGenomeFiles()
  fetchCifFiles()
  fetchNpyFiles()
  fetchHomologyFiles()
  fetchSnfFiles()
})
</script>

<style scoped>
.download-page {
  width: 100%;
  min-height: 100vh;
  padding: 24px;
  box-sizing: border-box;
  background:
    radial-gradient(circle at top left, rgba(122, 185, 234, 0.16), transparent 34%),
    #f7fbff;
  color: #17284a;
  font-family: "Arial", "Helvetica", sans-serif;
}

.page-container {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
}

.hero-card,
.panel-card,
.summary-card {
  background: #ffffff;
  border: 1px solid #dce8f6;
  border-radius: 8px;
  box-shadow: 0 8px 28px rgba(27, 83, 142, 0.08);
  box-sizing: border-box;
}

.hero-card {
  padding: 28px 34px;
}

.eyebrow {
  margin: 0 0 8px;
  color: #6fa4e8;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.hero-card h1 {
  margin: 0 0 10px;
  color: #0d4f9e;
  font-size: 30px;
  line-height: 1.2;
}

.hero-card p:last-child {
  max-width: 980px;
  margin: 0;
  color: #203250;
  font-size: 15px;
  line-height: 1.8;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
  margin-top: 18px;
}

.summary-card {
  min-height: 96px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.summary-card .el-icon {
  width: 48px;
  height: 48px;
  flex: 0 0 48px;
  color: #1261cb;
  background: #f4f7fc;
  border: 1px solid #d8e8fb;
  border-radius: 50%;
  font-size: 24px;
}

.summary-card span {
  display: block;
  color: #52627a;
  font-size: 13px;
  font-weight: 700;
}

.summary-card strong {
  display: block;
  margin-top: 4px;
  color: #ef9bd0;
  font-size: 26px;
  line-height: 1;
}

.panel-card {
  position: relative;
  margin-top: 18px;
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

.filter-panel {
  padding: 58px 28px 28px;
}

.data-panel {
  padding: 58px 28px 28px;
}

.download-tabs :deep(.el-tabs__item) {
  color: #2f456b;
  font-size: 16px;
  font-weight: 700;
  margin-top: 18px;
}

.download-tabs :deep(.el-tabs__item.is-active) {
  color: #0d4f9e;
}

.download-tabs :deep(.el-tabs__active-bar) {
  background: #6fa4e8;
}

.table-toolbar {
  margin: 14px 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-top: 25px;
  flex-wrap: nowrap;
}

.genome-toolbar-left,
.genome-toolbar-right {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: nowrap;
  min-width: 0;
}

.genome-toolbar-right {
  flex: 1 1 auto;
  justify-content: flex-end;
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

.genome-search-input {
  width: 260px;
}

.download-filtered-button {
  width: 166px;
  height: 36px;
  flex: 0 0 166px;
}

.resource-type-button {
  width: 68px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  border: 1px solid #8bbcff;
  border-radius: 4px;
  background: #f4f9ff;
  color: #0d4f9e;
  font-size: 12px;
  line-height: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.resource-download-button {
  width: 76px;
  height: 24px;
  padding: 0;
  font-size: 12px;
}

.resource-download-button :deep(span) {
  line-height: 1;
}

.download-filtered-button,
.resource-download-button {
  background: #f4f9ff;
}

.download-filtered-button:hover,
.download-filtered-button:focus,
.resource-download-button:hover,
.resource-download-button:focus {
  color: #409eff;
  border-color: #409eff;
  background: #ecf5ff;
}

.download-filtered-button:active,
.resource-download-button:active {
  color: #337ecc;
  border-color: #337ecc;
  background: #d9ecff;
}

.pagination-wrap {
  margin-top: 20px;
  display: flex;
  justify-content: flex-start;
  overflow-x: auto;
}

.table-toolbar h2 {
  margin: 0 0 6px;
  color: #0d4f9e;
  font-size: 20px;
}

.table-toolbar p {
  margin: 0;
  color: #52627a;
  font-size: 14px;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.empty-note {
  margin-top: 14px;
  padding: 14px 16px;
  color: #52627a;
  background: #f8fbff;
  border: 1px dashed #cfe2f8;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.6;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  min-height: 42px;
}

:deep(.el-table th.el-table__cell) {
  background: #f8fbff;
  color: #606266;
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

@media (max-width: 1100px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .table-toolbar {
    flex-wrap: wrap;
  }

  .genome-toolbar-right {
    justify-content: flex-start;
  }
}

@media (max-width: 720px) {
  .download-page {
    padding: 16px;
  }

  .hero-card,
  .filter-panel,
  .data-panel {
    padding-left: 18px;
    padding-right: 18px;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .table-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .genome-toolbar-left,
  .genome-toolbar-right {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
  }

  .genome-search-input,
  .page-size-select {
    width: 100%;
  }
}
</style>
