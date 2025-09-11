<template>
  <div class="min-h-screen bg-gray-50 p-8">
    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">
          Trigger & Action Creation Demo
        </h1>
        <p class="text-gray-600">
          Test the new trigger and action creation interface for FlowMaker
        </p>
      </div>

      <!-- Demo Controls -->
      <div class="bg-white rounded-2xl shadow-lg p-6 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Demo Controls</h2>
        <div class="flex space-x-4">
          <button
            @click="showTriggerModal = true"
            class="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            <span>Test Trigger Modal</span>
          </button>
          
          <button
            @click="showActionModal = true"
            class="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            <span>Test Action Modal</span>
          </button>
        </div>
      </div>

      <!-- Integration Manager -->
      <div class="bg-white rounded-2xl shadow-lg p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Integration Manager</h2>
        <TriggerActionManager />
      </div>

      <!-- Modals -->
      <TriggerActionModal
        :is-open="showTriggerModal"
        mode="trigger"
        @close="showTriggerModal = false"
        @select-trigger="handleTriggerSelect"
        @select-action="handleActionSelect"
      />

      <TriggerActionModal
        :is-open="showActionModal"
        mode="action"
        @close="showActionModal = false"
        @select-trigger="handleTriggerSelect"
        @select-action="handleActionSelect"
      />

      <!-- Configuration Panel -->
      <ConfigurationPanel
        :is-open="showConfigPanel"
        :mode="configMode"
        :integration="selectedIntegration"
        :selected-item="selectedItem"
        :initial-data="initialConfigData"
        @close="showConfigPanel = false"
        @submit="handleConfigSubmit"
      />

      <!-- Results Display -->
      <div v-if="createdNodes.length > 0" class="mt-8 bg-white rounded-2xl shadow-lg p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Created Nodes</h2>
        <div class="space-y-4">
          <div
            v-for="(node, index) in createdNodes"
            :key="index"
            class="p-4 border border-gray-200 rounded-lg"
          >
            <div class="flex items-center space-x-3 mb-2">
              <div 
                class="w-8 h-8 rounded-lg flex items-center justify-center text-sm"
                :class="node.integration.icon.bgColor"
              >
                <span :class="node.integration.icon.color">
                  {{ node.integration.icon.name }}
                </span>
              </div>
              <div>
                <h3 class="font-medium text-gray-900">
                  {{ node.integration.name }} - {{ node.item.name }}
                </h3>
                <p class="text-sm text-gray-600">{{ node.item.description }}</p>
              </div>
            </div>
            <div class="text-xs text-gray-500">
              <p><strong>Type:</strong> {{ node.mode }}</p>
              <p><strong>Configuration:</strong> {{ JSON.stringify(node.config, null, 2) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Integration, TriggerSchema, ActionSchema } from '@/types/integrations'
import TriggerActionModal from '@/components/TriggerActionModal.vue'
import ConfigurationPanel from '@/components/ConfigurationPanel.vue'
import TriggerActionManager from '@/components/TriggerActionManager.vue'

// State
const showTriggerModal = ref(false)
const showActionModal = ref(false)
const showConfigPanel = ref(false)
const configMode = ref<'trigger' | 'action'>('trigger')
const selectedIntegration = ref<Integration | null>(null)
const selectedItem = ref<TriggerSchema | ActionSchema | null>(null)
const initialConfigData = ref<Record<string, any>>({})
const createdNodes = ref<Array<{
  integration: Integration
  item: TriggerSchema | ActionSchema
  mode: 'trigger' | 'action'
  config: Record<string, any>
}>>([])

// Methods
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
  showConfigPanel.value = true
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
  showConfigPanel.value = true
}

const handleConfigSubmit = (config: Record<string, any>) => {
  if (selectedIntegration.value && selectedItem.value) {
    createdNodes.value.push({
      integration: selectedIntegration.value,
      item: selectedItem.value,
      mode: configMode.value,
      config
    })
  }
  
  showConfigPanel.value = false
  selectedIntegration.value = null
  selectedItem.value = null
  initialConfigData.value = {}
}
</script>

<style scoped>
/* Smooth transitions */
.transition-colors {
  transition: all 0.2s ease-in-out;
}
</style>
