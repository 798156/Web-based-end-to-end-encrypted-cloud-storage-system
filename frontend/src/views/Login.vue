<template>
  <div class="auth-container">
    <!-- 矩阵数字雨背景 -->
    <MatrixRain />
    
    <el-card class="auth-card" shadow="always">
      <template #header>
        <div class="card-header">
          <div class="logo-icon">
            <el-icon :size="40" color="#0F0"><Lock /></el-icon>
          </div>
          <h2 class="matrix-text">系统接入</h2>
          <p class="subtitle">端对端加密存储 · 安全初始化</p>
        </div>
      </template>
      <el-form :model="form" label-width="0" size="large">
        <el-form-item>
          <el-input 
            v-model="form.username" 
            placeholder="请输入用户名" 
            prefix-icon="User" 
            class="matrix-input"
          />
        </el-form-item>
        <el-form-item>
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="请输入密码" 
            prefix-icon="Lock" 
            show-password 
            class="matrix-input"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" style="width: 100%" class="matrix-btn">
            登录系统
          </el-button>
        </el-form-item>
        <div class="links">
          <span style="color: #0F0; margin-right: 5px;">新用户？</span>
          <router-link to="/register">建立连接</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import axios from 'axios'
import CryptoUtils from '../utils/crypto'
import MatrixRain from '../components/MatrixRain.vue'

const router = useRouter()
const loading = ref(false)
const form = ref({
  username: '',
  password: ''
})

// ... (keep logic same)
const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    // 1. 获取 Salt
    const saltRes = await axios.post('/api/get_salt', { username: form.value.username })
    const salt = saltRes.data.salt

    // 2. 计算 Auth Hash
    const encoder = new TextEncoder()
    const data = encoder.encode(form.value.password + salt)
    const hashBuffer = await window.crypto.subtle.digest('SHA-256', data)
    const authHash = CryptoUtils.arrayBufferToHex(hashBuffer)

    // 3. 登录请求
    const loginRes = await axios.post('/api/login', {
      username: form.value.username,
      auth_hash: authHash
    })

    const loginData = loginRes.data

    // 4. 解密私钥
    const masterKey = await CryptoUtils.deriveKeyFromPassword(form.value.password, CryptoUtils.hexToArrayBuffer(salt))
    const encryptedPrivateKeyCombined = CryptoUtils.base64ToArrayBuffer(loginData.encrypted_private_key)
    const iv = encryptedPrivateKeyCombined.slice(0, 12)
    const encryptedData = encryptedPrivateKeyCombined.slice(12)

    const privateKeyBuffer = await window.crypto.subtle.decrypt(
      { name: "AES-GCM", iv: iv },
      masterKey,
      encryptedData
    )

    // 验证私钥
    await window.crypto.subtle.importKey(
      "pkcs8",
      privateKeyBuffer,
      { name: "RSA-OAEP", hash: "SHA-256" },
      true,
      ["decrypt"]
    )

    // 存储会话
    sessionStorage.setItem('privateKey', CryptoUtils.arrayBufferToBase64(privateKeyBuffer))
    sessionStorage.setItem('publicKey', loginData.public_key)
    
    ElMessage.success('登录成功')
    router.push('/dashboard')

  } catch (error) {
    console.error(error)
    if (error.response && error.response.data && error.response.data.error) {
        ElMessage.error(error.response.data.error)
    } else if (error.message.includes('decrypt')) {
        ElMessage.error('密码错误，无法解密私钥')
    } else {
        ElMessage.error('登录失败')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  position: relative;
  overflow: hidden;
  background-color: #000;
}

.auth-card {
  width: 400px;
  border-radius: 4px;
  background: rgba(0, 20, 0, 0.85); /* 深绿色半透明背景 */
  backdrop-filter: blur(5px);
  box-shadow: 0 0 20px #0F0; /* 绿色发光边框 */
  z-index: 1;
  border: 1px solid #0F0;
}

.auth-card:hover {
  box-shadow: 0 0 40px #0F0;
}

.card-header {
  text-align: center;
}

.logo-icon {
  margin-bottom: 10px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.1); opacity: 1; }
  100% { transform: scale(1); opacity: 0.8; }
}

.matrix-text {
  margin: 0;
  color: #0F0;
  font-family: 'Courier New', Courier, monospace;
  letter-spacing: 2px;
  text-shadow: 0 0 5px #0F0;
}

.subtitle {
  margin: 5px 0 0;
  color: #0F0;
  font-family: 'Courier New', Courier, monospace;
  font-size: 12px;
  opacity: 0.8;
}

/* 覆盖 Element Plus 输入框样式 */
.matrix-input :deep(.el-input__wrapper) {
  background-color: rgba(0, 0, 0, 0.5);
  box-shadow: 0 0 0 1px #0F0 inset;
  border-radius: 0;
}

.matrix-input :deep(.el-input__inner) {
  color: #0F0;
  font-family: 'Courier New', Courier, monospace;
}

.matrix-input :deep(.el-input__inner::placeholder) {
  color: rgba(0, 255, 0, 0.5);
}

.matrix-btn {
  background-color: #000;
  border: 1px solid #0F0;
  color: #0F0;
  font-family: 'Courier New', Courier, monospace;
  font-weight: bold;
  letter-spacing: 2px;
  border-radius: 0;
  transition: all 0.3s;
}

.matrix-btn:hover {
  background-color: #0F0;
  color: #000;
  box-shadow: 0 0 15px #0F0;
}

.links {
  text-align: center;
  margin-top: 10px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 12px;
}

.links a {
  color: #0F0;
  text-decoration: none;
  font-weight: bold;
  text-shadow: 0 0 2px #0F0;
}

.links a:hover {
  text-decoration: underline;
  box-shadow: 0 0 5px #0F0;
}
</style>

