<template>
  <div class="bg-white border-r border-gray-200 p-4">
    <h3 class="text-lg font-semibold text-gray-900 mb-4">Node Palette</h3>
    
    <div class="space-y-2">
      <div class="text-sm font-medium text-gray-700 mb-2">Triggers</div>
      <div
        v-for="node in triggerNodes"
        :key="node.type"
        class="p-3 border border-gray-200 rounded-lg cursor-move hover:bg-gray-50 transition-colors"
        draggable="true"
        @dragstart="onDragStart($event, node)"
      >
        <div class="flex items-center space-x-2">
          <div class="w-3 h-3 rounded-full bg-green-500"></div>
          <span class="text-sm font-medium">{{ node.label }}</span>
        </div>
        <p class="text-xs text-gray-500 mt-1">{{ node.description }}</p>
      </div>

      <div class="text-sm font-medium text-gray-700 mb-2 mt-4">Actions</div>
      <div
        v-for="node in actionNodes"
        :key="node.type"
        class="p-3 border border-gray-200 rounded-lg cursor-move hover:bg-gray-50 transition-colors"
        draggable="true"
        @dragstart="onDragStart($event, node)"
      >
        <div class="flex items-center space-x-2">
          <div class="w-3 h-3 rounded-full bg-blue-500"></div>
          <span class="text-sm font-medium">{{ node.label }}</span>
        </div>
        <p class="text-xs text-gray-500 mt-1">{{ node.description }}</p>
      </div>

      <div class="text-sm font-medium text-gray-700 mb-2 mt-4">Logic</div>
      <div
        v-for="node in logicNodes"
        :key="node.type"
        class="p-3 border border-gray-200 rounded-lg cursor-move hover:bg-gray-50 transition-colors"
        draggable="true"
        @dragstart="onDragStart($event, node)"
      >
        <div class="flex items-center space-x-2">
          <div class="w-3 h-3 rounded-full bg-purple-500"></div>
          <span class="text-sm font-medium">{{ node.label }}</span>
        </div>
        <p class="text-xs text-gray-500 mt-1">{{ node.description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const triggerNodes = ref([
  {
    type: 'gmail_trigger',
    label: 'Gmail Trigger',
    description: 'Trigger on new email'
  },
  {
    type: 'webhook_trigger',
    label: 'Webhook',
    description: 'Trigger on HTTP request'
  },
  {
    type: 'schedule_trigger',
    label: 'Schedule',
    description: 'Trigger on schedule'
  }
])

const actionNodes = ref([
  {
    type: 'gmail_action',
    label: 'Send Email',
    description: 'Send email via Gmail'
  },
  {
    type: 'slack_action',
    label: 'Slack Message',
    description: 'Send Slack message'
  },
  {
    type: 'sheets_action',
    label: 'Google Sheets',
    description: 'Update spreadsheet'
  },
  {
    type: 'http_request',
    label: 'HTTP Request',
    description: 'Make HTTP request'
  }
])

const logicNodes = ref([
  {
    type: 'condition',
    label: 'Condition',
    description: 'If/else logic'
  },
  {
    type: 'transformer',
    label: 'Data Transformer',
    description: 'Transform data'
  },
  {
    type: 'filter',
    label: 'Filter',
    description: 'Filter data'
  }
])

const onDragStart = (event, node) => {
  event.dataTransfer.setData('application/json', JSON.stringify(node))
  event.dataTransfer.effectAllowed = 'copy'
}
</script> 