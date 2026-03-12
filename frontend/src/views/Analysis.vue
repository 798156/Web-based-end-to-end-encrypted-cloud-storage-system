<template>
  <div class="analysis-container">
    <!-- 顶部概览卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon bg-blue">
            <el-icon :size="30" color="white"><Files /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-label">文件总数</p>
            <h2 class="stat-value">{{ fileCount }}</h2>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon bg-green">
            <el-icon :size="30" color="white"><Coin /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-label">已用空间</p>
            <h2 class="stat-value">{{ formatBytes(totalSize) }}</h2>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon bg-purple">
            <el-icon :size="30" color="white"><PieChart /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-label">空间使用率</p>
            <h2 class="stat-value">{{ storagePercentage }}%</h2>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>📦 存储配额</h3>
              <el-tag type="info" effect="plain">1GB 总量</el-tag>
            </div>
          </template>
          <div class="storage-stats">
            <el-progress 
              type="dashboard" 
              :percentage="storagePercentage" 
              :color="colors" 
              :width="200"
              :stroke-width="15"
            >
              <template #default="{ percentage }">
                <span class="percentage-value">{{ percentage }}%</span>
                <span class="percentage-label">已使用</span>
              </template>
            </el-progress>
            <div class="progress-footer">
              <p>剩余空间: <strong>{{ formatBytes(TOTAL_QUOTA - totalSize) }}</strong></p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <h3>📊 文件类型分布</h3>
            </div>
          </template>
          <div ref="chartDom" style="width: 100%; height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Files, Coin, PieChart } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import axios from 'axios'

const chartDom = ref(null)
const totalSize = ref(0)
const fileCount = ref(0)
const typeData = ref([])

// 假设总空间配额为 1GB (演示用)
const TOTAL_QUOTA = 1024 * 1024 * 1024 

const storagePercentage = computed(() => {
  if (totalSize.value === 0) return 0
  const pct = Math.round((totalSize.value / TOTAL_QUOTA) * 100)
  return Math.min(pct, 100)
})

const colors = [
  { color: '#5cb87a', percentage: 60 },
  { color: '#e6a23c', percentage: 80 },
  { color: '#f56c6c', percentage: 100 }
]

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const initChart = () => {
  if (!chartDom.value) return
  
  const myChart = echarts.init(chartDom.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      bottom: '5%',
      left: 'center'
    },
    series: [
      {
        name: '文件类型',
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '20',
            fontWeight: 'bold'
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        labelLine: {
          show: false
        },
        data: typeData.value,
        animationType: 'scale',
        animationEasing: 'elasticOut',
        animationDelay: function (idx) {
          return Math.random() * 200;
        }
      }
    ]
  }
  myChart.setOption(option)
  
  // 响应式调整
  window.addEventListener('resize', () => {
    myChart.resize()
  })
}

onMounted(async () => {
  try {
    const res = await axios.get('/api/analysis')
    // 使用简单的动画过渡效果 (requestAnimationFrame 可以做更复杂的)
    totalSize.value = res.data.total_size || 0
    fileCount.value = res.data.file_count || 0
    typeData.value = res.data.type_distribution || []
    
    initChart()
  } catch (error) {
    console.error('Failed to load analysis data', error)
  }
})
</script>

<style scoped>
.analysis-container {
  max-width: 1200px;
  margin: 0 auto;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 8px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 10px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 20px;
}

.bg-blue { background: linear-gradient(135deg, #36D1DC, #5B86E5); }
.bg-green { background: linear-gradient(135deg, #11998e, #38ef7d); }
.bg-purple { background: linear-gradient(135deg, #8E2DE2, #4A00E0); }

.stat-info {
  flex: 1;
}

.stat-label {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.stat-value {
  color: #303133;
  font-size: 24px;
  margin: 5px 0 0 0;
  font-weight: bold;
}

.chart-card {
  height: 100%;
}

.storage-stats {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px 0;
}

.percentage-value {
  display: block;
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.percentage-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.progress-footer {
  margin-top: 20px;
  text-align: center;
  color: #606266;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-header h3 {
  margin: 0;
}
</style>
