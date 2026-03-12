<template>
  <div class="file-grid" v-loading="loading">
    <el-empty v-if="!files.length && !loading" description="暂无文件" />
    
    <el-row :gutter="20">
      <el-col 
        v-for="file in files" 
        :key="file.id" 
        :xs="24" :sm="12" :md="8" :lg="6" :xl="4"
        class="file-col"
      >
        <el-card class="file-card" shadow="hover">
          <div class="file-icon-container" @click="$emit('preview', file)">
             <el-icon :size="64" :color="getIconColor(file.name)">
               <component :is="getFileIcon(file.name)" />
             </el-icon>
          </div>
          
          <div class="file-info">
            <h3 class="file-name" :title="file.name">{{ file.name }}</h3>
            <div class="file-meta">
              <span>{{ file.size }}</span>
              <span>{{ formatDate(file.created_at) }}</span>
            </div>
          </div>
          
          <div class="file-actions">
            <el-tooltip content="下载" placement="bottom">
              <el-button text circle @click="$emit('download', file)">
                <el-icon :size="18" color="#409EFF"><Download /></el-icon>
              </el-button>
            </el-tooltip>
            
            <el-tooltip content="预览" placement="bottom" v-if="canPreview(file.name)">
              <el-button text circle @click="$emit('preview', file)">
                <el-icon :size="18" color="#67C23A"><View /></el-icon>
              </el-button>
            </el-tooltip>
            
            <template v-if="!isShared">
              <el-tooltip content="重命名" placement="bottom">
                <el-button text circle @click="$emit('rename', file)">
                    <el-icon :size="18" color="#E6A23C"><Edit /></el-icon>
                </el-button>
              </el-tooltip>

              <el-tooltip content="分享" placement="bottom">
                <el-button text circle @click="$emit('share', file)">
                    <el-icon :size="18" color="#909399"><Share /></el-icon>
                </el-button>
              </el-tooltip>
              
              <el-popconfirm title="确定删除吗？" @confirm="$emit('delete', file)">
                <template #reference>
                  <el-button text circle>
                    <el-icon :size="18" color="#F56C6C"><Delete /></el-icon>
                  </el-button>
                </template>
              </el-popconfirm>
            </template>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { Document, Picture, VideoCamera, Headset, Files, Download, View, Share, Delete, Edit } from '@element-plus/icons-vue'

const props = defineProps({
  files: {
    type: Array,
    default: () => []
  },
  loading: Boolean,
  isShared: Boolean
})

defineEmits(['download', 'preview', 'share', 'delete', 'rename'])

const getFileIcon = (fileName) => {
  const ext = fileName.split('.').pop().toLowerCase()
  if (['jpg', 'jpeg', 'png', 'gif'].includes(ext)) return Picture
  if (['mp4', 'webm', 'avi'].includes(ext)) return VideoCamera
  if (['mp3', 'wav'].includes(ext)) return Headset
  if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)) return Files
  return Document
}

const getIconColor = (fileName) => {
  const ext = fileName.split('.').pop().toLowerCase()
  if (['jpg', 'jpeg', 'png', 'gif'].includes(ext)) return '#409EFF'
  if (['pdf'].includes(ext)) return '#F56C6C'
  if (['doc', 'docx'].includes(ext)) return '#409EFF'
  if (['xls', 'xlsx'].includes(ext)) return '#67C23A'
  if (['ppt', 'pptx'].includes(ext)) return '#E6A23C'
  if (['zip', 'rar'].includes(ext)) return '#909399'
  return '#606266'
}

const canPreview = (fileName) => {
  const ext = fileName.split('.').pop().toLowerCase()
  // 扩展可预览的格式列表，但排除 docx/xlsx 等需要复杂渲染的格式
  return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'pdf', 'txt', 'md', 'json', 'js', 'html', 'css', 'py', 'java', 'c', 'cpp'].includes(ext)
}

const formatDate = (dateStr) => {
    if (!dateStr) return ''
    return new Date(dateStr).toLocaleDateString()
}
</script>

<style scoped>
.file-col {
  margin-bottom: 20px;
}
.file-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s;
}
.file-card:hover {
  transform: translateY(-5px);
}
.file-icon-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
  background-color: #f5f7fa;
  cursor: pointer;
  border-radius: 4px;
  margin-bottom: 10px;
}
.file-info {
  text-align: center;
  margin-bottom: 15px;
}
.file-name {
  font-size: 14px;
  font-weight: 600;
  margin: 5px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.file-meta {
  font-size: 12px;
  color: #909399;
  display: flex;
  justify-content: space-between;
  padding: 0 5px;
}
.file-actions {
  display: flex;
  justify-content: space-around;
  border-top: 1px solid #EBEEF5;
  padding-top: 10px;
}
</style>
