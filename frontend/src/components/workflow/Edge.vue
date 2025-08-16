<template>
  <g
    :class="[
      'workflow-edge-group',
      { 'selected': selected, 'hovered': isHovered }
    ]"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
    @click="handleClick"
    @contextmenu="handleContextMenu"
  >
    <!-- Main Edge Path -->
    <path
      :d="edgePath"
      :stroke="edgeColor"
      :stroke-width="edgeWidth"
      fill="none"
      :class="[
        'workflow-edge transition-all duration-200',
        { 'selected': selected }
      ]"
      :marker-end="`url(#arrow-${id})`"
    />

    <!-- Edge Label -->
    <foreignObject
      v-if="data?.label"
      :width="labelWidth"
      :height="labelHeight"
      :x="labelPosition.x"
      :y="labelPosition.y"
      class="pointer-events-none"
    >
      <div class="flex items-center justify-center h-full">
        <div
          :class="[
            'workflow-edge-label bg-white border border-gray-200 rounded-lg px-2 py-1 shadow-lg cursor-pointer',
            'hover:border-blue-500 hover:shadow-md transition-all duration-200',
            'flex items-center gap-1 text-xs font-medium'
          ]"
          @click="handleLabelClick"
          @dblclick="startLabelEdit"
        >
          <component :is="edgeIcon" class="w-3 h-3" />
          <span class="truncate">{{ data.label }}</span>
          <span v-if="data?.condition" class="ml-1 px-1 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
            {{ data.condition }}
          </span>
        </div>
      </div>
    </foreignObject>

    <!-- Edge Context Menu -->
    <foreignObject
      v-if="isHovered"
      :width="40"
      :height="40"
      :x="contextMenuPosition.x"
      :y="contextMenuPosition.y"
      class="pointer-events-auto"
    >
      <div class="flex items-center justify-center h-full">
        <button
          @click="showContextMenu"
          class="h-8 w-8 p-0 bg-white border border-gray-200 shadow-lg hover:bg-gray-50 rounded-md flex items-center justify-center transition-colors"
          title="Edge options"
        >
          <MoreHorizontal class="w-4 h-4 text-gray-600" />
        </button>
      </div>
    </foreignObject>

    <!-- Error Tooltip -->
    <foreignObject
      v-if="data?.type === 'error' && data?.errorMessage"
      :width="200"
      :height="60"
      :x="errorPosition.x"
      :y="errorPosition.y"
      class="pointer-events-none"
    >
      <div class="bg-red-50 border border-red-200 rounded-lg px-2 py-1 text-xs text-red-700 cursor-help">
        ⚠️ {{ data.errorMessage }}
      </div>
    </foreignObject>

    <!-- Arrow Marker Definition -->
    <defs>
      <marker
        :id="`arrow-${id}`"
        viewBox="0 0 10 10"
        refX="5"
        refY="5"
        markerWidth="6"
        markerHeight="6"
        orient="auto-start-reverse"
      >
        <path
          d="M 0 0 L 10 5 L 0 10 z"
          :fill="edgeColor"
        />
      </marker>
    </defs>
  </g>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  MoreHorizontal,
  Edit,
  Trash2,
  Copy,
  GitBranch,
  ArrowRight,
  AlertCircle,
  CheckCircle,
  X
} from 'lucide-vue-next'

const props = defineProps({
  id: {
    type: String,
    required: true
  },
  sourceX: {
    type: Number,
    required: true
  },
  sourceY: {
    type: Number,
    required: true
  },
  targetX: {
    type: Number,
    required: true
  },
  targetY: {
    type: Number,
    required: true
  },
  sourcePosition: {
    type: String,
    default: 'right'
  },
  targetPosition: {
    type: String,
    default: 'left'
  },
  data: {
    type: Object,
    default: () => ({})
  },
  selected: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'edge-click',
  'edge-context-menu',
  'edge-label-edit',
  'edge-rename',
  'edge-delete'
])

const isHovered = ref(false)
const isEditing = ref(false)
const editValue = ref('')

// Edge path calculation with orthogonal routing
const edgePath = computed(() => {
  const offset = 50
  const midX = (props.sourceX + props.targetX) / 2
  
  // Create orthogonal path with rounded corners
  const path = [
    `M ${props.sourceX} ${props.sourceY}`,
    `L ${props.sourceX + offset} ${props.sourceY}`,
    `L ${props.sourceX + offset} ${props.targetY}`,
    `L ${props.targetX} ${props.targetY}`,
  ].join(' ')
  
  return path
})

// Edge styling
const edgeColor = computed(() => {
  if (props.data?.type === 'error') return '#EF4444'
  if (props.data?.type === 'success') return '#22C55E'
  if (props.data?.type === 'conditional') return '#8B5CF6'
  if (props.selected) return '#6C5CE7'
  if (isHovered.value) return '#6B7280'
  return '#9CA3AF'
})

const edgeWidth = computed(() => {
  if (props.selected) return 3
  if (isHovered.value) return 2.5
  return 2
})

// Edge icon
const edgeIcon = computed(() => {
  if (props.data?.type === 'conditional') return GitBranch
  if (props.data?.type === 'error') return AlertCircle
  if (props.data?.type === 'success') return CheckCircle
  return ArrowRight
})

// Label positioning
const labelWidth = computed(() => {
  const baseWidth = 120
  const conditionWidth = props.data?.condition ? 60 : 0
  return baseWidth + conditionWidth
})

const labelHeight = computed(() => 40)

const labelPosition = computed(() => {
  const x = (props.sourceX + props.targetX) / 2 - labelWidth.value / 2
  const y = (props.sourceY + props.targetY) / 2 - labelHeight.value / 2
  return { x, y }
})

// Context menu positioning
const contextMenuPosition = computed(() => {
  const x = (props.sourceX + props.targetX) / 2 + 70
  const y = (props.sourceY + props.targetY) / 2 - 20
  return { x, y }
})

// Error tooltip positioning
const errorPosition = computed(() => {
  const x = (props.sourceX + props.targetX) / 2 - 100
  const y = (props.sourceY + props.targetY) / 2 + 30
  return { x, y }
})

// Event handlers
const handleMouseEnter = () => {
  isHovered.value = true
}

const handleMouseLeave = () => {
  isHovered.value = false
}

const handleClick = (event) => {
  emit('edge-click', { edgeId: props.id, event })
}

const handleContextMenu = (event) => {
  event.preventDefault()
  emit('edge-context-menu', { edgeId: props.id, event })
}

const handleLabelClick = () => {
  if (!isEditing.value) {
    emit('edge-label-edit', { edgeId: props.id, label: props.data?.label })
  }
}

const startLabelEdit = () => {
  isEditing.value = true
  editValue.value = props.data?.label || ''
}

const showContextMenu = () => {
  // This would trigger a context menu component
  emit('edge-context-menu', { edgeId: props.id })
}

// Keyboard navigation
const handleKeyDown = (event) => {
  switch (event.key) {
    case 'Enter':
      event.preventDefault()
      handleLabelClick()
      break
    case 'Delete':
    case 'Backspace':
      event.preventDefault()
      emit('edge-delete', { edgeId: props.id })
      break
    case 'Escape':
      event.preventDefault()
      isEditing.value = false
      break
  }
}

onMounted(() => {
  // Add keyboard event listeners if needed
})

onUnmounted(() => {
  // Cleanup
})
</script>

<style scoped>
.workflow-edge-group {
  cursor: pointer;
}

.workflow-edge {
  pointer-events: all;
}

.workflow-edge:hover {
  filter: drop-shadow(0 0 8px var(--color-primary));
}

.workflow-edge.selected {
  filter: drop-shadow(0 0 12px var(--color-primary));
}

.workflow-edge-label {
  pointer-events: auto;
}

.workflow-edge-label:hover {
  transform: scale(1.05);
}

/* Edge animation for new connections */
.workflow-edge.new-connection {
  stroke-dasharray: 5, 5;
  animation: edgeDash 1s linear infinite;
}

@keyframes edgeDash {
  to {
    stroke-dashoffset: -10;
  }
}

/* Edge validation states */
.workflow-edge.valid {
  stroke: var(--color-success);
}

.workflow-edge.invalid {
  stroke: var(--color-error);
  stroke-dasharray: 3, 3;
}

.workflow-edge.warning {
  stroke: var(--color-warning);
  stroke-dasharray: 2, 2;
}
</style>
