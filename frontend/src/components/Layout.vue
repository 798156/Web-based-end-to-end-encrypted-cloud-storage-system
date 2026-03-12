<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="aside">
      <div class="logo">
        <el-icon><Lock /></el-icon>
        <span>加密云存储</span>
      </div>
      <el-menu
        :default-active="activeRoute"
        class="el-menu-vertical"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><Files /></el-icon>
          <span>文件管理</span>
        </el-menu-item>
        <el-menu-item index="/analysis">
          <el-icon><PieChart /></el-icon>
          <span>存储分析</span>
        </el-menu-item>
        <el-menu-item index="/logs">
          <el-icon><List /></el-icon>
          <span>操作日志</span>
        </el-menu-item>
        <el-menu-item index="/recycle_bin">
          <el-icon><Delete /></el-icon>
          <span>回收站</span>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span>个人中心</span>
        </el-menu-item>
        <el-menu-item index="/about">
          <el-icon><InfoFilled /></el-icon>
          <span>关于系统</span>
        </el-menu-item>
      </el-menu>
      
      <div class="user-actions">
        <el-button type="danger" plain icon="SwitchButton" @click="handleLogout" style="width: 100%">退出登录</el-button>
      </div>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="breadcrumb">
          {{ currentRouteName }}
        </div>
        <div class="user-info">
          <img v-if="userInfo.avatar" :src="getAvatarUrl(userInfo.avatar)" class="header-avatar" />
          <el-avatar v-else :size="32" icon="UserFilled" />
          <span class="username">{{ userInfo.username || '已登录' }}</span>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" :key="route.path" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Lock, Files, User, InfoFilled, SwitchButton, UserFilled, PieChart, List, Delete } from '@element-plus/icons-vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const userInfo = ref({})
const API_BASE = 'http://localhost:5000'

const activeRoute = computed(() => route.path)

const currentRouteName = computed(() => {
  switch (route.path) {
    case '/dashboard': return '文件管理'
    case '/analysis': return '存储分析'
    case '/logs': return '操作日志'
    case '/recycle_bin': return '回收站'
    case '/profile': return '个人中心'
    case '/about': return '关于系统'
    default: return ''
  }
})

const getAvatarUrl = (avatar) => {
    if (!avatar) return ''
    if (avatar.startsWith('http')) return avatar
    return `${API_BASE}/static/avatars/${avatar}`
}

const handleLogout = () => {
  sessionStorage.clear()
  axios.get('/api/logout')
  router.push('/login')
}

const fetchUserInfo = async () => {
    try {
        const res = await axios.get('/api/me')
        userInfo.value = res.data
    } catch (e) {
        // ignore
    }
}

const handleAvatarUpdate = () => {
    fetchUserInfo()
}

onMounted(() => {
    fetchUserInfo()
    window.addEventListener('avatar-updated', handleAvatarUpdate)
    window.addEventListener('user-updated', handleAvatarUpdate)
})

onUnmounted(() => {
    window.removeEventListener('avatar-updated', handleAvatarUpdate)
    window.removeEventListener('user-updated', handleAvatarUpdate)
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.aside {
  background-color: #001529;
  color: white;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  background-color: #002140;
  gap: 10px;
}

.el-menu-vertical {
  border-right: none;
  background-color: transparent;
  flex: 1;
}

:deep(.el-menu-item) {
  color: #a6adb4;
}

:deep(.el-menu-item:hover) {
  background-color: #001529;
  color: white;
}

:deep(.el-menu-item.is-active) {
  background-color: #1890ff;
  color: white;
}

.user-actions {
  padding: 20px;
}

.header {
  background-color: white;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}

.breadcrumb {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.username {
  font-size: 14px;
  color: #606266;
}
.header-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.main-content {
  background-color: #f0f2f5;
  background-image: 
    radial-gradient(#dcdfe6 1px, transparent 1px),
    radial-gradient(#dcdfe6 1px, transparent 1px);
  background-size: 20px 20px;
  background-position: 0 0, 10px 10px;
  padding: 20px;
  min-height: calc(100vh - 60px);
}

/* Page Transition */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s cubic-bezier(0.55, 0, 0.1, 1);
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
