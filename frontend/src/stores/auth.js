import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/services/api'
import { supabase } from '@/lib/supabaseClient'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const refreshTokenTimeoutId = ref(null)
  const loading = ref(false)
  const isRefreshing = ref(false)

  const isAuthenticated = computed(() => !!token.value)

  const login = async (credentials) => {
    loading.value = true
    try {
      const { data, error } = await supabase.auth.signInWithPassword({ 
        email: credentials.email, 
        password: credentials.password 
      })
      if (error) throw error
      token.value = data.session?.access_token || null
      user.value = data.user
      if (token.value) localStorage.setItem('token', token.value)
      return data
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  const register = async (userData) => {
    loading.value = true
    try {
      const { data, error } = await supabase.auth.signUp({ 
        email: userData.email, 
        password: userData.password 
      })
      if (error) throw error
      if (data.session?.access_token) {
        token.value = data.session.access_token
        user.value = data.user
        localStorage.setItem('token', token.value)
      }
      return data
    } catch (error) {
      throw error
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      try { await authAPI.logout?.() } catch {}
      // Clear local state
      user.value = null
      token.value = null
      localStorage.removeItem('token')
      if (refreshTokenTimeoutId.value) {
        clearTimeout(refreshTokenTimeoutId.value)
        refreshTokenTimeoutId.value = null
      }
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  const fetchUser = async () => {
    if (!token.value) return
    
    try {
      const { data: sessionData } = await supabase.auth.getSession()
      if (sessionData.session?.access_token) {
        token.value = sessionData.session.access_token
        const { data: userData } = await supabase.auth.getUser()
        user.value = userData.user
      } else {
        await logout()
      }
    } catch (error) {
      await logout()
      throw error
    }
  }

  const refreshToken = async () => {
    if (isRefreshing.value) return token.value
    isRefreshing.value = true
    
    try {
      const { data } = await supabase.auth.getSession()
      token.value = data.session?.access_token || null
      if (token.value) {
        localStorage.setItem('token', token.value)
      } else {
        await logout()
      }
      return token.value
    } catch (error) {
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

  const scheduleRefresh = (refreshExpiresInSeconds) => {
    if (!refreshExpiresInSeconds) return
    const skew = 60 // seconds before expiry
    const delayMs = Math.max((refreshExpiresInSeconds - skew) * 1000, 30_000)
    if (refreshTokenTimeoutId.value) clearTimeout(refreshTokenTimeoutId.value)
    refreshTokenTimeoutId.value = setTimeout(() => {
      refreshToken().catch(() => {})
    }, delayMs)
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