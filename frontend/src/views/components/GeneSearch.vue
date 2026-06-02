<template>
  <div class="panel-card form-panel">
    <div class="panel-tag">Gene Search</div>

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-position="top"
      class="search-form"
    >
      <el-form-item label="Input your gene(s)" prop="geneIds">
        <el-input
          v-model="form.geneIds"
          type="textarea"
          :autosize="{ minRows: 6, maxRows: 12 }"
          placeholder="Please input gene ID, one per line or separated by comma / semicolon"
          clearable
          class="gene-id-textarea"
        />
      </el-form-item>

      <div class="example-row">
        <span class="example-label">eg.</span>

        <el-link
          v-for="(item, index) in geneExamples"
          :key="item"
          type="primary"
          :underline="false"
          :class="['example-link', `example-link-${index % 4}`]"
          @click="fillGeneExample(item)"
        >
          {{ item }}
        </el-link>
      </div>

      <div class="form-actions">
        <el-button type="primary" plain @click="handleSubmit">
          Submit
        </el-button>

        <el-button type="danger" plain @click="handleReset">
          Reset
        </el-button>

        <el-button
          type="success"
          plain
          :loading="geneListDownloading"
          @click="handleDownloadGeneList"
        >
          <span>Gene list</span>
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const emit = defineEmits(['search', 'reset'])

const formRef = ref()
const geneListDownloading = ref(false)

const form = reactive({
  geneIds: ''
})

const geneExamples = [
  'ACP',
  'BCH1',
  'NIN, Nod22',
  'PNO1-like; RINRK1'
]

const rules = {
  geneIds: [
    {
      required: true,
      message: 'Please input gene ID',
      trigger: 'blur'
    }
  ]
}

const fillGeneExample = value => {
  form.geneIds = value
}

const parseGeneIds = value => {
  return value
    .split(/[\n,;，；\s]+/)
    .map(item => item.trim())
    .filter(Boolean)
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch (error) {
    ElMessage.warning('Please input gene ID')
    return
  }

  const geneIdList = parseGeneIds(form.geneIds)

  if (!geneIdList.length) {
    ElMessage.warning('Please input gene ID')
    return
  }

  emit('search', geneIdList)
}

const handleReset = () => {
  form.geneIds = ''
  formRef.value?.clearValidate()
  emit('reset')
}

const formatGeneList = data => {
  return (Array.isArray(data) ? data : [])
    .map(item => String(item ?? '').trim())
    .filter(Boolean)
}

const handleDownloadGeneList = async () => {
  if (geneListDownloading.value) return

  geneListDownloading.value = true

  try {
    const res = await request.get('/api/genes/unique/')
    const geneList = formatGeneList(res.data.data || [])

    if (!geneList.length) {
      ElMessage.warning('No gene list to download')
      return
    }

    const textContent = `${geneList.join('\n')}\n`

    const blob = new Blob([textContent], {
      type: 'text/plain;charset=utf-8;'
    })

    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')

    link.href = url
    link.setAttribute('download', 'gene_list.txt')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    window.URL.revokeObjectURL(url)
    ElMessage.success('Gene list downloaded')
  } catch (error) {
    console.error('Failed to download gene list:', error)
    ElMessage.error(error?.response?.data?.message || 'Failed to download gene list')
  } finally {
    geneListDownloading.value = false
  }
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

.form-panel {
  min-height: 340px;
  padding: 48px 28px 28px;
  display: flex;
  align-items: center;
  justify-content: center;
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
  margin-top: 20px;
}

.gene-id-textarea {
  width: 100%;
}

.example-row {
  margin-top: -8px;
  margin-bottom: 18px;
  font-size: 15px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.example-label {
  color: #333;
}

.example-link {
  font-size: 14px;
  cursor: pointer;
  font-style: italic;
  font-weight: 500;
  transition: all 0.2s ease;
  margin-top: 5px;
}

.example-link-0 {
  color: #2f5bd3 !important;
}

.example-link-1 {
  color: #0d7b58 !important;
}

.example-link-2 {
  color: #48bbf5 !important;
}

.example-link-3 {
  color: #0f9bbe !important;
}

.example-link:hover {
  transform: translateY(-1px);
  opacity: 0.8;
}

.form-actions {
  margin-top: 28px;
  display: flex;
  justify-content: center;
  gap: 14px;
}

:deep(.el-form-item__label) {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
}

:deep(.el-textarea__inner) {
  font-size: 15px;
  line-height: 1.6;
  font-style: italic;
}

@media (max-width: 768px) {
  .form-panel {
    padding-left: 16px;
    padding-right: 16px;
    padding-top: 44px;
    padding-bottom: 20px;
  }

  .panel-tag {
    font-size: 16px;
    padding: 10px 18px;
  }
}
</style>
