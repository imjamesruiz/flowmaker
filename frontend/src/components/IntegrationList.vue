<template>
  <div class="space-y-4">
    <div
      v-for="integration in integrations"
      :key="integration.id"
      class="bg-white border border-gray-200 rounded-xl hover:border-gray-300 transition-all duration-200 hover:shadow-md"
    >
      <!-- Integration Header -->
      <div class="p-4 border-b border-gray-100">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div 
              class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
              :class="integration.icon.bgColor"
            >
              <span :class="integration.icon.color">{{ integration.icon.name }}</span>
            </div>
            <div>
              <div class="flex items-center space-x-2">
                <h3 class="font-semibold text-gray-900">{{ integration.name }}</h3>
                <div class="flex space-x-1">
                  <span
                    v-if="integration.isPopular"
                    class="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded-full"
                  >
                    Popular
                  </span>
                  <span
                    v-if="integration.isNew"
                    class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full"
                  >
                    New
                  </span>
                </div>
              </div>
              <p class="text-sm text-gray-600">{{ integration.description }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
              {{ integration.authType === 'oauth' ? 'OAuth' : integration.authType === 'api_key' ? 'API Key' : 'No Auth' }}
            </span>
            <button
              @click="toggleExpanded(integration.id)"
              class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg
                class="w-4 h-4 text-gray-500 transform transition-transform"
                :class="{ 'rotate-180': expandedIntegrations.includes(integration.id) }"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Expanded Content -->
      <div
        v-if="expandedIntegrations.includes(integration.id)"
        class="p-4 bg-gray-50"
      >
        <!-- Triggers Section -->
        <div v-if="mode === 'trigger' && integration.triggers.length > 0" class="mb-4">
          <h4 class="text-sm font-medium text-gray-700 mb-3 flex items-center">
            <span class="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
            Triggers ({{ integration.triggers.length }})
          </h4>
          <div class="grid gap-3">
            <div
              v-for="trigger in integration.triggers"
              :key="trigger.id"
              @click="selectTrigger(integration, trigger)"
              class="p-3 bg-white border border-gray-200 rounded-lg hover:border-indigo-300 hover:bg-indigo-50 cursor-pointer transition-all group"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                    <span class="text-green-600 text-sm">{{ trigger.icon }}</span>
                  </div>
                  <div>
                    <h5 class="font-medium text-gray-900 group-hover:text-indigo-700">
                      {{ trigger.name }}
                    </h5>
                    <p class="text-sm text-gray-600">{{ trigger.description }}</p>
                  </div>
                </div>
                <svg class="w-5 h-5 text-gray-400 group-hover:text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions Section -->
        <div v-if="mode === 'action' && integration.actions.length > 0" class="mb-4">
          <h4 class="text-sm font-medium text-gray-700 mb-3 flex items-center">
            <span class="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
            Actions ({{ integration.actions.length }})
          </h4>
          <div class="grid gap-3">
            <div
              v-for="action in integration.actions"
              :key="action.id"
              @click="selectAction(integration, action)"
              class="p-3 bg-white border border-gray-200 rounded-lg hover:border-indigo-300 hover:bg-indigo-50 cursor-pointer transition-all group"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                    <span class="text-blue-600 text-sm">{{ action.icon }}</span>
                  </div>
                  <div>
                    <h5 class="font-medium text-gray-900 group-hover:text-indigo-700">
                      {{ action.name }}
                    </h5>
                    <p class="text-sm text-gray-600">{{ action.description }}</p>
                  </div>
                </div>
                <svg class="w-5 h-5 text-gray-400 group-hover:text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- No triggers/actions message -->
        <div
          v-if="(mode === 'trigger' && integration.triggers.length === 0) || (mode === 'action' && integration.actions.length === 0)"
          class="text-center py-6 text-gray-500"
        >
          <div class="w-12 h-12 mx-auto mb-3 bg-gray-100 rounded-full flex items-center justify-center">
            <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
          </div>
          <p class="text-sm">
            No {{ mode === 'trigger' ? 'triggers' : 'actions' }} available for this integration
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Integration, TriggerSchema, ActionSchema } from '@/types/integrations'

interface Props {
  integrations: Integration[]
  mode: 'trigger' | 'action'
}

interface Emits {
  (e: 'select-integration', integration: Integration): void
  (e: 'select-trigger', integration: Integration, trigger: TriggerSchema): void
  (e: 'select-action', integration: Integration, action: ActionSchema): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// State
const expandedIntegrations = ref<string[]>([])

// Methods
const toggleExpanded = (integrationId: string) => {
  const index = expandedIntegrations.value.indexOf(integrationId)
  if (index > -1) {
    expandedIntegrations.value.splice(index, 1)
  } else {
    expandedIntegrations.value.push(integrationId)
  }
}

const selectTrigger = (integration: Integration, trigger: TriggerSchema) => {
  emit('select-trigger', integration, trigger)
}

const selectAction = (integration: Integration, action: ActionSchema) => {
  emit('select-action', integration, action)
}
</script>

<style scoped>
/* Smooth transitions */
.transition-all {
  transition: all 0.2s ease-in-out;
}

/* Hover effects */
.group:hover .group-hover\:text-indigo-700 {
  color: #4338ca;
}

.group:hover .group-hover\:text-indigo-500 {
  color: #6366f1;
}

/* Custom scrollbar for the container if needed */
.space-y-4::-webkit-scrollbar {
  width: 6px;
}

.space-y-4::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.space-y-4::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.space-y-4::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
