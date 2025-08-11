import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  const login = async (credentials) => {
    loading.value = true
    try {
      const response = await api.post('/auth/login', credentials)
      const { access_token, user: userData } = response.data
      
      token.value = access_token
      user.value = userData
      localStorage.setItem('token', access_token)
      
      // Set auth header for future requests
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      return response.data
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  const register = async (userData) => {
    loading.value = true
    try {
      const response = await api.post('/auth/register', userData)
      return response.data
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      // Clear local state
      user.value = null
      token.value = null
      localStorage.removeItem('token')
      
      // Clear auth header
      delete api.defaults.headers.common['Authorization']
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  const fetchUser = async () => {
    if (!token.value) return
    
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
    } catch (error) {
      // Token might be invalid, clear it
      await logout()
      throw error
    }
  }

  const refreshToken = async () => {
    if (!token.value) return
    
    try {
      const response = await api.post('/auth/refresh')
      const { access_token } = response.data
      
      token.value = access_token
      localStorage.setItem('token', access_token)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      return access_token
    } catch (error) {
      await logout()
      throw error
    }
  }

  // Initialize auth state
  const init = async () => {
    if (token.value) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      try {
        await fetchUser()
      } catch (error) {
        console.error('Failed to fetch user:', error)
      }
    }
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    fetchUser,
    refreshToken,
    init
  }
}) 