<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 overflow-y-auto"
    @click.self="closeModal"
  >
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>
    
    <!-- Modal -->
    <div class="flex min-h-full items-center justify-center p-4">
      <div
        class="relative w-full max-w-4xl bg-white rounded-2xl shadow-2xl transform transition-all"
        :class="modalClasses"
      >
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <span class="text-white text-lg font-semibold">
                {{ mode === 'trigger' ? '⚡' : '🔧' }}
              </span>
            </div>
            <div>
              <h2 class="text-xl font-semibold text-gray-900">
                {{ mode === 'trigger' ? 'Add Trigger' : 'Add Action' }}
              </h2>
              <p class="text-sm text-gray-500">
                {{ mode === 'trigger' ? 'Choose an event source to start your workflow' : 'Choose an action to perform in your workflow' }}
              </p>
            </div>
          </div>
          <button
            @click="closeModal"
            class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- Content -->
        <div class="p-6">
          <!-- Search Bar -->
          <div class="mb-6">
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
              </div>
              <input
                v-model="searchQuery"
                type="text"
                class="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
                :placeholder="`Search ${mode === 'trigger' ? 'triggers' : 'actions'}...`"
              />
            </div>
          </div>

          <!-- Category Tabs -->
          <div class="mb-6">
            <div class="flex space-x-1 bg-gray-100 p-1 rounded-xl">
              <button
                v-for="category in categories"
                :key="category.id"
                @click="selectedCategory = category.id"
                class="flex-1 px-4 py-2 text-sm font-medium rounded-lg transition-all"
                :class="selectedCategory === category.id 
                  ? 'bg-white text-indigo-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'"
              >
                <span class="mr-2">{{ category.icon }}</span>
                {{ category.name }}
              </button>
            </div>
          </div>

          <!-- Integration List -->
          <div class="max-h-96 overflow-y-auto">
            <IntegrationList
              :integrations="filteredIntegrations"
              :mode="mode"
              @select-integration="handleIntegrationSelect"
              @select-trigger="handleTriggerSelect"
              @select-action="handleActionSelect"
            />
          </div>

          <!-- Empty State -->
          <div
            v-if="filteredIntegrations.length === 0"
            class="text-center py-12"
          >
            <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.29-1.009-5.824-2.709M15 6.291A7.962 7.962 0 0012 5c-2.34 0-4.29 1.009-5.824 2.709"></path>
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-900 mb-2">No {{ mode === 'trigger' ? 'triggers' : 'actions' }} found</h3>
            <p class="text-gray-500">
              Try adjusting your search or browse different categories
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { 
  INTEGRATIONS, 
  INTEGRATION_CATEGORIES, 
  searchIntegrations, 
  getIntegrationsByCategory,
  getPopularIntegrations,
  type Integration,
  type TriggerSchema,
  type ActionSchema
} from '@/types/integrations'
import IntegrationList from './IntegrationList.vue'

interface Props {
  isOpen: boolean
  mode: 'trigger' | 'action'
}

interface Emits {
  (e: 'close'): void
  (e: 'select-trigger', integration: Integration, trigger: TriggerSchema): void
  (e: 'select-action', integration: Integration, action: ActionSchema): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// State
const searchQuery = ref('')
const selectedCategory = ref('all')
const categories = computed(() => [
  { id: 'all', name: 'All', icon: '🔍' },
  { id: 'popular', name: 'Popular', icon: '⭐' },
  ...INTEGRATION_CATEGORIES
])

// Computed
const filteredIntegrations = computed(() => {
  let integrations = INTEGRATIONS

  // Filter by mode (trigger/action)
  integrations = integrations.filter(integration => {
    if (props.mode === 'trigger') {
      return integration.triggers.length > 0
    } else {
      return integration.actions.length > 0
    }
  })

  // Filter by category
  if (selectedCategory.value === 'popular') {
    integrations = getPopularIntegrations()
  } else if (selectedCategory.value !== 'all') {
    integrations = getIntegrationsByCategory(selectedCategory.value)
  }

  // Filter by search query
  if (searchQuery.value.trim()) {
    integrations = searchIntegrations(searchQuery.value)
  }

  return integrations
})

const modalClasses = computed(() => {
  return props.isOpen ? 'scale-100 opacity-100' : 'scale-95 opacity-0'
})

// Methods
const closeModal = () => {
  emit('close')
}

const handleIntegrationSelect = (integration: Integration) => {
  // This will be handled by IntegrationList component
}

const handleTriggerSelect = (integration: Integration, trigger: TriggerSchema) => {
  emit('select-trigger', integration, trigger)
  closeModal()
}

const handleActionSelect = (integration: Integration, action: ActionSchema) => {
  emit('select-action', integration, action)
  closeModal()
}

// Reset state when modal opens
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    searchQuery.value = ''
    selectedCategory.value = 'all'
  }
})

// Keyboard shortcuts
onMounted(() => {
  const handleKeyDown = (event: KeyboardEvent) => {
    if (props.isOpen && event.key === 'Escape') {
      closeModal()
    }
  }
  
  document.addEventListener('keydown', handleKeyDown)
  
  // Cleanup
  return () => {
    document.removeEventListener('keydown', handleKeyDown)
  }
})
</script>

<style scoped>
/* Custom scrollbar */
.max-h-96::-webkit-scrollbar {
  width: 6px;
}

.max-h-96::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.max-h-96::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.max-h-96::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Animation classes */
.transform {
  transition: transform 0.2s ease-out, opacity 0.2s ease-out;
}
</style>
