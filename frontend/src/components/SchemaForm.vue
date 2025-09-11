<template>
  <div class="space-y-6">
    <div
      v-for="field in fields"
      :key="field.id"
      class="space-y-2"
    >
      <!-- Field Label -->
      <label
        :for="field.id"
        class="block text-sm font-medium text-gray-700"
      >
        {{ field.label }}
        <span v-if="field.required" class="text-red-500 ml-1">*</span>
      </label>

      <!-- Field Description -->
      <p v-if="field.description" class="text-sm text-gray-500">
        {{ field.description }}
      </p>

      <!-- Text Input -->
      <input
        v-if="field.type === 'text' || field.type === 'email' || field.type === 'url'"
        :id="field.id"
        v-model="formData[field.id]"
        :type="field.type"
        :placeholder="field.placeholder"
        :required="field.required"
        class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
        :class="{ 'border-red-300 focus:ring-red-500 focus:border-red-500': errors[field.id] }"
      />

      <!-- Password Input -->
      <div v-else-if="field.type === 'password'" class="relative">
        <input
          :id="field.id"
          v-model="formData[field.id]"
          :type="showPassword[field.id] ? 'text' : 'password'"
          :placeholder="field.placeholder"
          :required="field.required"
          class="block w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
          :class="{ 'border-red-300 focus:ring-red-500 focus:border-red-500': errors[field.id] }"
        />
        <button
          type="button"
          @click="togglePasswordVisibility(field.id)"
          class="absolute inset-y-0 right-0 pr-3 flex items-center"
        >
          <svg
            v-if="showPassword[field.id]"
            class="h-5 w-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"></path>
          </svg>
          <svg
            v-else
            class="h-5 w-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
          </svg>
        </button>
      </div>

      <!-- Number Input -->
      <input
        v-else-if="field.type === 'number'"
        :id="field.id"
        v-model.number="formData[field.id]"
        type="number"
        :placeholder="field.placeholder"
        :required="field.required"
        :min="field.validation?.min"
        :max="field.validation?.max"
        class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
        :class="{ 'border-red-300 focus:ring-red-500 focus:border-red-500': errors[field.id] }"
      />

      <!-- Textarea -->
      <textarea
        v-else-if="field.type === 'textarea'"
        :id="field.id"
        v-model="formData[field.id]"
        :placeholder="field.placeholder"
        :required="field.required"
        rows="4"
        class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors resize-vertical"
        :class="{ 'border-red-300 focus:ring-red-500 focus:border-red-500': errors[field.id] }"
      ></textarea>

      <!-- Select Dropdown -->
      <select
        v-else-if="field.type === 'select'"
        :id="field.id"
        v-model="formData[field.id]"
        :required="field.required"
        class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
        :class="{ 'border-red-300 focus:ring-red-500 focus:border-red-500': errors[field.id] }"
      >
        <option value="" disabled>{{ field.placeholder || 'Select an option' }}</option>
        <option
          v-for="option in field.options"
          :key="option.value"
          :value="option.value"
        >
          {{ option.label }}
        </option>
      </select>

      <!-- Multi-select -->
      <div v-else-if="field.type === 'multiselect'" class="space-y-2">
        <div class="flex flex-wrap gap-2">
          <div
            v-for="option in field.options"
            :key="option.value"
            class="flex items-center"
          >
            <input
              :id="`${field.id}-${option.value}`"
              v-model="formData[field.id]"
              type="checkbox"
              :value="option.value"
              class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label
              :for="`${field.id}-${option.value}`"
              class="ml-2 text-sm text-gray-700"
            >
              {{ option.label }}
            </label>
          </div>
        </div>
      </div>

      <!-- Checkbox -->
      <div v-else-if="field.type === 'boolean'" class="flex items-center">
        <input
          :id="field.id"
          v-model="formData[field.id]"
          type="checkbox"
          class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
        />
        <label :for="field.id" class="ml-2 text-sm text-gray-700">
          {{ field.label }}
        </label>
      </div>

      <!-- OAuth Selector -->
      <div v-else-if="field.type === 'oauth'" class="space-y-3">
        <div class="flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <div class="flex items-center space-x-3">
            <div class="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center">
              <svg class="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
              </svg>
            </div>
            <div>
              <p class="text-sm font-medium text-gray-900">OAuth Connection</p>
              <p class="text-xs text-gray-500">Select an authenticated connection</p>
            </div>
          </div>
          <select
            v-model="formData[field.id]"
            class="px-3 py-1 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="">Select connection...</option>
            <option value="connection-1">My Gmail Account</option>
            <option value="connection-2">Work Slack</option>
            <option value="connection-3">Personal Google Sheets</option>
          </select>
        </div>
        <button
          type="button"
          class="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
        >
          + Add new connection
        </button>
      </div>

      <!-- Error Message -->
      <p v-if="errors[field.id]" class="text-sm text-red-600">
        {{ errors[field.id] }}
      </p>
    </div>

    <!-- Form Actions -->
    <div class="flex justify-end space-x-3 pt-6 border-t border-gray-200">
      <button
        type="button"
        @click="$emit('cancel')"
        class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors"
      >
        Cancel
      </button>
      <button
        type="button"
        @click="handleSubmit"
        :disabled="!isFormValid"
        class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-lg hover:bg-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {{ submitText }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import type { FieldSchema } from '@/types/integrations'

interface Props {
  fields: FieldSchema[]
  initialData?: Record<string, any>
  submitText?: string
}

interface Emits {
  (e: 'submit', data: Record<string, any>): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  initialData: () => ({}),
  submitText: 'Save Configuration'
})

const emit = defineEmits<Emits>()

// State
const formData = ref<Record<string, any>>({})
const errors = ref<Record<string, string>>({})
const showPassword = ref<Record<string, boolean>>({})

// Computed
const isFormValid = computed(() => {
  return props.fields.every(field => {
    if (!field.required) return true
    
    const value = formData.value[field.id]
    if (value === undefined || value === null || value === '') {
      return false
    }
    
    // Additional validation
    if (field.type === 'email' && value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(value)
    }
    
    if (field.type === 'url' && value) {
      try {
        new URL(value)
        return true
      } catch {
        return false
      }
    }
    
    return true
  })
})

// Methods
const togglePasswordVisibility = (fieldId: string) => {
  showPassword.value[fieldId] = !showPassword.value[fieldId]
}

const validateField = (field: FieldSchema, value: any): string | null => {
  if (field.required && (value === undefined || value === null || value === '')) {
    return `${field.label} is required`
  }
  
  if (value && field.validation) {
    if (field.validation.min !== undefined && value < field.validation.min) {
      return `${field.label} must be at least ${field.validation.min}`
    }
    
    if (field.validation.max !== undefined && value > field.validation.max) {
      return `${field.label} must be at most ${field.validation.max}`
    }
    
    if (field.validation.pattern && !new RegExp(field.validation.pattern).test(value)) {
      return field.validation.message || `${field.label} format is invalid`
    }
  }
  
  if (field.type === 'email' && value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(value)) {
      return 'Please enter a valid email address'
    }
  }
  
  if (field.type === 'url' && value) {
    try {
      new URL(value)
    } catch {
      return 'Please enter a valid URL'
    }
  }
  
  return null
}

const validateForm = (): boolean => {
  errors.value = {}
  let isValid = true
  
  props.fields.forEach(field => {
    const error = validateField(field, formData.value[field.id])
    if (error) {
      errors.value[field.id] = error
      isValid = false
    }
  })
  
  return isValid
}

const handleSubmit = () => {
  if (validateForm()) {
    emit('submit', { ...formData.value })
  }
}

// Initialize form data
const initializeForm = () => {
  const data: Record<string, any> = {}
  
  props.fields.forEach(field => {
    if (props.initialData[field.id] !== undefined) {
      data[field.id] = props.initialData[field.id]
    } else if (field.defaultValue !== undefined) {
      data[field.id] = field.defaultValue
    } else if (field.type === 'boolean') {
      data[field.id] = false
    } else if (field.type === 'multiselect') {
      data[field.id] = []
    } else {
      data[field.id] = ''
    }
  })
  
  formData.value = data
}

// Watch for field changes to clear errors
watch(formData, () => {
  // Clear errors when user starts typing
  Object.keys(errors.value).forEach(key => {
    if (formData.value[key] !== undefined) {
      delete errors.value[key]
    }
  })
}, { deep: true })

// Initialize on mount
onMounted(() => {
  initializeForm()
})

// Re-initialize when fields change
watch(() => props.fields, () => {
  initializeForm()
}, { deep: true })
</script>

<style scoped>
/* Custom focus styles */
input:focus,
textarea:focus,
select:focus {
  outline: none;
}

/* Smooth transitions */
.transition-colors {
  transition: all 0.2s ease-in-out;
}

/* Custom scrollbar for textarea */
textarea::-webkit-scrollbar {
  width: 6px;
}

textarea::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

textarea::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

textarea::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
