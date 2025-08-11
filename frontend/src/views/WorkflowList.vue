<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Workflows</h1>
        <p class="mt-2 text-gray-600">Create and manage your automation workflows</p>
      </div>
      <router-link
        to="/workflows/new"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        New Workflow
      </router-link>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="workflows.length === 0" class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No workflows</h3>
      <p class="mt-1 text-sm text-gray-500">Get started by creating a new workflow.</p>
      <div class="mt-6">
        <router-link
          to="/workflows/new"
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
          </svg>
          New Workflow
        </router-link>
      </div>
    </div>

    <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="workflow in workflows"
        :key="workflow.id"
        class="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow"
      >
        <div class="p-6">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900 truncate">{{ workflow.name }}</h3>
            <div class="flex items-center space-x-2">
              <span
                :class="{
                  'bg-green-100 text-green-800': workflow.is_active,
                  'bg-gray-100 text-gray-800': !workflow.is_active
                }"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              >
                {{ workflow.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>
          
          <p v-if="workflow.description" class="mt-2 text-sm text-gray-600 line-clamp-2">
            {{ workflow.description }}
          </p>
          
          <div class="mt-4 flex items-center justify-between text-sm text-gray-500">
            <span>Created {{ formatDate(workflow.created_at) }}</span>
            <span>{{ workflow.node_count || 0 }} nodes</span>
          </div>
        </div>
        
        <div class="bg-gray-50 px-6 py-3 flex items-center justify-between">
          <div class="flex space-x-2">
            <button
              @click="executeWorkflow(workflow.id)"
              :disabled="executing === workflow.id"
              class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <svg v-if="executing === workflow.id" class="animate-spin -ml-1 mr-1 h-3 w-3" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ executing === workflow.id ? 'Running...' : 'Run' }}
            </button>
            <button
              @click="toggleWorkflow(workflow)"
              :disabled="updating === workflow.id"
              class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-gray-700 bg-gray-100 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50"
            >
              {{ workflow.is_active ? 'Disable' : 'Enable' }}
            </button>
          </div>
          
          <div class="flex space-x-2">
            <router-link
              :to="`/workflows/${workflow.id}/edit`"
              class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-gray-700 bg-gray-100 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            >
              Edit
            </router-link>
            <button
              @click="deleteWorkflow(workflow.id)"
              class="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { useWorkflowsStore } from '@/stores/workflows'
import { format } from 'date-fns'

const toast = useToast()
const workflowsStore = useWorkflowsStore()

const loading = ref(false)
const executing = ref(null)
const updating = ref(null)

const workflows = ref([])

const formatDate = (dateString) => {
  return format(new Date(dateString), 'MMM d, yyyy')
}

const loadWorkflows = async () => {
  loading.value = true
  try {
    await workflowsStore.fetchWorkflows()
    workflows.value = workflowsStore.workflows
  } catch (error) {
    toast.error('Failed to load workflows')
  } finally {
    loading.value = false
  }
}

const executeWorkflow = async (workflowId) => {
  executing.value = workflowId
  try {
    await workflowsStore.executeWorkflow(workflowId)
    toast.success('Workflow execution started')
  } catch (error) {
    toast.error('Failed to execute workflow')
  } finally {
    executing.value = null
  }
}

const toggleWorkflow = async (workflow) => {
  updating.value = workflow.id
  try {
    await workflowsStore.updateWorkflow(workflow.id, {
      ...workflow,
      is_active: !workflow.is_active
    })
    workflow.is_active = !workflow.is_active
    toast.success(`Workflow ${workflow.is_active ? 'enabled' : 'disabled'}`)
  } catch (error) {
    toast.error('Failed to update workflow')
  } finally {
    updating.value = null
  }
}

const deleteWorkflow = async (workflowId) => {
  if (!confirm('Are you sure you want to delete this workflow?')) {
    return
  }
  
  try {
    await workflowsStore.deleteWorkflow(workflowId)
    workflows.value = workflows.value.filter(w => w.id !== workflowId)
    toast.success('Workflow deleted')
  } catch (error) {
    toast.error('Failed to delete workflow')
  }
}

onMounted(() => {
  loadWorkflows()
})
</script> 