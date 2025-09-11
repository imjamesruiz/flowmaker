<template>
  <div
    v-if="isOpen"
    class="fixed inset-y-0 right-0 z-40 w-96 bg-white shadow-2xl transform transition-transform duration-300 ease-in-out"
    :class="isOpen ? 'translate-x-0' : 'translate-x-full'"
  >
    <!-- Header -->
    <div class="flex items-center justify-between p-6 border-b border-gray-200 bg-gray-50">
      <div class="flex items-center space-x-3">
        <div 
          class="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
          :class="integration?.icon.bgColor"
        >
          <span :class="integration?.icon.color">{{ integration?.icon.name }}</span>
        </div>
        <div>
          <h2 class="text-lg font-semibold text-gray-900">
            {{ integration?.name }}
          </h2>
          <p class="text-sm text-gray-500">
            {{ mode === 'trigger' ? 'Configure Trigger' : 'Configure Action' }}
          </p>
        </div>
      </div>
      <button
        @click="closePanel"
        class="p-2 hover:bg-gray-200 rounded-lg transition-colors"
      >
        <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </button>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto">
      <div class="p-6">
        <!-- Selected Item Info -->
        <div class="mb-6 p-4 bg-gray-50 rounded-xl">
          <div class="flex items-center space-x-3">
            <div 
              class="w-8 h-8 rounded-lg flex items-center justify-center"
              :class="mode === 'trigger' ? 'bg-green-100' : 'bg-blue-100'"
            >
              <span 
                class="text-sm"
                :class="mode === 'trigger' ? 'text-green-600' : 'text-blue-600'"
              >
                {{ selectedItem?.icon }}
              </span>
            </div>
            <div>
              <h3 class="font-medium text-gray-900">
                {{ selectedItem?.name }}
              </h3>
              <p class="text-sm text-gray-600">
                {{ selectedItem?.description }}
              </p>
            </div>
          </div>
        </div>

        <!-- Configuration Form -->
        <div class="space-y-6">
          <div>
            <h4 class="text-sm font-medium text-gray-700 mb-4">Configuration</h4>
            <SchemaForm
              :fields="selectedItem?.fields || []"
              :initial-data="initialData"
              :submit-text="submitButtonText"
              @submit="handleSubmit"
              @cancel="closePanel"
            />
          </div>

          <!-- Preview Section -->
          <div v-if="selectedItem" class="border-t border-gray-200 pt-6">
            <h4 class="text-sm font-medium text-gray-700 mb-4">Preview</h4>
            <div class="p-4 bg-gray-50 rounded-lg">
              <div class="flex items-center space-x-3 mb-3">
                <div 
                  class="w-6 h-6 rounded-lg flex items-center justify-center"
                  :class="mode === 'trigger' ? 'bg-green-100' : 'bg-blue-100'"
                >
                  <span 
                    class="text-xs"
                    :class="mode === 'trigger' ? 'text-green-600' : 'text-blue-600'"
                  >
                    {{ selectedItem.icon }}
                  </span>
                </div>
                <span class="text-sm font-medium text-gray-900">
                  {{ selectedItem.name }}
                </span>
              </div>
              <div class="text-xs text-gray-600 space-y-1">
                <p><strong>Integration:</strong> {{ integration?.name }}</p>
                <p><strong>Type:</strong> {{ mode === 'trigger' ? 'Trigger' : 'Action' }}</p>
                <p v-if="integration?.authType !== 'none'">
                  <strong>Auth:</strong> {{ integration.authType === 'oauth' ? 'OAuth' : 'API Key' }}
                </p>
              </div>
            </div>
          </div>

          <!-- Help Section -->
          <div class="border-t border-gray-200 pt-6">
            <h4 class="text-sm font-medium text-gray-700 mb-4">Need Help?</h4>
            <div class="space-y-3">
              <a
                href="#"
                class="flex items-center space-x-2 text-sm text-indigo-600 hover:text-indigo-700"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                </svg>
                <span>View Documentation</span>
              </a>
              <a
                href="#"
                class="flex items-center space-x-2 text-sm text-indigo-600 hover:text-indigo-700"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span>Get Support</span>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="border-t border-gray-200 p-6 bg-gray-50">
      <div class="flex space-x-3">
        <button
          @click="closePanel"
          class="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors"
        >
          Cancel
        </button>
        <button
          @click="handleSubmit"
          class="flex-1 px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-lg hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors"
        >
          {{ submitButtonText }}
        </button>
      </div>
    </div>
  </div>

  <!-- Backdrop -->
  <div
    v-if="isOpen"
    class="fixed inset-0 z-30 bg-black bg-opacity-50 transition-opacity"
    @click="closePanel"
  ></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Integration, TriggerSchema, ActionSchema } from '@/types/integrations'
import SchemaForm from './SchemaForm.vue'

interface Props {
  isOpen: boolean
  mode: 'trigger' | 'action'
  integration: Integration | null
  selectedItem: TriggerSchema | ActionSchema | null
  initialData?: Record<string, any>
}

interface Emits {
  (e: 'close'): void
  (e: 'submit', data: Record<string, any>): void
}

const props = withDefaults(defineProps<Props>(), {
  initialData: () => ({})
})

const emit = defineEmits<Emits>()

// Computed
const submitButtonText = computed(() => {
  if (props.mode === 'trigger') {
    return 'Add Trigger'
  } else {
    return 'Add Action'
  }
})

// Methods
const closePanel = () => {
  emit('close')
}

const handleSubmit = (data: Record<string, any>) => {
  emit('submit', data)
}
</script>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Smooth transitions */
.transition-transform {
  transition: transform 0.3s ease-in-out;
}

.transition-opacity {
  transition: opacity 0.3s ease-in-out;
}

.transition-colors {
  transition: all 0.2s ease-in-out;
}
</style>
