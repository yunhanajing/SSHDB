<template>
  <div class="jbrowse-page">
    <div class="page-container">
      <!-- Search Card -->
      <section class="section-card search-card">
        <div class="section-label">Search</div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          class="search-form"
        >
          <div class="form-grid">
            <!-- Species -->
            <el-form-item label="Species" prop="species" class="grid-item">
              <el-select
                v-model="form.species"
                class="italic-select"
                placeholder="eg. Arabidopsis thaliana"
                clearable
                filterable
                style="width: 100%"
                :loading="genomesLoading"
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

            <!-- Genome Version -->
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
                @change="handleGenomeChange"
              >
                <el-option
                  v-for="item in genomeVersionOptions"
                  :key="item.conservatory_genome_name"
                  :label="`${item.genome_version} (${item.conservatory_genome_name})`"
                  :value="item.conservatory_genome_name"
                />
              </el-select>
            </el-form-item>
          </div>

          <div class="form-actions">
            <el-button type="primary" plain @click="handleSearch">
              Search
            </el-button>

            <el-button type="danger" plain @click="handleReset">
              Reset
            </el-button>
          </div>
        </el-form>
      </section>

      <!-- Browser Card -->
      <section class="section-card browser-card">
        <div class="section-label">JBrowse</div>

        <div class="current-genome-line">
          <span class="current-label">Current Genome:</span>
          <span class="current-link">{{ selectedSpeciesLabel }}</span>
          <span class="divider">|</span>
          <span class="current-link">{{ selectedGenomeLabel }}</span>
        </div>

        <div
          v-if="canShowBrowser"
          class="jbrowse-browser-box"
        >
          <div class="jbrowse-frame-box">
            <iframe
              :key="iframeKey"
              :src="activeJbrowseUrl"
              class="jbrowse-frame"
              title="JBrowse Genome Browser"
            />
          </div>

          <div class="jbrowse-download-bar">
            <div class="jbrowse-download-actions">
              <span class="toolbar-label">Download:</span>

              <el-button
                size="small"
                plain
                type="primary"
                :icon="Download"
                :disabled="!downloadLinks.fasta"
                @click="downloadGenome"
              >
                FASTA
              </el-button>

              <el-button
                size="small"
                plain
                type="primary"
                :icon="Download"
                :disabled="!downloadLinks.annotation"
                @click="downloadAnnotation"
              >
                GFF3
              </el-button>
            </div>
          </div>
        </div>

        <div
          v-else
          class="empty-browser-box"
        >
          {{ emptyBrowserMessage }}
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'

const formRef = ref()

const DEFAULT_SPECIES = 'Arabidopsis thaliana'
const DEFAULT_CONSERVATORY_GENOME_NAME = 'Athaliana'

const JBROWSE_BASE_URL = normalizeBaseUrl(
  import.meta.env.VITE_JBROWSE_BASE_URL || '/jbrowse-static'
)
const JBROWSE_VIEWER_VERSION = '20260521-annotation-height'

const form = reactive({
  species: DEFAULT_SPECIES,
  conservatory_genome_name: DEFAULT_CONSERVATORY_GENOME_NAME
})

const rules = {
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

const genomesLoading = ref(false)
const speciesGenomeData = ref([])
const speciesOptions = ref([])
const genomeVersionOptions = ref([])
const iframeKey = ref(0)
const activeJbrowseUrl = ref('')

function normalizeBaseUrl(value) {
  const base = String(value || '').trim()
  return base ? base.replace(/\/+$/, '') : ''
}

function joinUrl(base, path) {
  const cleanPath = String(path || '').replace(/^\/+/, '')
  return base ? `${base}/${cleanPath}` : `/${cleanPath}`
}

function normalizeGenomeManifest(manifest) {
  const speciesMap = new Map()

  Object.entries(manifest || {}).forEach(([genomeKey, config]) => {
    const species = config.species || genomeKey
    const conservatoryGenomeName =
      config.conservatory_genome_name || genomeKey
    const genomeVersion =
      config.genome_version || config.assemblyName || conservatoryGenomeName

    if (!speciesMap.has(species)) {
      speciesMap.set(species, {
        family: config.family || '',
        species,
        genome_versions: []
      })
    }

    speciesMap.get(species).genome_versions.push({
      genome_key: genomeKey,
      genome_version: genomeVersion,
      conservatory_genome_name: conservatoryGenomeName,
      fasta_uri: config.fastaUri || config.fasta_url || config.genome_url || '',
      annotation_uri:
        config.gff3Uri ||
        config.annotation_url ||
        config.gff3_url ||
        config.gff_url ||
        ''
    })
  })

  return Array.from(speciesMap.values())
    .map(item => ({
      ...item,
      genome_versions: item.genome_versions.sort((a, b) =>
        a.genome_version.localeCompare(b.genome_version)
      )
    }))
    .sort((a, b) => a.species.localeCompare(b.species))
}

const selectedGenome = computed(() => {
  return genomeVersionOptions.value.find(
    item => item.conservatory_genome_name === form.conservatory_genome_name
  )
})

const selectedSpeciesLabel = computed(() => {
  return form.species || '-'
})

const selectedGenomeLabel = computed(() => {
  if (!selectedGenome.value) return '-'

  return `${selectedGenome.value.genome_version} (${selectedGenome.value.conservatory_genome_name})`
})

const jbrowseUrl = computed(() => {
  if (!selectedGenome.value) return ''

  const params = new URLSearchParams()

  params.set(
    'genome',
    selectedGenome.value.genome_key || form.conservatory_genome_name
  )
  params.set('v', JBROWSE_VIEWER_VERSION)

  return `${joinUrl(JBROWSE_BASE_URL, 'viewer.html')}?${params.toString()}`
})

const canShowBrowser = computed(() => {
  return Boolean(activeJbrowseUrl.value)
})

const downloadLinks = computed(() => {
  return {
    fasta: resolveJbrowseAssetUri(selectedGenome.value?.fasta_uri),
    annotation: resolveJbrowseAssetUri(selectedGenome.value?.annotation_uri)
  }
})

const emptyBrowserMessage = computed(() => {
  if (genomesLoading.value) return 'Loading genome browser manifest...'

  if (!speciesOptions.value.length) {
    return `No genomes found. Please check ${joinUrl(JBROWSE_BASE_URL, 'genomes.json')}.`
  }

  return 'Please select species and genome version, then click Search.'
})

const fetchGenomeOptions = async () => {
  genomesLoading.value = true

  try {
    const response = await fetch(joinUrl(JBROWSE_BASE_URL, 'genomes.json'), {
      cache: 'no-store'
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const manifest = await response.json()

    speciesGenomeData.value = normalizeGenomeManifest(manifest)

    speciesOptions.value = speciesGenomeData.value
      .map(item => item.species)
      .filter(Boolean)
      .sort((a, b) => a.localeCompare(b))
  } catch (error) {
    console.error('Failed to fetch genome manifest:', error)

    speciesGenomeData.value = []
    speciesOptions.value = []
    genomeVersionOptions.value = []

    ElMessage.error('Failed to load JBrowse genome manifest')
  } finally {
    genomesLoading.value = false
  }
}

const handleSpeciesChange = species => {
  form.conservatory_genome_name = ''
  activeJbrowseUrl.value = ''

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
      form.conservatory_genome_name = defaultGenome.conservatory_genome_name
      return
    }
  }

  if (genomeVersionOptions.value.length === 1) {
    form.conservatory_genome_name =
      genomeVersionOptions.value[0].conservatory_genome_name
  }
}

const handleSpeciesClear = () => {
  form.species = ''
  form.conservatory_genome_name = ''
  genomeVersionOptions.value = []
  activeJbrowseUrl.value = ''
}

const handleGenomeChange = () => {
  activeJbrowseUrl.value = ''
}

const selectFirstAvailableGenome = () => {
  const firstSpecies = speciesGenomeData.value[0]
  const firstGenome = firstSpecies?.genome_versions?.[0]

  if (!firstSpecies || !firstGenome) return false

  form.species = firstSpecies.species
  genomeVersionOptions.value = firstSpecies.genome_versions
  form.conservatory_genome_name = firstGenome.conservatory_genome_name

  return true
}

const handleSearch = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch (error) {
    ElMessage.warning('Please select species and genome version')
    return
  }

  if (!jbrowseUrl.value) {
    ElMessage.warning('Invalid JBrowse genome')
    return
  }

  activeJbrowseUrl.value = jbrowseUrl.value
  iframeKey.value += 1
}

const handleReset = () => {
  form.species = DEFAULT_SPECIES
  form.conservatory_genome_name = DEFAULT_CONSERVATORY_GENOME_NAME

  if (speciesOptions.value.includes(DEFAULT_SPECIES)) {
    handleSpeciesChange(form.species)
  } else {
    selectFirstAvailableGenome()
  }

  activeJbrowseUrl.value = ''

  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

function openDownload(path) {
  if (!path) {
    ElMessage.warning('Download file is not available')
    return
  }

  const url = resolveJbrowseAssetUri(path)
  const filename = url.split('/').pop() || ''
  const link = document.createElement('a')

  link.href = url
  link.download = filename
  link.rel = 'noopener'
  document.body.appendChild(link)
  link.click()
  link.remove()
}

function resolveJbrowseAssetUri(uri) {
  if (!uri) return ''

  if (/^(https?:)?\/\//.test(uri) || uri.startsWith('data:')) {
    return uri
  }

  if (uri.startsWith('/jbrowse/')) {
    return joinUrl(JBROWSE_BASE_URL, uri.slice('/jbrowse/'.length))
  }

  if (uri.startsWith('/jbrowse-static/')) {
    return joinUrl(JBROWSE_BASE_URL, uri.slice('/jbrowse-static/'.length))
  }

  if (uri.startsWith('/')) {
    return uri
  }

  return joinUrl(JBROWSE_BASE_URL, uri)
}

function downloadGenome() {
  openDownload(downloadLinks.value.fasta)
}

function downloadAnnotation() {
  openDownload(downloadLinks.value.annotation)
}

onMounted(async () => {
  await fetchGenomeOptions()

  const speciesExists = speciesOptions.value.includes(DEFAULT_SPECIES)

  if (!speciesExists) {
    if (!selectFirstAvailableGenome()) return
  } else {
    handleSpeciesChange(form.species)
  }

  const defaultGenomeExists = genomeVersionOptions.value.some(
    item => item.conservatory_genome_name === DEFAULT_CONSERVATORY_GENOME_NAME
  )

  if (speciesExists && !defaultGenomeExists) {
    form.conservatory_genome_name = ''

    ElMessage.warning(
      `Default genome version "${DEFAULT_CONSERVATORY_GENOME_NAME}" not found`
    )
    return
  }

  if (jbrowseUrl.value) {
    activeJbrowseUrl.value = jbrowseUrl.value
    iframeKey.value += 1
  }
})
</script>

<style scoped>
.jbrowse-page,
.jbrowse-page * {
  box-sizing: border-box;
}

.jbrowse-page {
  width: 100%;
  max-width: 100%;
  min-height: 100vh;
  padding: 24px;
  display: flex;
  justify-content: center;
  background: #f5f9fc;
  color: #1f2937;
  overflow-x: hidden;
}

.page-container {
  width: 100%;
  max-width: 1600px;
  min-width: 0;
}

/* Section Card */
.section-card {
  position: relative;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  margin: 0 0 24px;
  padding: 78px 30px 32px;
  background: #ffffff;
  border: 1px solid #dfe7ef;
  border-radius: 8px;
  box-shadow: 0 3px 14px rgba(33, 52, 71, 0.06);
}

.section-label {
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

.section-label::before {
  content: '';
  position: absolute;
  left: 0;
  bottom: -10px;
  width: 0;
  height: 0;
  border-top: 10px solid #a1d0dd;
  border-left: 10px solid transparent;
}

/* Search */
.search-card {
  min-height: 235px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-form {
  width: 100%;
  max-width: 700px;
  min-width: 0;
  margin: 0 auto;
}

.form-grid {
  display: flex;
  justify-content: center;
  gap: 50px;
  flex-wrap: nowrap;
  min-width: 0;
}

.grid-item {
  width: 300px;
  flex: 0 0 300px;
  margin-bottom: 0;
  min-width: 0;
}

.form-actions {
  margin-top: 28px;
  display: flex;
  justify-content: center;
  gap: 14px;
}

/* Element Plus */
:deep(.el-form-item__label) {
  color: #1f2937;
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 8px;
}

:deep(.el-form-item.is-required:not(.is-no-asterisk).asterisk-left > .el-form-item__label::before) {
  color: #f56c6c;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  height: 42px;
  min-height: 42px;
  box-sizing: border-box;
  align-items: center;
  box-shadow: 0 0 0 1px #dce3eb inset;
}

:deep(.italic-select .el-select__selected-item),
:deep(.italic-select .el-select__placeholder),
:deep(.italic-select .el-tag__content) {
  font-style: italic;
}

:deep(.gene-select-popper .el-select-dropdown__wrap) {
  max-height: 135px;
}

/* Browser */
.browser-card {
  padding-top: 64px;
}

.current-genome-line {
  width: calc(100% - 118px);
  max-width: calc(100% - 118px);
  min-width: 0;
  margin: -28px 0 14px 118px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 9px;
  font-size: 15px;
  overflow-wrap: anywhere;
}

.current-label {
  color: #1f2937;
  font-weight: 600;
  flex: 0 0 auto;
}

.current-link {
  color: #2d7eea;
  font-weight: 500;
  min-width: 0;
  overflow-wrap: anywhere;
}

.divider {
  color: #a0a8b3;
  flex: 0 0 auto;
}

.jbrowse-browser-box {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  margin-top: 30px;
  border: 1px solid #d8e1ea;
  border-radius: 6px;
  overflow: hidden;
  background: #ffffff;
}

.jbrowse-frame-box {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  padding: 10px;
  background: #ffffff;
  overflow: hidden;
}

.jbrowse-frame {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  height: 550px;
  border: none;
  border-radius: 4px;
  display: block;
  overflow: hidden;
}

.jbrowse-download-bar {
  width: 100%;
  max-width: 100%;
  min-height: 46px;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 10px;
  border-top: 1px solid #e1e8f0;
  background: #fbfdff;
}

.jbrowse-download-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.toolbar-label {
  color: #2d7eea;
  font-size: 15px;
  font-weight: 500;
  margin-right: 4px;
}

.empty-browser-box {
  width: 100%;
  max-width: 100%;
  min-height: 260px;
  margin-top: 30px;
  border: 1px dashed #d8e1ea;
  border-radius: 6px;
  background: #fbfdff;
  color: #606266;
  font-size: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 20px;
}

/* Genome Info: 如果这个页面暂时没用到，可以保留 */
.genome-info-card {
  padding-top: 64px;
}

.genome-label {
  min-width: 136px;
}

.info-box {
  display: grid;
  grid-template-columns: 1.2fr 1.2fr 1.2fr 2fr;
  gap: 0;
  border: 1px solid #e1e8f0;
  border-radius: 8px;
  background: #ffffff;
  overflow: hidden;
}

.info-item {
  min-height: 108px;
  padding: 22px 22px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-right: 1px solid #e1e8f0;
}

.info-item:last-child {
  border-right: none;
}

.info-icon {
  width: 54px;
  height: 54px;
  flex: 0 0 54px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eef8ff;
  border: 1px solid #d6ecff;
  border-radius: 50%;
  color: #2d7eea;
  font-size: 25px;
}

.plant-icon {
  color: #2f9e44;
}

.info-title {
  margin-bottom: 8px;
  color: #1f2937;
  font-size: 15px;
  font-weight: 700;
}

.info-value {
  color: #2d7eea;
  font-size: 15px;
  line-height: 1.45;
  word-break: break-word;
}

/* Responsive */
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

  .info-box {
    grid-template-columns: 1fr 1fr;
  }

  .info-item {
    border-bottom: 1px solid #e1e8f0;
  }
}

@media (max-width: 768px) {
  .jbrowse-page {
    padding: 16px;
  }

  .section-card {
    margin: 0 0 20px;
    padding: 82px 18px 28px;
  }

  .section-label {
    font-size: 16px;
    padding: 10px 18px;
  }

  .search-card {
    align-items: stretch;
  }

  .search-form {
    width: 100%;
    max-width: none;
  }

  .form-grid {
    flex-direction: column;
    gap: 0;
  }

  .grid-item {
    width: 100%;
    flex: 0 0 100%;
    margin-bottom: 18px;
  }

  .current-genome-line {
    width: 100%;
    max-width: 100%;
    margin-left: 0;
  }

  .jbrowse-browser-box {
    margin-top: 20px;
  }

  .jbrowse-frame-box {
    padding: 8px;
  }

  .jbrowse-frame {
    height: 520px;
  }

  .jbrowse-download-bar {
    justify-content: flex-start;
  }

  .info-box {
    grid-template-columns: 1fr;
  }

  .info-item {
    border-right: none;
  }
}
</style>
