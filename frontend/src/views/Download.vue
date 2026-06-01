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
              <span>Npy files</span>
              <strong>300 +</strong>
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
              <span>Homology results</span>
              <strong>2M +</strong>
            </div>
          </article>

          <article class="summary-card">
            <el-icon><FolderOpened /></el-icon>
            <div>
              <span>SNF-related Genes</span>
              <strong>240 +</strong>
            </div>
          </article>
        </section>
      </section>

      <section class="panel-card filter-panel">
        <div class="panel-tag">Filters</div>

        <el-form
          ref="formRef"
          :model="downloadForm"
          :rules="rules"
          label-position="top"
          class="download-form"
        >
          <div class="filter-grid">
            <el-form-item label="Species" prop="species" class="filter-item species-filter">
              <el-select
                v-model="downloadForm.species"
                class="italic-select"
                clearable
                filterable
                placeholder="Select species"
                :teleported="false"
                @change="handleSpeciesChange"
                @clear="handleSpeciesClear"
              >
                <el-option
                  v-for="species in speciesOptions"
                  :key="species"
                  :label="species"
                  :value="species"
                />
              </el-select>
            </el-form-item>

            <el-form-item
              label="Genome Version"
              prop="genomeVersion"
              class="filter-item genome-filter"
            >
              <el-select
                v-model="downloadForm.genomeVersion"
                clearable
                filterable
                placeholder="Select genome version"
                :disabled="!downloadForm.species"
                :teleported="false"
              >
                <el-option
                  v-for="item in genomeVersionOptions"
                  :key="item.conservatory_genome_name"
                  :label="`${item.genome_version} (${item.conservatory_genome_name})`"
                  :value="item.conservatory_genome_name"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="File Type" prop="fileType" class="filter-item file-type-filter">
              <el-select
                v-model="downloadForm.fileType"
                clearable
                placeholder="Select file type"
                :teleported="false"
              >
                <el-option
                  v-for="type in fileTypeOptions"
                  :key="type.value"
                  :label="type.label"
                  :value="type.value"
                />
              </el-select>
            </el-form-item>
          </div>

          <div class="form-actions">
            <el-button type="primary" size="small" plain @click="handleSubmit">
              Submit
            </el-button>
            <el-button type="danger" size="small" plain @click="resetFilters">
              Reset
            </el-button>
          </div>
        </el-form>
      </section>

      <section class="panel-card data-panel">
        <div class="panel-tag">Files</div>

        <el-tabs v-model="activeTab" class="download-tabs">
          <el-tab-pane label="Genome Resources" name="genome">
            <div class="table-toolbar">
              <el-button
                type="primary"
                plain
                :disabled="!filteredGenomeFiles.length"
                @click="downloadFiles(filteredGenomeFiles)"
              >
                Download filtered
              </el-button>
            </div>

            <resource-table
              :files="filteredGenomeFiles"
              empty-text="No genome files are configured yet"
            />
          </el-tab-pane>

          <el-tab-pane label="Structure CIF Files" name="cif">
            <div class="table-toolbar">

              <el-button
                type="primary"
                plain
                :disabled="!filteredCifFiles.length"
                @click="downloadFiles(filteredCifFiles)"
              >
                Download filtered
              </el-button>
            </div>

            <resource-table
              :files="filteredCifFiles"
              empty-text="No CIF files found"
            />
          </el-tab-pane>

          <el-tab-pane label="Npy files" name="npy">
            <div class="table-toolbar">
              <el-button
                type="primary"
                plain
                :disabled="!filteredNpyFiles.length"
                @click="downloadFiles(filteredNpyFiles)"
              >
                Download filtered
              </el-button>
            </div>

            <resource-table
              :files="filteredNpyFiles"
              empty-text="No NPY files are configured yet"
            />
          </el-tab-pane>

          <el-tab-pane label="Homology results" name="homology">
            <div class="table-toolbar">

              <el-button
                type="primary"
                plain
                :disabled="!filteredHomologyFiles.length"
                @click="downloadFiles(filteredHomologyFiles)"
              >
                Download filtered
              </el-button>
            </div>

            <resource-table
              :files="filteredHomologyFiles"
              empty-text="No homology result files are configured yet"
            />
          </el-tab-pane>

          <el-tab-pane label="SNF-related Genes" name="snf">
            <div class="table-toolbar">

              <el-button
                type="primary"
                plain
                :disabled="!filteredSnfFiles.length"
                @click="downloadFiles(filteredSnfFiles)"
              >
                Download filtered
              </el-button>
            </div>

            <resource-table
              :files="filteredSnfFiles"
              empty-text="No SNF-related gene files are configured yet"
            />
          </el-tab-pane>
        </el-tabs>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, reactive, ref } from 'vue'
import { ElButton, ElMessage, ElTable, ElTableColumn, ElTag } from 'element-plus'
import { FolderOpened } from '@element-plus/icons-vue'
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
        h(
          ElTableColumn,
          { prop: 'type', label: 'Type', width: 150, align: 'center' },
          {
            default: ({ row }) => h(ElTag, { effect: 'plain', type: 'primary' }, () => row.type)
          }
        ),
        h(ElTableColumn, { prop: 'format', label: 'Format', width: 110, align: 'center' }),
        h(ElTableColumn, { prop: 'sizeLabel', label: 'Size', width: 120, align: 'center' }),
        h(ElTableColumn, { prop: 'updatedAt', label: 'Updated', width: 130, align: 'center' }),
        h(
          ElTableColumn,
          { label: 'Action', width: 140, align: 'center' },
          {
            default: ({ row }) => h(
              ElButton,
              {
                tag: 'a',
                type: 'primary',
                plain: true,
                size: 'small',
                href: row.url,
                download: row.filename
              },
              () => 'Download'
            )
          }
        )
      ]
    )
  }
})

const formRef = ref()
const activeTab = ref('genome')

const DEFAULT_SPECIES = 'Arabidopsis thaliana'
const DEFAULT_CONSERVATORY_GENOME_NAME = 'Athaliana'
const DEFAULT_FILE_TYPE = 'Genome'

const downloadForm = reactive({
  species: DEFAULT_SPECIES,
  genomeVersion: DEFAULT_CONSERVATORY_GENOME_NAME,
  fileType: DEFAULT_FILE_TYPE
})

const speciesGenomeData = ref([])
const speciesOptions = ref([])
const genomeVersionOptions = ref([])
const genomeFiles = ref([])

const fileTypeOptions = [
  { label: 'Genome', value: 'Genome' },
  { label: 'GFF', value: 'GFF' },
  { label: 'CIF', value: 'CIF' },
  { label: 'Npy', value: 'Npy' },
  { label: 'Homology', value: 'Homology' },
  { label: 'SNF-related Genes', value: 'SNF' }
]

// Only Species is required. Genome Version and File Type are optional filters.
const rules = {
  species: [
    {
      required: true,
      message: 'Please select species',
      trigger: 'change'
    }
  ]
}

const cifFileManifest = [
  { filename: 'gmacp__glyma.18g244300_model.cif', bytes: 89679 },
  { filename: 'gmacp__lj1g3v2840250_model.cif', bytes: 90363 },
  { filename: 'gmacp__medtr7g080390_model.cif', bytes: 91579 },
  { filename: 'mtnsp1__phvul_010g129400_model.cif', bytes: 349353 },
  { filename: 'mtpen3-like__phvul.005g166500_model.cif', bytes: 1005902 }
]

// Add real manifests or replace these arrays with API data later.
const npyFileManifest = []
const homologyFileManifest = []
const snfFileManifest = []

const speciesByProteinPrefix = {
  glyma: 'Glycine max',
  phvul: 'Phaseolus vulgaris',
  medtr: 'Medicago truncatula',
  lj: 'Lotus japonicus'
}

function resolveProteinSpecies(proteinId) {
  const normalizedProteinId = proteinId.toLowerCase()
  const matchedPrefix = Object.keys(speciesByProteinPrefix)
    .find(prefix => normalizedProteinId.startsWith(prefix))

  return matchedPrefix ? speciesByProteinPrefix[matchedPrefix] : 'Unknown'
}

function normalizeManifestFiles(files, fallbackType, fallbackFormat, fallbackDirectory = '/downloads') {
  return files.map(item => ({
    species: item.species || DEFAULT_SPECIES,
    genomeVersion: item.genomeVersion || item.genome_version || '',
    conservatoryGenomeName: item.conservatoryGenomeName || item.conservatory_genome_name || '',
    type: item.type || fallbackType,
    format: item.format || fallbackFormat,
    bytes: item.bytes || 0,
    sizeLabel: item.sizeLabel || formatFileSize(item.bytes || 0),
    updatedAt: item.updatedAt || item.updated_at || '-',
    filename: item.filename,
    url: item.url || `${fallbackDirectory}/${item.filename}`
  }))
}

const cifFiles = computed(() =>
  cifFileManifest.map(item => {
    const baseName = item.filename.replace(/_model\.cif$/i, '')
    const [, proteinId = baseName] = baseName.split('__')

    return {
      species: resolveProteinSpecies(proteinId),
      genomeVersion: '',
      conservatoryGenomeName: '',
      type: 'CIF',
      format: 'CIF',
      bytes: item.bytes,
      sizeLabel: formatFileSize(item.bytes),
      updatedAt: '-',
      filename: item.filename,
      url: `/cif/${item.filename}`
    }
  })
)

const npyFiles = computed(() => normalizeManifestFiles(npyFileManifest, 'Npy', 'NPY', '/npy'))
const homologyFiles = computed(() => normalizeManifestFiles(homologyFileManifest, 'Homology', 'TSV', '/homology'))
const snfFiles = computed(() => normalizeManifestFiles(snfFileManifest, 'SNF-related Genes', 'TSV', '/snf'))

const allFiles = computed(() => [
  ...genomeFiles.value,
  ...cifFiles.value,
  ...npyFiles.value,
  ...homologyFiles.value,
  ...snfFiles.value
])

const filteredGenomeFiles = computed(() => filterFiles(genomeFiles.value, ['Genome', 'GFF', 'CDS', 'Protein', 'FASTA']))
const filteredCifFiles = computed(() => filterFiles(cifFiles.value, ['CIF']))
const filteredNpyFiles = computed(() => filterFiles(npyFiles.value, ['Npy']))
const filteredHomologyFiles = computed(() => filterFiles(homologyFiles.value, ['Homology']))
const filteredSnfFiles = computed(() => filterFiles(snfFiles.value, ['SNF', 'SNF-related Genes']))

const tabByFileType = {
  Genome: 'genome',
  GFF: 'genome',
  CIF: 'cif',
  Npy: 'npy',
  Homology: 'homology',
  SNF: 'snf'
}

function filterFiles(files, allowedTypes = []) {
  return files.filter(item => {
    const matchesSpecies = !downloadForm.species || item.species === downloadForm.species
    const matchesType =
      !downloadForm.fileType ||
      allowedTypes.includes(downloadForm.fileType) ||
      item.type === downloadForm.fileType
    const matchesGenome =
      !downloadForm.genomeVersion ||
      !item.conservatoryGenomeName ||
      item.conservatoryGenomeName === downloadForm.genomeVersion

    return matchesSpecies && matchesType && matchesGenome
  })
}

function handleSpeciesChange(species) {
  downloadForm.genomeVersion = ''

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
      downloadForm.genomeVersion = DEFAULT_CONSERVATORY_GENOME_NAME
      return
    }
  }

  if (genomeVersionOptions.value.length) {
    downloadForm.genomeVersion =
      genomeVersionOptions.value[0].conservatory_genome_name
  }
}

function handleSpeciesClear() {
  downloadForm.species = ''
  downloadForm.genomeVersion = ''
  genomeVersionOptions.value = []
}

async function handleSubmit() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  if (downloadForm.fileType && tabByFileType[downloadForm.fileType]) {
    activeTab.value = tabByFileType[downloadForm.fileType]
  }
}

function resetFilters() {
  if (formRef.value) {
    formRef.value.clearValidate()
  }

  downloadForm.species = DEFAULT_SPECIES
  downloadForm.fileType = DEFAULT_FILE_TYPE
  handleSpeciesChange(DEFAULT_SPECIES)
  activeTab.value = 'genome'
}

function downloadFiles(files) {
  if (!files.length) {
    ElMessage.warning('No files available for the current filters')
    return
  }

  files.forEach((file, index) => {
    window.setTimeout(() => {
      const link = document.createElement('a')
      link.href = file.url
      link.download = file.filename
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

async function fetchSpeciesOptions() {
  try {
    const res = await request.get('/api/species/names/')
    speciesGenomeData.value = res.data.data || []

    const apiSpecies = speciesGenomeData.value
      .map(item => item.species)
      .filter(Boolean)
    const fileSpecies = allFiles.value
      .map(item => item.species)
      .filter(Boolean)

    speciesOptions.value = Array.from(new Set([...apiSpecies, ...fileSpecies]))
      .sort((a, b) => a.localeCompare(b))

    if (speciesOptions.value.includes(DEFAULT_SPECIES)) {
      downloadForm.species = DEFAULT_SPECIES
    } else if (speciesOptions.value.length) {
      downloadForm.species = speciesOptions.value[0]
    }

    handleSpeciesChange(downloadForm.species)
  } catch (error) {
    console.error('Failed to fetch species options:', error)
    speciesOptions.value = Array.from(
      new Set(allFiles.value.map(item => item.species).filter(Boolean))
    ).sort((a, b) => a.localeCompare(b))
    handleSpeciesChange(downloadForm.species)
  }
}

onMounted(() => {
  fetchSpeciesOptions()
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

.download-form {
  width: 100%;
}

.filter-grid {
  display: grid;
  grid-template-columns: minmax(230px, 290px) minmax(240px, 280px) minmax(170px, 210px);
  column-gap: 28px;
  row-gap: 17px;
  align-items: end;
  justify-content: center;
  margin-top: 18px;
}

.filter-item {
  margin-bottom: 0;
}

.filter-item :deep(.el-form-item__label) {
  color: #2f456b;
  font-size: 16px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 10px;
  text-align: left;
}

.filter-item :deep(.el-select) {
  width: 100%;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 22px;
}

.form-actions :deep(.el-button) {
  min-width: 72px;
  height: 32px;
  padding: 6px 16px;
  margin-left: 0;
  font-size: 13px;
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
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  margin-top: 25px;
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

@media (max-width: 1100px) {
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .filter-grid {
    grid-template-columns: repeat(2, minmax(230px, 290px));
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

  .filter-grid {
    grid-template-columns: minmax(0, 290px);
  }

  .table-toolbar {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
