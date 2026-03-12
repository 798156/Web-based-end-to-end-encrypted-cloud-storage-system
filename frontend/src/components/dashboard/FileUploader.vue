<template>
  <div class="file-uploader">
    <el-upload
      class="upload-demo"
      action="#"
      :http-request="customUpload"
      :show-file-list="false"
      :disabled="uploading"
      drag
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        拖拽文件到此处或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持任意文件格式 (PNG, JPG, DOCX, PDF, MP4 等)，全程加密传输
        </div>
      </template>
    </el-upload>
    
    <!-- 进度条 -->
    <el-progress 
      v-if="uploading" 
      :percentage="uploadProgress" 
      :status="uploadStatus"
      class="upload-progress"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'
import CryptoUtils from '../../utils/crypto'

const emit = defineEmits(['upload-success'])

const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')

const privateKeyB64 = sessionStorage.getItem('privateKey')
const publicKeyB64 = sessionStorage.getItem('publicKey')

const customUpload = async (options) => {
  const file = options.file
  uploading.value = true
  uploadProgress.value = 0
  uploadStatus.value = ''
  
  try {
    // 1. 生成文件 AES 密钥
    uploadProgress.value = 10
    const fileKey = await window.crypto.subtle.generateKey(
      { name: "AES-GCM", length: 256 },
      true,
      ["encrypt", "decrypt"]
    )

    // 2. 加密文件内容
    uploadProgress.value = 30
    const fileBuffer = await file.arrayBuffer()
    const iv = window.crypto.getRandomValues(new Uint8Array(12))
    const encryptedContent = await window.crypto.subtle.encrypt(
      { name: "AES-GCM", iv: iv },
      fileKey,
      fileBuffer
    )

    // 3. 加密文件密钥 (用公钥)
    uploadProgress.value = 60
    const publicKeyBuffer = CryptoUtils.base64ToArrayBuffer(publicKeyB64)
    const publicKey = await window.crypto.subtle.importKey(
      "spki",
      publicKeyBuffer,
      { name: "RSA-OAEP", hash: "SHA-256" },
      true,
      ["encrypt"]
    )

    const exportedFileKey = await window.crypto.subtle.exportKey("raw", fileKey)
    const encryptedFileKey = await window.crypto.subtle.encrypt(
      { name: "RSA-OAEP" },
      publicKey,
      exportedFileKey
    )

    // 4. 上传
    uploadProgress.value = 80
    const formData = new FormData()
    const encryptedBlob = new Blob([encryptedContent], { type: 'application/octet-stream' })
    formData.append('file', encryptedBlob)
    // 使用 unicodeToBase64 支持中文文件名
    formData.append('encrypted_name', CryptoUtils.unicodeToBase64(file.name))
    formData.append('encrypted_key', CryptoUtils.arrayBufferToBase64(encryptedFileKey))
    formData.append('iv', CryptoUtils.arrayBufferToHex(iv))

    await axios.post('/api/upload', formData, {
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        // 映射 80-100%
        if (percentCompleted < 100) {
           uploadProgress.value = 80 + Math.floor(percentCompleted * 0.1)
        }
      }
    })
    
    uploadProgress.value = 100
    uploadStatus.value = 'success'
    ElMessage.success('上传成功')
    emit('upload-success')
    
  } catch (error) {
    console.error(error)
    uploadStatus.value = 'exception'
    ElMessage.error('上传失败: ' + error.message)
  } finally {
    setTimeout(() => {
        uploading.value = false
        uploadProgress.value = 0
    }, 1500)
  }
}
</script>

<style scoped>
.file-uploader {
  width: 100%;
}
.upload-progress {
  margin-top: 10px;
}
</style>
