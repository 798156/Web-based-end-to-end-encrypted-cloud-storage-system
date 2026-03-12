<template>
  <div class="audit-log-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button icon="ArrowLeft" @click="$router.push('/dashboard')">返回云盘</el-button>
            <span class="title">安全审计日志</span>
          </div>
        </div>
      </template>

      <el-table :data="logs" style="width: 100%" v-loading="loading">
        <el-table-column label="时间" prop="created_at" width="180" />
        <el-table-column label="动作" prop="action" width="150">
          <template #default="scope">
            <el-tag :type="getActionType(scope.row.action)">{{ scope.row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="详情" prop="details" />
        <el-table-column label="IP地址" prop="ip" width="150" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const logs = ref([])
const loading = ref(false)

const getActionType = (action) => {
  switch (action) {
    case 'UPLOAD': return 'success'
    case 'DOWNLOAD': return 'info'
    case 'DELETE': return 'danger'
    case 'SHARE': return 'warning'
    case 'RESTORE': return 'primary'
    case 'PERMANENT_DELETE': return 'danger'
    default: return 'info'
  }
}

const loadLogs = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/logs')
    logs.value = res.data.map(log => ({
      ...log,
      created_at: new Date(log.created_at).toLocaleString()
    }))
  } catch (error) {
    ElMessage.error('加载日志失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.audit-log-container {
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
