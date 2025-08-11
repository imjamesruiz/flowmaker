import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors and token refresh
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    const authStore = useAuthStore()

    // Handle 401 errors (unauthorized)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        // Try to refresh token
        await authStore.refreshToken()
        
        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${authStore.token}`
        return api(originalRequest)
      } catch (refreshError) {
        // Refresh failed, logout user
        await authStore.logout()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// API methods
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getProfile: () => api.get('/auth/me'),
  refreshToken: () => api.post('/auth/refresh'),
}

export const workflowsAPI = {
  getAll: (params) => api.get('/workflows', { params }),
  getById: (id) => api.get(`/workflows/${id}`),
  create: (data) => api.post('/workflows', data),
  update: (id, data) => api.put(`/workflows/${id}`, data),
  delete: (id) => api.delete(`/workflows/${id}`),
  execute: (id, data) => api.post(`/workflows/${id}/execute`, data),
  
  // Nodes
  getNodes: (workflowId) => api.get(`/workflows/${workflowId}/nodes`),
  createNode: (workflowId, data) => api.post(`/workflows/${workflowId}/nodes`, data),
  updateNode: (workflowId, nodeId, data) => api.put(`/workflows/${workflowId}/nodes/${nodeId}`, data),
  deleteNode: (workflowId, nodeId) => api.delete(`/workflows/${workflowId}/nodes/${nodeId}`),
  
  // Connections
  getConnections: (workflowId) => api.get(`/workflows/${workflowId}/connections`),
  createConnection: (workflowId, data) => api.post(`/workflows/${workflowId}/connections`, data),
  updateConnection: (workflowId, connectionId, data) => api.put(`/workflows/${workflowId}/connections/${connectionId}`, data),
  deleteConnection: (workflowId, connectionId) => api.delete(`/workflows/${workflowId}/connections/${connectionId}`),
}

export const integrationsAPI = {
  getAll: () => api.get('/integrations'),
  getById: (id) => api.get(`/integrations/${id}`),
  create: (data) => api.post('/integrations', data),
  update: (id, data) => api.put(`/integrations/${id}`, data),
  delete: (id) => api.delete(`/integrations/${id}`),
  test: (id) => api.post(`/integrations/${id}/test`),
}

export const executionsAPI = {
  getAll: (params) => api.get('/executions', { params }),
  getById: (id) => api.get(`/executions/${id}`),
  getLogs: (id) => api.get(`/executions/${id}/logs`),
  delete: (id) => api.delete(`/executions/${id}`),
}

export const oauthAPI = {
  getGoogleAuthUrl: (integrationId) => api.get(`/oauth/google/auth-url?integration_id=${integrationId}`),
  getSlackAuthUrl: (integrationId) => api.get(`/oauth/slack/auth-url?integration_id=${integrationId}`),
  revokeToken: (tokenId) => api.delete(`/oauth/tokens/${tokenId}`),
}

export default api 