import { createRouter, createWebHistory } from 'vue-router'
import AppStore from '../components/AppStore.vue'
import UserManagement from '../components/UserManagement.vue'
import Login from '../components/Login.vue'
import Register from '../components/Register.vue'

const routes = [
  {
    path: '/',
    name: 'AppStore',
    component: AppStore
  },
  {
    path: '/users',
    name: 'UserManagement',
    component: UserManagement,
    meta: { requiresAuth: true, requiresAdmin: true }
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    try {
      const response = await fetch('/api/check-auth')
      if (!response.ok) {
        return next('/login')
      }
      
      const data = await response.json()
      if (to.meta.requiresAdmin && data.role !== 'admin') {
        return next('/')
      }
    } catch (error) {
      return next('/login')
    }
  }
  next()
})

export default router 