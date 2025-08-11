<template>
  <div class="bg-white border-l border-gray-200 p-4 w-80">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Properties</h3>
    
    <div v-if="selectedNode" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Node Type</label>
        <div class="text-sm text-gray-900 bg-gray-50 p-2 rounded">{{ selectedNode.type }}</div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Node ID</label>
        <div class="text-sm text-gray-900 bg-gray-50 p-2 rounded">{{ selectedNode.id }}</div>
      </div>

      <!-- Gmail Trigger Properties -->
      <div v-if="selectedNode.type === 'gmail_trigger'" class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email Filter</label>
          <input
            v-model="selectedNode.config.emailFilter"
            type="text"
            placeholder="from:example@gmail.com"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Check Interval (minutes)</label>
          <input
            v-model="selectedNode.config.checkInterval"
            type="number"
            min="1"
            max="60"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <!-- Gmail Action Properties -->
      <div v-if="selectedNode.type === 'gmail_action'" class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">To</label>
          <input
            v-model="selectedNode.config.to"
            type="email"
            placeholder="recipient@example.com"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Subject</label>
          <input
            v-model="selectedNode.config.subject"
            type="text"
            placeholder="Email subject"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Body</label>
          <textarea
            v-model="selectedNode.config.body"
            rows="4"
            placeholder="Email body"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          ></textarea>
        </div>
      </div>

      <!-- Slack Action Properties -->
      <div v-if="selectedNode.type === 'slack_action'" class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Channel</label>
          <input
            v-model="selectedNode.config.channel"
            type="text"
            placeholder="#general"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Message</label>
          <textarea
            v-model="selectedNode.config.message"
            rows="3"
            placeholder="Slack message"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          ></textarea>
        </div>
      </div>

      <!-- Condition Properties -->
      <div v-if="selectedNode.type === 'condition'" class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Condition</label>
          <select
            v-model="selectedNode.config.operator"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="equals">Equals</option>
            <option value="contains">Contains</option>
            <option value="greater_than">Greater Than</option>
            <option value="less_than">Less Than</option>
            <option value="exists">Exists</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Field Path</label>
          <input
            v-model="selectedNode.config.fieldPath"
            type="text"
            placeholder="data.email"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Value</label>
          <input
            v-model="selectedNode.config.value"
            type="text"
            placeholder="Expected value"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <!-- HTTP Request Properties -->
      <div v-if="selectedNode.type === 'http_request'" class="space-y-3">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Method</label>
          <select
            v-model="selectedNode.config.method"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">URL</label>
          <input
            v-model="selectedNode.config.url"
            type="url"
            placeholder="https://api.example.com/endpoint"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Headers (JSON)</label>
          <textarea
            v-model="selectedNode.config.headers"
            rows="3"
            placeholder='{"Content-Type": "application/json"}'
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          ></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Body (JSON)</label>
          <textarea
            v-model="selectedNode.config.body"
            rows="3"
            placeholder='{"key": "value"}'
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          ></textarea>
        </div>
      </div>

      <div class="pt-4 border-t border-gray-200">
        <button
          @click="deleteNode"
          class="w-full bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
        >
          Delete Node
        </button>
      </div>
    </div>

    <div v-else class="text-center text-gray-500 py-8">
      <p>Select a node to edit its properties</p>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  selectedNode: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:selectedNode', 'deleteNode'])

const deleteNode = () => {
  if (props.selectedNode) {
    emit('deleteNode', props.selectedNode.id)
  }
}
</script> 