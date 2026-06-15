import { defineStore } from 'pinia'
import { ref, computed, markRaw } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const tokenCookie = useCookie('token', { maxAge: 60 * 60 * 24 }) // 24 hours
  const user = ref<any>(null)
  
  const token = computed({
    get: () => tokenCookie.value,
    set: (val) => { tokenCookie.value = val }
  })

  const isLoggedIn = computed(() => !!token.value)

  // Configure axios base settings
  const config = useRuntimeConfig()
  const apiInstance = axios.create({
    baseURL: config.public.apiBase
  })

  // Add interceptor to append authorization header
  apiInstance.interceptors.request.use((config) => {
    if (token.value) {
      config.headers.Authorization = `Bearer ${token.value}`
    }
    return config
  }, (error) => {
    return Promise.reject(error)
  })

  const api = computed(() => apiInstance)

  async function register(username: string, email: string, password: string) {
    try {
      const res = await apiInstance.post('/api/auth/register', { username, email, password })
      token.value = res.data.token
      user.value = res.data.user
      return { success: true }
    } catch (err: any) {
      return { 
        success: false, 
        error: err.response?.data?.error || 'Registration failed' 
      }
    }
  }

  async function login(email: string, password: string) {
    try {
      const res = await apiInstance.post('/api/auth/login', { email, password })
      token.value = res.data.token
      user.value = res.data.user
      return { success: true }
    } catch (err: any) {
      return { 
        success: false, 
        error: err.response?.data?.error || 'Login failed' 
      }
    }
  }

  function logout() {
    token.value = null
    user.value = null
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const res = await apiInstance.get('/api/auth/me')
      user.value = res.data.user
    } catch (err) {
      // If token is invalid or expired
      logout()
    }
  }

  return {
    token,
    user,
    isLoggedIn,
    api,
    register,
    login,
    logout,
    fetchUser
  }
})
