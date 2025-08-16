import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useWorkflowsStore = defineStore('workflows', () => {
  const workflows = ref([])
  const currentWorkflow = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const activeWorkflows = computed(() => 
    workflows.value.filter(w => w.is_active)
  )

  const fetchWorkflows = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/workflows')
      workflows.value = response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchWorkflow = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`/workflows/${id}`)
      currentWorkflow.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const createWorkflow = async (workflowData) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('/workflows', workflowData)
      workflows.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateWorkflow = async (id, workflowData) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.put(`/workflows/${id}`, workflowData)
      const index = workflows.value.findIndex(w => w.id === id)
      if (index !== -1) {
        workflows.value[index] = response.data
      }
      if (currentWorkflow.value?.id === id) {
        currentWorkflow.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateWorkflowBulk = async (id, workflowData) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.put(`/workflows/${id}/bulk`, workflowData)
      const index = workflows.value.findIndex(w => w.id === id)
      if (index !== -1) {
        workflows.value[index] = response.data
      }
      if (currentWorkflow.value?.id === id) {
        currentWorkflow.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteWorkflow = async (id) => {
    loading.value = true
    error.value = null
    try {
      await api.delete(`/workflows/${id}`)
      workflows.value = workflows.value.filter(w => w.id !== id)
      if (currentWorkflow.value?.id === id) {
        currentWorkflow.value = null
      }
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const executeWorkflow = async (id, executionData = {}) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post(`/workflows/${id}/execute`, executionData)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const testWorkflow = async (id, executionData = {}) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.post(`/workflows/${id}/test`, executionData)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const createNode = async (workflowId, nodeData) => {
    try {
      const response = await api.post(`/workflows/${workflowId}/nodes`, nodeData)
      if (currentWorkflow.value?.id === workflowId) {
        currentWorkflow.value.nodes.push(response.data)
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const updateNode = async (workflowId, nodeId, nodeData) => {
    try {
      const response = await api.put(`/workflows/${workflowId}/nodes/${nodeId}`, nodeData)
      if (currentWorkflow.value?.id === workflowId) {
        const index = currentWorkflow.value.nodes.findIndex(n => n.id === nodeId)
        if (index !== -1) {
          currentWorkflow.value.nodes[index] = response.data
        }
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const deleteNode = async (workflowId, nodeId) => {
    try {
      await api.delete(`/workflows/${workflowId}/nodes/${nodeId}`)
      if (currentWorkflow.value?.id === workflowId) {
        currentWorkflow.value.nodes = currentWorkflow.value.nodes.filter(n => n.id !== nodeId)
      }
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const createConnection = async (workflowId, connectionData) => {
    try {
      const response = await api.post(`/workflows/${workflowId}/connections`, connectionData)
      if (currentWorkflow.value?.id === workflowId) {
        currentWorkflow.value.connections.push(response.data)
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const updateConnection = async (workflowId, connectionId, connectionData) => {
    try {
      const response = await api.put(`/workflows/${workflowId}/connections/${connectionId}`, connectionData)
      if (currentWorkflow.value?.id === workflowId) {
        const index = currentWorkflow.value.connections.findIndex(c => c.id === connectionId)
        if (index !== -1) {
          currentWorkflow.value.connections[index] = response.data
        }
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const deleteConnection = async (workflowId, connectionId) => {
    try {
      await api.delete(`/workflows/${workflowId}/connections/${connectionId}`)
      if (currentWorkflow.value?.id === workflowId) {
        currentWorkflow.value.connections = currentWorkflow.value.connections.filter(c => c.id !== connectionId)
      }
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    workflows,
    currentWorkflow,
    loading,
    error,
    activeWorkflows,
    fetchWorkflows,
    fetchWorkflow,
    createWorkflow,
    updateWorkflow,
    updateWorkflowBulk,
    deleteWorkflow,
    executeWorkflow,
    testWorkflow,
    createNode,
    updateNode,
    deleteNode,
    createConnection,
    updateConnection,
    deleteConnection,
    clearError
  }
}) 