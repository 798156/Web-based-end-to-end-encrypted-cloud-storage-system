<template>
  <el-dialog v-model="visible" title="分享文件" width="400px" destroy-on-close>
    <el-form>
      <el-form-item label="接收者用户名">
        <el-input v-model="recipientUsername" placeholder="请输入对方用户名"></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="handleShare" :loading="sharing">分享</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import CryptoUtils from '../../utils/crypto'

const props = defineProps({
  modelValue: Boolean,
  file: Object
})

const emit = defineEmits(['update:modelValue', 'share-success'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const recipientUsername = ref('')
const sharing = ref(false)

const privateKeyB64 = sessionStorage.getItem('privateKey')

const handleShare = async () => {
  if (!recipientUsername.value) {
    ElMessage.warning('请输入用户名')
    return
  }
  
  sharing.value = true
  try {
    // 1. 获取接收者公钥
    const userRes = await axios.post('/api/users/public_key', { username: recipientUsername.value })
    const recipientPublicKeyB64 = userRes.data.public_key
    const recipientId = userRes.data.user_id
    
    // 2. 解密当前文件的 AES Key (需要先用自己的私钥解开)
    const file = props.file
    
    const privateKeyBuffer = CryptoUtils.base64ToArrayBuffer(privateKeyB64)
    const privateKey = await window.crypto.subtle.importKey(
      "pkcs8",
      privateKeyBuffer,
      { name: "RSA-OAEP", hash: "SHA-256" },
      true,
      ["decrypt"]
    )

    const myEncryptedKeyBuffer = CryptoUtils.base64ToArrayBuffer(file.encrypted_key)
    const decryptedKeyBuffer = await window.crypto.subtle.decrypt(
      { name: "RSA-OAEP" },
      privateKey,
      myEncryptedKeyBuffer
    )
    
    // 3. 用接收者的公钥加密 AES Key
    const recipientPublicKeyBuffer = CryptoUtils.base64ToArrayBuffer(recipientPublicKeyB64)
    const recipientPublicKey = await window.crypto.subtle.importKey(
      "spki",
      recipientPublicKeyBuffer,
      { name: "RSA-OAEP", hash: "SHA-256" },
      true,
      ["encrypt"]
    )

    const sharedEncryptedKey = await window.crypto.subtle.encrypt(
      { name: "RSA-OAEP" },
      recipientPublicKey,
      decryptedKeyBuffer
    )

    // 4. 发送分享请求
    await axios.post('/api/share', {
      file_id: file.id,
      recipient_id: recipientId,
      encrypted_key: CryptoUtils.arrayBufferToBase64(sharedEncryptedKey)
    })

    ElMessage.success('分享成功')
    visible.value = false
    emit('share-success')

  } catch (error) {
    console.error('Share failed:', error)
    if (error.response && error.response.data && error.response.data.error) {
      ElMessage.error(error.response.data.error)
    } else if (error.message) {
      ElMessage.error('分享失败: ' + error.message)
    } else {
      ElMessage.error('分享失败')
    }
  } finally {
    sharing.value = false
  }
}
</script>
