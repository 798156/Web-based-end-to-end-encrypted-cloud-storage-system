import axios from 'axios'
import CryptoUtils from '../utils/crypto'
import { ElMessage } from 'element-plus'

export function useFileCrypto() {
  const decryptFileBlob = async (file, isShared = false) => {
    const privateKeyB64 = sessionStorage.getItem('privateKey')
    if (!privateKeyB64) {
      throw new Error('未检测到安全密钥，请尝试重新登录')
    }

    try {
      const apiUrl = isShared ? `/api/download_shared/${file.id}` : `/api/download/${file.id}`
      const res = await axios.get(apiUrl, { responseType: 'blob' })
      const encryptedBuffer = await res.data.arrayBuffer()

      const privateKeyBuffer = CryptoUtils.base64ToArrayBuffer(privateKeyB64)
      const privateKey = await window.crypto.subtle.importKey(
        "pkcs8",
        privateKeyBuffer,
        { name: "RSA-OAEP", hash: "SHA-256" },
        true,
        ["decrypt"]
      )

      const encryptedKeyBuffer = CryptoUtils.base64ToArrayBuffer(file.encrypted_key)
      let decryptedKeyBuffer;
      try {
        decryptedKeyBuffer = await window.crypto.subtle.decrypt(
            { name: "RSA-OAEP" },
            privateKey,
            encryptedKeyBuffer
        )
      } catch (e) {
          throw new Error('解密密钥失败。这通常是因为该文件是用旧的密钥对加密的。')
      }

      const fileKey = await window.crypto.subtle.importKey(
        "raw",
        decryptedKeyBuffer,
        { name: "AES-GCM" },
        true,
        ["decrypt"]
      )

      const iv = CryptoUtils.hexToArrayBuffer(file.iv)
      const decryptedBuffer = await window.crypto.subtle.decrypt(
        { name: "AES-GCM", iv: iv },
        fileKey,
        encryptedBuffer
      )

      return new Blob([decryptedBuffer])
    } catch (error) {
      console.error('Decryption failed:', error)
      throw error
    }
  }

  const downloadFile = async (file, isShared = false) => {
    try {
      const blob = await decryptFileBlob(file, isShared)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.name
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      ElMessage.error('解密下载失败: ' + (error.message || '未知错误'))
    }
  }

  return {
    decryptFileBlob,
    downloadFile
  }
}
