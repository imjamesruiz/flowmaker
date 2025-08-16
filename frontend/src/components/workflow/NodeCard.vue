<template>
  <div
    ref="nodeRef"
    :class="[
      'workflow-node relative group transition-all duration-200 cursor-grab active:cursor-grabbing',
      'min-w-[200px] max-w-[280px]',
      nodeTypeClass,
      { 'selected': selected, 'dragging': dragging }
    ]"
    :style="nodeStyle"
    @mousedown="handleMouseDown"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
    @click="handleClick"
    @contextmenu="handleContextMenu"
    tabindex="0"
    role="button"
    :aria-label="`${data.label} node`"
    @keydown="handleKeyDown"
  >
    <!-- Input Ports -->
    <div class="absolute left-0 top-0 bottom-0 flex flex-col justify-center">
      <div
        v-for="(input, index) in data.inputs"
        :key="`input-${input.id}`"
        class="relative"
        :style="{ top: `${(index + 1) * (100 / (data.inputs.length + 1))}%` }"
      >
        <div
          :class="[
            'workflow-handle absolute left-[-8px] transform -translate-y-1/2',
            'flex items-center justify-center',
            { 'valid-target': isConnecting && isValidConnection(input) }
          ]"
          :data-port-id="input.id"
          :data-port-direction="'input'"
          @mousedown.stop="startConnection('input', input)"
          @mouseenter="showPortTooltip(input, $event)"
          @mouseleave="hidePortTooltip"
          :title="`${input.label} (${input.type})`"
          role="button"
          tabindex="0"
          :aria-label="`Connect to ${input.label}`"
        >
          <div class="w-2 h-2 bg-current rounded-full"></div>
        </div>
      </div>
    </div>

    <!-- Node Content -->
    <div class="p-4 text-white">
      <!-- Header -->
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center gap-2">
          <component :is="nodeIcon" class="w-4 h-4" />
          <h3 class="font-semibold text-sm leading-tight">{{ data.label }}</h3>
        </div>
        <div class="flex items-center gap-1">
          <component :is="statusIcon" :class="statusIconClass" />
        </div>
      </div>

      <!-- Badge -->
      <div class="flex items-center gap-2 mb-2">
        <span class="px-2 py-1 bg-white/20 rounded-md text-xs font-medium">
          {{ data.type }}
        </span>
        <span v-if="data.status !== 'idle'" class="px-2 py-1 bg-white/20 rounded-md text-xs">
          {{ data.status }}
        </span>
      </div>

      <!-- Description -->
      <p v-if="data.description" class="text-xs text-white/80 leading-relaxed">
        {{ data.description }}
      </p>

      <!-- Port Summary -->
      <div class="flex items-center justify-between text-xs text-white/60 mt-2">
        <span>{{ data.inputs.length }} inputs</span>
        <span>{{ data.outputs.length }} outputs</span>
      </div>
    </div>

    <!-- Output Ports -->
    <div class="absolute right-0 top-0 bottom-0 flex flex-col justify-center">
      <div
        v-for="(output, index) in data.outputs"
        :key="`output-${output.id}`"
        class="relative"
        :style="{ top: `${(index + 1) * (100 / (data.outputs.length + 1))}%` }"
      >
        <div
          :class="[
            'workflow-handle absolute right-[-8px] transform -translate-y-1/2',
            'flex items-center justify-center',
            { 'valid-target': isConnecting && isValidConnection(output) }
          ]"
          :data-port-id="output.id"
          :data-port-direction="'output'"
          @mousedown.stop="startConnection('output', output)"
          @mouseenter="showPortTooltip(output, $event)"
          @mouseleave="hidePortTooltip"
          :title="`${output.label} (${output.type})`"
          role="button"
          tabindex="0"
          :aria-label="`Connect from ${output.label}`"
        >
          <div class="w-2 h-2 bg-current rounded-full"></div>
        </div>
      </div>
    </div>

    <!-- Node Actions (visible on hover/select) -->
    <div
      v-if="selected || isHovered"
      class="absolute -top-10 left-1/2 transform -translate-x-1/2 flex items-center gap-1 bg-white border border-gray-200 rounded-lg px-2 py-1 shadow-lg z-10"
    >
      <button
        @click.stop="configureNode"
        class="p-1 hover:bg-gray-100 rounded transition-colors"
        title="Configure"
        aria-label="Configure node"
      >
        <Settings class="w-3 h-3 text-gray-600" />
      </button>
      <button
        @click.stop="duplicateNode"
        class="p-1 hover:bg-gray-100 rounded transition-colors"
        title="Duplicate"
        aria-label="Duplicate node"
      >
        <Copy class="w-3 h-3 text-gray-600" />
      </button>
      <button
        @click.stop="deleteNode"
        class="p-1 hover:bg-red-50 rounded transition-colors"
        title="Delete"
        aria-label="Delete node"
      >
        <Trash2 class="w-3 h-3 text-red-600" />
      </button>
    </div>

    <!-- Port Tooltip -->
    <div
      v-if="portTooltip.show"
      :class="[
        'workflow-tooltip',
        { 'show': portTooltip.show }
      ]"
      :style="portTooltip.style"
    >
      <div class="font-medium">{{ portTooltip.data?.label }}</div>
      <div class="text-xs opacity-80">{{ portTooltip.data?.type }}</div>
      <div v-if="portTooltip.data?.description" class="text-xs opacity-60 mt-1">
        {{ portTooltip.data.description }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Play,
  Zap,
  GitBranch,
  Code,
  Globe,
  Settings,
  Copy,
  Trash2,
  CheckCircle,
  XCircle,
  AlertCircle,
  Loader
} from 'lucide-vue-next'

const props = defineProps({
  id: {
    type: String,
    required: true
  },
  data: {
    type: Object,
    required: true
  },
  selected: {
    type: Boolean,
    default: false
  },
  dragging: {
    type: Boolean,
    default: false
  },
  isConnecting: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'node-click',
  'node-context-menu',
  'start-connection',
  'configure',
  'duplicate',
  'delete'
])

const nodeRef = ref(null)
const isHovered = ref(false)
const portTooltip = ref({
  show: false,
  data: null,
  style: {}
})

// Node type styling
const nodeTypeClass = computed(() => {
  const typeMap = {
    trigger: 'node-trigger',
    action: 'node-action',
    condition: 'node-condition',
    transformer: 'node-transformer',
    webhook: 'node-webhook'
  }
  return typeMap[props.data.type] || 'node-action'
})

// Node icon
const nodeIcon = computed(() => {
  const iconMap = {
    trigger: Play,
    action: Zap,
    condition: GitBranch,
    transformer: Code,
    webhook: Globe
  }
  return iconMap[props.data.type] || Zap
})

// Status icon
const statusIcon = computed(() => {
  const statusMap = {
    idle: AlertCircle,
    running: Loader,
    success: CheckCircle,
    error: XCircle
  }
  return statusMap[props.data.status] || AlertCircle
})

const statusIconClass = computed(() => {
  const statusMap = {
    idle: 'text-white/60',
    running: 'text-white animate-spin',
    success: 'text-green-300',
    error: 'text-red-300'
  }
  return statusMap[props.data.status] || 'text-white/60'
})

// Node style with gradient
const nodeStyle = computed(() => {
  const gradients = {
    trigger: 'linear-gradient(135deg, #2ECC71 0%, #27AE60 100%)',
    action: 'linear-gradient(135deg, #377DFF 0%, #2563EB 100%)',
    condition: 'linear-gradient(135deg, #F4D03F 0%, #F39C12 100%)',
    transformer: 'linear-gradient(135deg, #8E44AD 0%, #9B59B6 100%)',
    webhook: 'linear-gradient(135deg, #E74C3C 0%, #C0392B 100%)'
  }
  
  return {
    background: gradients[props.data.type] || gradients.action,
    border: `2px solid ${getNodeBorderColor(props.data.type)}`
  }
})

function getNodeBorderColor(type) {
  const colors = {
    trigger: '#2ECC71',
    action: '#377DFF',
    condition: '#F4D03F',
    transformer: '#8E44AD',
    webhook: '#E74C3C'
  }
  return colors[type] || colors.action
}

// Event handlers
const handleMouseDown = (event) => {
  if (event.button === 0) { // Left click
    emit('node-click', { nodeId: props.id, event })
  }
}

const handleMouseEnter = () => {
  isHovered.value = true
}

const handleMouseLeave = () => {
  isHovered.value = false
  hidePortTooltip()
}

const handleClick = (event) => {
  emit('node-click', { nodeId: props.id, event })
}

const handleContextMenu = (event) => {
  event.preventDefault()
  emit('node-context-menu', { nodeId: props.id, event })
}

const handleKeyDown = (event) => {
  switch (event.key) {
    case 'Enter':
      event.preventDefault()
      configureNode()
      break
    case 'Delete':
    case 'Backspace':
      event.preventDefault()
      deleteNode()
      break
    case 'Escape':
      event.preventDefault()
      // Cancel any ongoing operations
      break
  }
}

// Connection handling
const startConnection = (direction, port) => {
  emit('start-connection', {
    nodeId: props.id,
    portId: port.id,
    direction,
    port
  })
}

const isValidConnection = (port) => {
  // For now, allow all connections from output to input
  // In the future, this could check port types, data types, etc.
  return true
}

// Port tooltip
const showPortTooltip = (port, event) => {
  const rect = event.target.getBoundingClientRect()
  portTooltip.value = {
    show: true,
    data: port,
    style: {
      left: `${rect.left + rect.width / 2}px`,
      top: `${rect.top - 10}px`,
      transform: 'translate(-50%, -100%)'
    }
  }
}

const hidePortTooltip = () => {
  portTooltip.value.show = false
}

// Node actions
const configureNode = () => {
  emit('configure', { nodeId: props.id })
}

const duplicateNode = () => {
  emit('duplicate', { nodeId: props.id })
}

const deleteNode = () => {
  emit('delete', { nodeId: props.id })
}

// Focus management
onMounted(() => {
  if (nodeRef.value) {
    nodeRef.value.addEventListener('focus', () => {
      // Handle focus
    })
  }
})

onUnmounted(() => {
  if (nodeRef.value) {
    nodeRef.value.removeEventListener('focus', () => {
      // Cleanup
    })
  }
})
</script>

<style scoped>
.workflow-node {
  user-select: none;
}

.workflow-node:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgb(108 92 231 / 0.6);
}

.workflow-handle {
  z-index: 10;
}

.workflow-handle:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgb(108 92 231 / 0.6);
}

/* Springy drop animation */
.workflow-node.dragging {
  transform: scale(1.05) rotate(2deg);
  transition: transform 0.1s ease;
}

.workflow-node:not(.dragging) {
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* Magnetic snapping visual feedback */
.workflow-node.snapping {
  box-shadow: 0 0 0 4px rgb(108 92 231 / 0.3);
}
</style>
