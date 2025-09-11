<template>
  <div>
    <!-- Trigger/Action Creation Buttons -->
    <div class="flex space-x-3 mb-4">
      <button
        @click="openTriggerModal"
        class="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        <span>Add Trigger</span>
      </button>
      
      <button
        @click="openActionModal"
        class="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        <span>Add Action</span>
      </button>
    </div>

    <!-- Trigger/Action Modal -->
    <TriggerActionModal
      :is-open="isModalOpen"
      :mode="modalMode"
      @close="closeModal"
      @select-trigger="handleTriggerSelect"
      @select-action="handleActionSelect"
    />

    <!-- Configuration Panel -->
    <ConfigurationPanel
      :is-open="isConfigPanelOpen"
      :mode="configMode"
      :integration="selectedIntegration"
      :selected-item="selectedItem"
      :initial-data="initialConfigData"
      @close="closeConfigPanel"
      @submit="handleConfigSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useWorkflowStore } from '@/store/workflowStore'
import type { Integration, TriggerSchema, ActionSchema } from '@/types/integrations'
import TriggerActionModal from './TriggerActionModal.vue'
import ConfigurationPanel from './ConfigurationPanel.vue'

// State
const isModalOpen = ref(false)
const isConfigPanelOpen = ref(false)
const modalMode = ref<'trigger' | 'action'>('trigger')
const configMode = ref<'trigger' | 'action'>('trigger')
const selectedIntegration = ref<Integration | null>(null)
const selectedItem = ref<TriggerSchema | ActionSchema | null>(null)
const initialConfigData = ref<Record<string, any>>({})

// Store
const { addIntegrationNode } = useWorkflowStore()

// Computed
const defaultPosition = computed(() => ({ x: 100, y: 100 }))

// Methods
const openTriggerModal = () => {
  modalMode.value = 'trigger'
  isModalOpen.value = true
}

const openActionModal = () => {
  modalMode.value = 'action'
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}

const closeConfigPanel = () => {
  isConfigPanelOpen.value = false
  selectedIntegration.value = null
  selectedItem.value = null
  initialConfigData.value = {}
}

const handleTriggerSelect = (integration: Integration, trigger: TriggerSchema) => {
  selectedIntegration.value = integration
  selectedItem.value = trigger
  configMode.value = 'trigger'
  
  // Initialize config data with default values
  const config: Record<string, any> = {}
  trigger.fields.forEach(field => {
    if (field.defaultValue !== undefined) {
      config[field.id] = field.defaultValue
    } else if (field.type === 'boolean') {
      config[field.id] = false
    } else if (field.type === 'multiselect') {
      config[field.id] = []
    } else {
      config[field.id] = ''
    }
  })
  
  initialConfigData.value = config
  isConfigPanelOpen.value = true
}

const handleActionSelect = (integration: Integration, action: ActionSchema) => {
  selectedIntegration.value = integration
  selectedItem.value = action
  configMode.value = 'action'
  
  // Initialize config data with default values
  const config: Record<string, any> = {}
  action.fields.forEach(field => {
    if (field.defaultValue !== undefined) {
      config[field.id] = field.defaultValue
    } else if (field.type === 'boolean') {
      config[field.id] = false
    } else if (field.type === 'multiselect') {
      config[field.id] = []
    } else {
      config[field.id] = ''
    }
  })
  
  initialConfigData.value = config
  isConfigPanelOpen.value = true
}

const handleConfigSubmit = (config: Record<string, any>) => {
  if (selectedIntegration.value && selectedItem.value) {
    addIntegrationNode(
      selectedIntegration.value,
      selectedItem.value,
      config,
      defaultPosition.value
    )
  }
  
  closeConfigPanel()
}
</script>

<style scoped>
/* Smooth transitions */
.transition-colors {
  transition: all 0.2s ease-in-out;
}
</style>
