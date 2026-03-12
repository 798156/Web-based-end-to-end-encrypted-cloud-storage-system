<template>
  <div class="dashboard-container">
    <el-card class="dashboard-card">
      <template #header>
        <div class="header-row">
          <div class="header-left">
            <h2>我的云盘</h2>
          </div>
          <div class="header-right">
            <el-input
              v-model="searchQuery"
              placeholder="搜索文件名..."
              prefix-icon="Search"
              style="width: 250px; margin-right: 15px;"
              clearable
            />
            <el-button type="primary" @click="triggerUpload">
              <el-icon><Upload /></el-icon> 上传文件
            </el-button>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeTab" class="dashboard-tabs">
        <el-tab-pane label="我的文件" name="myFiles">
          <file-grid 
            :files="filteredFiles" 
            :loading="loading" 
            :is-shared="false"
            @preview="openPreview"
            @download="handleDownload"
            @share="openShare"
            @delete="handleDelete"
            @rename="handleRename"
          />
        </el-tab-pane>

        <el-tab-pane label="我收到的分享" name="sharedFiles">
          <file-grid 
            :files="sharedFiles" 
            :loading="sharedLoading" 
            :is-shared="true"
            @preview="openPreviewShared"
            @download="handleDownloadShared"
          />
        </el-tab-pane>

        <el-tab-pane label="我发出的分享" name="sentShares">
          <shared-list 
            :shares="sentShares" 
            :loading="sentLoading" 
            @revoke="handleRevokeShare"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 隐藏的上传组件，通过 triggerUpload 触发 -->
    <el-dialog v-model="uploadDialogVisible" title="上传文件" width="500px">
        <file-uploader @upload-success="onUploadSuccess" />
    </el-dialog>

    <preview-dialog 
      v-model="previewVisible" 
      :file="currentFile" 
      :is-shared="isPreviewShared" 
    />

    <share-dialog 
      v-model="shareVisible" 
      :file="currentFile" 
      @share-success="onShareSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Upload } from '@element-plus/icons-vue'
import axios from 'axios'

import FileGrid from '../components/dashboard/FileGrid.vue'
import SharedList from '../components/dashboard/SharedList.vue'
import FileUploader from '../components/dashboard/FileUploader.vue'
import PreviewDialog from '../components/dashboard/PreviewDialog.vue'
import ShareDialog from '../components/dashboard/ShareDialog.vue'
import { useFileCrypto } from '../composables/useFileCrypto'

import CryptoUtils from '../utils/crypto'

const router = useRouter()
const { downloadFile } = useFileCrypto()

// State
const activeTab = ref('myFiles')
const files = ref([])
const sharedFiles = ref([])
const sentShares = ref([])
const loading = ref(false)
const sharedLoading = ref(false)
const sentLoading = ref(false)
const searchQuery = ref('')

const uploadDialogVisible = ref(false)
const previewVisible = ref(false)
const shareVisible = ref(false)
const currentFile = ref(null)
const isPreviewShared = ref(false)

// Computed
const filteredFiles = computed(() => {
  if (!searchQuery.value) return files.value
  return files.value.filter(file => 
    file.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

// Methods
const loadFiles = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/files')
    files.value = processFiles(res.data)
  } catch (error) {
    ElMessage.error('获取文件列表失败')
  } finally {
    loading.value = false
  }
}

const loadSharedFiles = async () => {
  sharedLoading.value = true
  try {
    const res = await axios.get('/api/shared_files')
    sharedFiles.value = processFiles(res.data)
  } catch (error) {
    ElMessage.error('获取分享列表失败')
  } finally {
    sharedLoading.value = false
  }
}

const loadSentShares = async () => {
  sentLoading.value = true
  try {
    const res = await axios.get('/api/sent_shares')
    sentShares.value = res.data.map(share => {
        let fileName = "未知文件"
        try {
            fileName = CryptoUtils.base64ToUnicode(share.encrypted_name)
        } catch (e) {
            fileName = "解密失败"
        }
        return {
            ...share,
            name: fileName,
            created_at: new Date(share.created_at).toLocaleString()
        }
    })
  } catch (error) {
    ElMessage.error('获取已分享列表失败')
  } finally {
    sentLoading.value = false
  }
}

const processFiles = (data) => {
  return data.map(file => {
    let fileName = "未知文件"
    try {
      fileName = CryptoUtils.base64ToUnicode(file.encrypted_name)
    } catch (e) {
      fileName = "解密失败"
    }
    return {
      ...file,
      name: fileName,
      size: (file.size / 1024).toFixed(2) + ' KB',
      date: file.created_at // Keep original for sorting if needed
    }
  })
}

// Upload
const triggerUpload = () => {
  uploadDialogVisible.value = true
}

const onUploadSuccess = () => {
  uploadDialogVisible.value = false
  loadFiles()
}

// Preview
const openPreview = (file) => {
  currentFile.value = file
  isPreviewShared.value = false
  previewVisible.value = true
}

const openPreviewShared = (file) => {
  currentFile.value = file
  isPreviewShared.value = true
  previewVisible.value = true
}

// Download
const handleDownload = (file) => {
  downloadFile(file, false)
}

const handleDownloadShared = (file) => {
  downloadFile(file, true)
}

// Share
const openShare = (file) => {
  currentFile.value = file
  shareVisible.value = true
}

const onShareSuccess = () => {
  // Maybe refresh something if needed
}

// Delete
const handleDelete = async (file) => {
  try {
    await axios.delete(`/api/files/${file.id}`)
    ElMessage.success('文件已删除')
    loadFiles()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// Watchers
watch(activeTab, (val) => {
  if (val === 'myFiles') {
    loadFiles()
  } else if (val === 'sharedFiles') {
    loadSharedFiles()
  } else if (val === 'sentShares') {
    loadSentShares()
  }
})

const handleRevokeShare = async (share) => {
  try {
    await axios.delete(`/api/shares/${share.id}`)
    ElMessage.success('撤销分享成功')
    loadSentShares()
  } catch (error) {
    ElMessage.error('撤销失败')
  }
}

// Rename
const handleRename = async (file) => {
    try {
        const { value: newName } = await ElMessageBox.prompt('请输入新文件名', '重命名', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            inputValue: file.name
        })
        
        if (newName && newName !== file.name) {
            // Encrypt new name
            const encryptedName = CryptoUtils.unicodeToBase64(newName)
            await axios.put(`/api/files/${file.id}/rename`, {
                encrypted_name: encryptedName
            })
            ElMessage.success('重命名成功')
            loadFiles()
        }
    } catch (e) {
        if (e !== 'cancel') ElMessage.error('重命名失败')
    }
}

onMounted(() => {
  loadFiles()
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}
.dashboard-card {
  min-height: 80vh;
}
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-left h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}
.header-right {
  display: flex;
  align-items: center;
}
.dashboard-tabs {
  margin-top: 10px;
}
</style>
