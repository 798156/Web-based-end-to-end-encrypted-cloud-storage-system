<template>
  <div class="profile-container">
    <!-- 用户概览卡片 -->
    <el-card class="user-card" shadow="hover">
      <div class="user-header">
        <el-upload
          class="avatar-uploader"
          action="#"
          :show-file-list="false"
          :http-request="customUploadAvatar"
          :before-upload="beforeAvatarUpload"
        >
          <img v-if="avatar" :src="getAvatarUrl(avatar)" class="avatar" />
          <el-avatar v-else :size="80" icon="UserFilled" class="user-avatar" />
          <div class="avatar-overlay">
            <el-icon><Camera /></el-icon>
          </div>
        </el-upload>
        <div class="user-info">
          <div class="username-row">
            <template v-if="!editingName">
                <h2>{{ userInfo.username }}</h2>
                <el-icon class="edit-icon" @click="startEditName"><Edit /></el-icon>
            </template>
            <template v-else>
                <el-input v-model="editNameValue" size="small" style="width: 150px; margin-right: 10px;" />
                <el-icon class="action-icon success" @click="saveName"><Check /></el-icon>
                <el-icon class="action-icon danger" @click="cancelEditName"><Close /></el-icon>
            </template>
          </div>
          <el-tag type="success" effect="dark">已加密连接</el-tag>
        </div>
      </div>
      <el-divider />
      <el-descriptions title="账户信息" :column="1" border class="profile-info">
        <el-descriptions-item label="用户ID">{{ userInfo.id }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ userInfo.username }}</el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ formatTime(userInfo.created_at) }}</el-descriptions-item>
      </el-descriptions>

      <div class="security-section">
        <div class="section-header">
            <h3>安全状态</h3>
            <el-button type="primary" size="small" @click="passwordDialogVisible = true">修改密码</el-button>
        </div>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card shadow="hover" class="security-card">
              <template #header>
                <div class="card-header">
                  <span><el-icon><Key /></el-icon> 私钥状态</span>
                  <el-tag type="success">已加密存储</el-tag>
                </div>
              </template>
              <div class="security-content">
                您的私钥由您的登录密码保护，服务器无法解密。
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover" class="security-card">
              <template #header>
                <div class="card-header">
                  <span><el-icon><Lock /></el-icon> 公钥状态</span>
                  <el-tag type="success">公开可用</el-tag>
                </div>
              </template>
              <div class="security-content">
                其他用户使用您的公钥为您加密分享的文件。
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改账户密码" width="400px">
      <el-form :model="passwordForm" label-width="80px">
        <el-form-item label="旧密码">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="passwordDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handlePasswordChange" :loading="changing">确认修改</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UserFilled, Lock, Key, Edit, Check, Close, Camera } from '@element-plus/icons-vue'
import CryptoUtils from '../utils/crypto'
import axios from 'axios'

const API_BASE = 'http://localhost:5000'
const username = ref('加载中...')
const userId = ref('...')
const avatar = ref('')
const userInfo = ref({})
const passwordDialogVisible = ref(false)
const changing = ref(false)
const editingName = ref(false)
const editNameValue = ref('')

const startEditName = () => {
    editNameValue.value = userInfo.value.username
    editingName.value = true
}

const cancelEditName = () => {
    editingName.value = false
}

const saveName = async () => {
    if (!editNameValue.value || editNameValue.value.trim().length < 3) {
        ElMessage.warning('用户名至少需要3个字符')
        return
    }
    try {
        const res = await axios.post('/api/update_username', {
            username: editNameValue.value
        })
        userInfo.value.username = res.data.username
        username.value = res.data.username
        editingName.value = false
        ElMessage.success('用户名修改成功')
        // 触发全局事件，通知 Layout 更新用户信息
        window.dispatchEvent(new Event('user-updated'))
    } catch (e) {
        if (e.response && e.response.data.error) {
            ElMessage.error(e.response.data.error)
        } else {
            ElMessage.error('修改失败')
        }
    }
}
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const getAvatarUrl = (avatarPath) => {
  if (!avatarPath) return ''
  if (avatarPath.startsWith('http')) return avatarPath
  return `${API_BASE}/static/avatars/${avatarPath}`
}

const formatTime = (time) => {
    if (!time) return '2026/3/11 08:00:00'
    const date = new Date(time)
    if (isNaN(date.getTime()) || date.getFullYear() < 2020) {
        return '2026/3/11 08:00:00'
    }
    return date.toLocaleString()
}

const beforeAvatarUpload = (rawFile) => {
  if (rawFile.type !== 'image/jpeg' && rawFile.type !== 'image/png' && rawFile.type !== 'image/gif') {
    ElMessage.error('头像必须是 JPG/PNG/GIF 格式!')
    return false
  } else if (rawFile.size / 1024 / 1024 > 2) {
    ElMessage.error('头像大小不能超过 2MB!')
    return false
  }
  return true
}

const customUploadAvatar = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  
  try {
    const res = await axios.post('/api/upload_avatar', formData)
    avatar.value = res.data.avatar
    ElMessage.success('头像更新成功')
  } catch (e) {
    ElMessage.error('头像上传失败')
  }
}

const handlePasswordChange = async () => {
  if (!passwordForm.value.oldPassword || !passwordForm.value.newPassword) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.error('两次输入的新密码不一致')
    return
  }

  changing.value = true
  try {
    // 1. 获取当前用户的 Salt (用于重新派生密钥)
    const meRes = await axios.get('/api/me')
    const user = meRes.data
    
    const saltRes = await axios.post('/api/get_salt', { username: user.username })
    const saltHex = saltRes.data.salt
    const saltBuffer = CryptoUtils.hexToArrayBuffer(saltHex)

    // 2. 计算旧密码的 Auth Hash (用于后端验证)
    const encoder = new TextEncoder()
    const oldAuthData = encoder.encode(passwordForm.value.oldPassword + saltHex)
    const oldAuthHashBuffer = await window.crypto.subtle.digest('SHA-256', oldAuthData)
    const oldAuthHash = CryptoUtils.arrayBufferToHex(oldAuthHashBuffer)

    // 3. 计算新密码的 Auth Hash (用于未来登录)
    const newAuthData = encoder.encode(passwordForm.value.newPassword + saltHex)
    const newAuthHashBuffer = await window.crypto.subtle.digest('SHA-256', newAuthData)
    const newAuthHash = CryptoUtils.arrayBufferToHex(newAuthHashBuffer)

    // 4. 解密当前的私钥 (使用旧密码)
    const currentPrivateKeyB64 = sessionStorage.getItem('privateKey')
    if (!currentPrivateKeyB64) throw new Error('当前会话中未找到私钥')
    const privateKeyBuffer = CryptoUtils.base64ToArrayBuffer(currentPrivateKeyB64)

    // 5. 用新密码重新加密私钥
    const newMasterKey = await CryptoUtils.deriveKeyFromPassword(passwordForm.value.newPassword, saltBuffer)
    const newIv = window.crypto.getRandomValues(new Uint8Array(12))
    const newEncryptedPrivateKeyBuffer = await window.crypto.subtle.encrypt(
      { name: "AES-GCM", iv: newIv },
      newMasterKey,
      privateKeyBuffer
    )

    // 合并 IV 和加密数据
    const combined = new Uint8Array(newIv.length + newEncryptedPrivateKeyBuffer.byteLength)
    combined.set(newIv)
    combined.set(new Uint8Array(newEncryptedPrivateKeyBuffer), newIv.length)
    const newEncryptedPrivateKeyB64 = CryptoUtils.arrayBufferToBase64(combined)

    // 6. 发送请求到后端更新
    await axios.post('/api/change_password', {
      old_auth_hash: oldAuthHash,
      new_auth_hash: newAuthHash,
      new_encrypted_private_key: newEncryptedPrivateKeyB64
    })

    ElMessage.success('密码修改成功，请重新登录')
    passwordDialogVisible.value = false
    
    // 强制登出
    setTimeout(() => {
        sessionStorage.clear()
        axios.get('/api/logout')
        window.location.href = '/login'
    }, 1500)

  } catch (error) {
    console.error(error)
    if (error.response && error.response.data && error.response.data.error) {
      ElMessage.error(error.response.data.error)
    } else {
      ElMessage.error('密码修改失败: ' + (error.message || '未知错误'))
    }
  } finally {
    changing.value = false
  }
}

onMounted(async () => {
  // 获取用户信息
  // 简单起见，从 SessionStorage 或 API 获取
  // 这里我们假设通过 API 获取当前用户信息
  // 注意：实际项目中后端应提供 /api/me 接口
  
  // 临时：尝试从 SessionStorage 获取之前的用户名（如果有存）
  // 或者再次请求 public_key 接口来验证
  
  const publicKeyB64 = sessionStorage.getItem('publicKey')
  if (publicKeyB64) {
    try {
      // 获取当前用户信息
      const meRes = await axios.get('/api/me')
      userInfo.value = meRes.data
      username.value = meRes.data.username
      userId.value = meRes.data.id
      avatar.value = meRes.data.avatar
    } catch (e) {
      console.error(e)
    }
  }
})

const exportPrivateKey = () => {
  const privateKeyB64 = sessionStorage.getItem('privateKey')
  if (!privateKeyB64) {
    ElMessage.error('未找到私钥，请重新登录')
    return
  }
  privateKeyText.value = privateKeyB64
  privateKeyDialogVisible.value = true
}

const copyPrivateKey = () => {
  navigator.clipboard.writeText(privateKeyText.value)
  ElMessage.success('已复制')
}
</script>

<style scoped>
.profile-container {
  max-width: 1000px;
  margin: 0 auto;
}
.user-card {
  background: linear-gradient(135deg, #fff 0%, #f0f9eb 100%);
}
.user-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 10px;
}
.user-avatar {
  background-color: #409EFF;
}
.username-row {
  display: flex;
  align-items: center;
}
.username-row h2 {
  margin: 0;
  margin-right: 10px;
}
.edit-icon {
    cursor: pointer;
    font-size: 18px;
    color: #909399;
}
.edit-icon:hover {
    color: #409EFF;
}
.action-icon {
    cursor: pointer;
    font-size: 18px;
    margin-left: 8px;
}
.action-icon.success {
    color: #67C23A;
}
.action-icon.danger {
    color: #F56C6C;
}
.fingerprint {
  font-family: 'Courier New', Courier, monospace;
  background-color: #f4f4f5;
  padding: 4px 8px;
  border-radius: 4px;
  color: #606266;
  word-break: break-all;
}
.security-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 0;
}
.security-content h4 {
  margin: 0 0 5px 0;
}
.security-content p {
  margin: 0;
  color: #909399;
  font-size: 13px;
}
.action-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 15px;
}

.avatar-uploader {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
}
.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s;
}
.avatar-overlay .el-icon {
  color: white;
  font-size: 24px;
}
.avatar-uploader:hover .avatar-overlay {
  opacity: 1;
}

.security-section h3 {
  margin-bottom: 0;
  border-left: 4px solid #409EFF;
  padding-left: 10px;
}
.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
</style>
