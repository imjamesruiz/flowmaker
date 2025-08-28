import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const loading = ref(false)
  const isRefreshing = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  const login = async (credentials) => {
    loading.value = true
    try {
      const response = await authAPI.login(credentials)
      const { access_token, user: userData } = response.data
      
      token.value = access_token
      user.value = userData
      localStorage.setItem('token', access_token)
      
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
      const response = await authAPI.register(userData)
      // After successful registration, automatically log the user in
      if (response.data) {
        // Try to login with the same credentials
        try {
          await login({
            email: userData.email,
            password: userData.password
          })
        } catch (loginError) {
          // If auto-login fails, just return the registration response
          console.warn('Auto-login after registration failed:', loginError)
        }
      }
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
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  const fetchUser = async () => {
    if (!token.value) return
    
    try {
      const response = await authAPI.getProfile()
      user.value = response.data
    } catch (error) {
      // Token might be invalid, clear it
      await logout()
      throw error
    }
  }

  const refreshToken = async () => {
    if (!token.value) {
      throw new Error('No token available to refresh')
    }
    
    // Prevent multiple simultaneous refresh attempts
    if (isRefreshing.value) {
      // Wait for the current refresh to complete
      while (isRefreshing.value) {
        await new Promise(resolve => setTimeout(resolve, 100))
      }
      return token.value
    }
    
    isRefreshing.value = true
    
    try {
      // Use the refreshApi instance directly with the current token
      const response = await authAPI.refreshToken()
      const { access_token } = response.data
      
      token.value = access_token
      localStorage.setItem('token', access_token)
      
      return access_token
    } catch (error) {
      // If refresh fails, clear the token and logout
      await logout()
      throw error
    } finally {
      isRefreshing.value = false
    }
  }

  // Initialize auth state
  const init = async () => {
    if (token.value) {
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