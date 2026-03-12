<template>
  <el-dialog v-model="visible" :title="title" width="80%" top="5vh" destroy-on-close>
    <div class="preview-content" v-loading="loading">
      <img v-if="type === 'image'" :src="url" style="max-width: 100%; max-height: 70vh;" />
      <iframe v-else-if="type === 'pdf'" :src="url" style="width: 100%; height: 70vh; border: none;"></iframe>
      <pre v-else-if="type === 'text'" class="text-preview">{{ text }}</pre>
      <div v-else class="unsupported-preview">
        <el-result icon="info" title="无法预览此格式" sub-title="为了您的安全，此文件类型不支持在线预览，请下载后查看。">
        </el-result>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useFileCrypto } from '../../composables/useFileCrypto'

const props = defineProps({
  modelValue: Boolean,
  file: Object,
  isShared: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const type = ref('')
const url = ref('')
const text = ref('')
const title = ref('')

const { decryptFileBlob } = useFileCrypto()

watch(() => props.modelValue, async (val) => {
  if (val && props.file) {
    title.value = props.file.name
    await loadPreview()
  } else {
    // Clear resources
    if (url.value) URL.revokeObjectURL(url.value)
    url.value = ''
    text.value = ''
    type.value = ''
  }
})

const loadPreview = async () => {
  loading.value = true
  try {
    const blob = await decryptFileBlob(props.file, props.isShared)
    const ext = props.file.name.split('.').pop().toLowerCase()

    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(ext)) {
      type.value = 'image'
      url.value = URL.createObjectURL(blob)
    } else if (ext === 'pdf') {
      type.value = 'pdf'
      url.value = URL.createObjectURL(blob)
    } else if (['txt', 'md', 'json', 'js', 'html', 'css', 'py', 'java', 'c', 'cpp'].includes(ext)) {
      type.value = 'text'
      text.value = await blob.text()
    } else {
      type.value = 'unsupported'
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('预览失败: ' + (e.message || '未知错误'))
    visible.value = false
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.preview-content {
  min-height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
}
.text-preview {
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 70vh;
  overflow-y: auto;
  width: 100%;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
.unsupported-preview {
    color: #909399;
    font-size: 16px;
}
</style>
