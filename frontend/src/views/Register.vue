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
          <h2 class="matrix-text">账户注册</h2>
          <p class="subtitle">安全密钥生成中...</p>
        </div>
      </template>
      <el-form :model="form" label-width="0" size="large">
        <el-form-item>
          <el-input 
            v-model="form.username" 
            placeholder="设置用户名" 
            prefix-icon="User" 
            class="matrix-input"
          />
        </el-form-item>
        <el-form-item>
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="设置密码" 
            prefix-icon="Lock" 
            show-password 
            class="matrix-input"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleRegister" :loading="loading" style="width: 100%" class="matrix-btn">
            立即注册
          </el-button>
        </el-form-item>
        <div class="links">
          <span style="color: #0F0; margin-right: 5px;">已有账号？</span>
          <router-link to="/login">返回登录</router-link>
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
const handleRegister = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    // 1. 生成 Salt
    const salt = window.crypto.getRandomValues(new Uint8Array(16))
    const saltHex = Array.from(salt).map(b => b.toString(16).padStart(2, '0')).join('')

    // 2. 派生主密钥
    const masterKey = await CryptoUtils.deriveKeyFromPassword(form.value.password, salt)

    // 3. 生成 RSA 密钥对
    const keyPair = await window.crypto.subtle.generateKey(
      {
        name: "RSA-OAEP",
        modulusLength: 2048,
        publicExponent: new Uint8Array([1, 0, 1]),
        hash: "SHA-256"
      },
      true,
      ["encrypt", "decrypt"]
    )

    // 4. 导出公钥
    const exportedPublicKey = await window.crypto.subtle.exportKey("spki", keyPair.publicKey)
    const publicKeyBase64 = CryptoUtils.arrayBufferToBase64(exportedPublicKey)

    // 5. 导出并加密私钥
    const exportedPrivateKey = await window.crypto.subtle.exportKey("pkcs8", keyPair.privateKey)
    const iv = window.crypto.getRandomValues(new Uint8Array(12))
    const encryptedPrivateKey = await window.crypto.subtle.encrypt(
      { name: "AES-GCM", iv: iv },
      masterKey,
      exportedPrivateKey
    )

    const encryptedPrivateKeyCombined = new Uint8Array(iv.byteLength + encryptedPrivateKey.byteLength)
    encryptedPrivateKeyCombined.set(iv, 0)
    encryptedPrivateKeyCombined.set(new Uint8Array(encryptedPrivateKey), iv.byteLength)
    const encryptedPrivateKeyBase64 = CryptoUtils.arrayBufferToBase64(encryptedPrivateKeyCombined)

    // 6. 生成 Auth Hash
    const encoder = new TextEncoder()
    const data = encoder.encode(form.value.password + saltHex)
    const hashBuffer = await window.crypto.subtle.digest('SHA-256', data)
    const authHash = CryptoUtils.arrayBufferToHex(hashBuffer)

    // 7. 注册请求
    await axios.post('/api/register', {
      username: form.value.username,
      auth_hash: authHash,
      public_key: publicKeyBase64,
      encrypted_private_key: encryptedPrivateKeyBase64,
      salt: saltHex
    })

    ElMessage.success('注册成功，请登录')
    router.push('/login')

  } catch (error) {
    console.error(error)
    ElMessage.error(error.response?.data?.error || '注册失败')
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

