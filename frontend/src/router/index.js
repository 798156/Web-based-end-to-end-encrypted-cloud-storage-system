import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '../views/Dashboard.vue'
import Analysis from '../views/Analysis.vue'
import AuditLog from '../views/AuditLog.vue'
import RecycleBin from '../views/RecycleBin.vue'
import Profile from '../views/Profile.vue'
import About from '../views/About.vue'
import Layout from '../components/Layout.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard
      },
      {
        path: '/recycle_bin',
        name: 'RecycleBin',
        component: RecycleBin
      },
      {
        path: '/analysis',
        name: 'Analysis',
        component: Analysis
      },
      {
        path: 'logs',
        name: 'AuditLog',
        component: AuditLog
      },
      {
        path: 'profile',
        name: 'Profile',
        component: Profile
      },
      {
        path: 'about',
        name: 'About',
        component: About
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const privateKey = sessionStorage.getItem('privateKey')
  if (to.meta.requiresAuth && !privateKey) {
    next('/login')
  } else {
    next()
  }
})

export default router
