<template>
  <div class="recycle-bin-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button icon="ArrowLeft" @click="$router.push('/dashboard')">返回云盘</el-button>
            <span class="title">回收站</span>
          </div>
          <el-button type="danger" plain @click="clearAll" :disabled="!files.length">清空回收站</el-button>
        </div>
      </template>

      <el-table :data="files" style="width: 100%" v-loading="loading">
        <el-table-column label="文件名" prop="name">
          <template #default="scope">
            <el-icon><Document /></el-icon> {{ scope.row.name }}
          </template>
        </el-table-column>
        <el-table-column label="大小" prop="size" width="120" />
        <el-table-column label="删除时间" prop="deleted_at" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" type="primary" @click="restoreFile(scope.row)">还原</el-button>
            <el-popconfirm title="确定彻底删除吗？无法恢复！" @confirm="permanentDelete(scope.row)">
              <template #reference>
                <el-button size="small" type="danger">彻底删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, ArrowLeft } from '@element-plus/icons-vue'
import axios from 'axios'
import CryptoUtils from '../utils/crypto'

const router = useRouter()
const files = ref([])
const loading = ref(false)

const loadFiles = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/recycle_bin')
    files.value = res.data.map(file => {
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
        deleted_at: new Date(file.deleted_at).toLocaleString()
      }
    })
  } catch (error) {
    ElMessage.error('加载回收站失败')
  } finally {
    loading.value = false
  }
}

const restoreFile = async (file) => {
  try {
    await axios.post(`/api/files/${file.id}/restore`)
    ElMessage.success('文件已还原')
    loadFiles()
  } catch (error) {
    ElMessage.error('还原失败')
  }
}

const permanentDelete = async (file) => {
  try {
    await axios.delete(`/api/files/${file.id}/permanent`)
    ElMessage.success('文件已彻底删除')
    loadFiles()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const clearAll = async () => {
  try {
    await ElMessageBox.confirm('确定要清空回收站吗？此操作不可恢复！', '警告', {
      confirmButtonText: '确定清空',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 由于后端没有批量接口，前端循环调用（临时方案）
    // 理想情况应添加 /api/recycle_bin/clear 接口
    const promises = files.value.map(file => axios.delete(`/api/files/${file.id}/permanent`))
    await Promise.all(promises)
    
    ElMessage.success('回收站已清空')
    loadFiles()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('清空失败')
  }
}

onMounted(() => {
  loadFiles()
})
</script>

<style scoped>
.recycle-bin-container {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}
.title {
  font-size: 18px;
  font-weight: bold;
}
</style>
