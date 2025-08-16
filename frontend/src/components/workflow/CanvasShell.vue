<template>
  <div
    ref="canvasContainer"
    :class="[
      'workflow-canvas relative w-full h-full overflow-hidden',
      { 'connecting': isConnecting, 'panning': isPanning }
    ]"
    :data-theme="theme"
    @mousedown="handleMouseDown"
    @mousemove="handleMouseMove"
    @mouseup="handleMouseUp"
    @wheel="handleWheel"
    @keydown="handleKeyDown"
    @drop="handleDrop"
    @dragover="handleDragOver"
    @dragenter="handleDragEnter"
    @dragleave="handleDragLeave"
    tabindex="0"
    role="application"
    aria-label="Workflow canvas"
  >
    <!-- Grid Background -->
    <div class="absolute inset-0 workflow-canvas-grid"></div>

    <!-- Snap Guides -->
    <div
      v-if="snapGuides.show"
      class="absolute pointer-events-none z-10"
    >
      <div
        v-for="guide in snapGuides.guides"
        :key="guide.id"
        :class="[
          'workflow-snap-guide',
          guide.type
        ]"
        :style="guide.style"
      ></div>
    </div>

    <!-- Connection Preview -->
    <svg
      v-if="connectionPreview.show"
      class="absolute inset-0 pointer-events-none z-20"
    >
      <path
        :d="connectionPreview.path"
        :stroke="connectionPreview.color"
        stroke-width="2"
        fill="none"
        stroke-dasharray="5,5"
        opacity="0.6"
      />
    </svg>

    <!-- Canvas Content -->
    <div
      class="absolute inset-0 transform-gpu"
      :style="canvasTransform"
    >
      <slot></slot>
    </div>

    <!-- Zoom Controls -->
    <div class="absolute top-4 left-4 flex flex-col gap-2 z-30">
      <button
        @click="zoomIn"
        class="p-2 bg-white border border-gray-300 rounded-lg shadow-lg hover:bg-gray-50 transition-colors"
        title="Zoom In (Ctrl + +)"
        aria-label="Zoom in"
      >
        <ZoomIn class="w-4 h-4 text-gray-600" />
      </button>
      <button
        @click="zoomOut"
        class="p-2 bg-white border border-gray-300 rounded-lg shadow-lg hover:bg-gray-50 transition-colors"
        title="Zoom Out (Ctrl + -)"
        aria-label="Zoom out"
      >
        <ZoomOut class="w-4 h-4 text-gray-600" />
      </button>
      <button
        @click="resetZoom"
        class="p-2 bg-white border border-gray-300 rounded-lg shadow-lg hover:bg-gray-50 transition-colors"
        title="Reset Zoom (Ctrl + 0)"
        aria-label="Reset zoom"
      >
        <RotateCcw class="w-4 h-4 text-gray-600" />
      </button>
      <button
        @click="fitToContent"
        class="p-2 bg-white border border-gray-300 rounded-lg shadow-lg hover:bg-gray-50 transition-colors"
        title="Fit to Content"
        aria-label="Fit to content"
      >
        <Maximize2 class="w-4 h-4 text-gray-600" />
      </button>
    </div>

    <!-- Mode Indicator -->
    <div class="absolute top-4 right-4 z-30">
      <div
        :class="[
          'px-3 py-1 rounded-lg text-sm font-medium shadow-lg',
          modeIndicatorClass
        ]"
      >
        {{ modeIndicatorText }}
      </div>
    </div>

    <!-- MiniMap -->
    <div
      v-if="showMinimap"
      class="absolute bottom-4 right-4 w-48 h-32 bg-white border border-gray-300 rounded-lg shadow-lg z-30"
    >
      <div class="p-2 border-b border-gray-200">
        <h3 class="text-xs font-medium text-gray-700">MiniMap</h3>
      </div>
      <div class="relative w-full h-24 overflow-hidden">
        <div
          class="absolute inset-0 bg-gray-100"
          :style="minimapStyle"
        >
          <!-- MiniMap content would be rendered here -->
        </div>
        <div
          class="absolute border-2 border-blue-500 bg-blue-500/20"
          :style="viewportIndicator"
        ></div>
      </div>
    </div>

    <!-- Status Bar -->
    <div class="absolute bottom-0 left-0 right-0 h-8 bg-white border-t border-gray-200 flex items-center justify-between px-4 text-sm text-gray-600 z-30">
      <div class="flex items-center gap-4">
        <span>{{ nodeCount }} nodes</span>
        <span>{{ edgeCount }} connections</span>
        <span>Zoom: {{ Math.round(zoom * 100) }}%</span>
      </div>
      <div class="flex items-center gap-2">
        <span v-if="isConnecting" class="text-blue-600">Connecting...</span>
        <span v-if="isPanning" class="text-gray-600">Pan Mode</span>
        <span v-if="isSelecting" class="text-gray-600">Select Mode</span>
      </div>
    </div>

    <!-- Context Menu -->
    <div
      v-if="contextMenu.show"
      :class="[
        'workflow-context-menu',
        'absolute z-50'
      ]"
      :style="contextMenu.style"
    >
      <div
        v-for="item in contextMenu.items"
        :key="item.id"
        :class="[
          'workflow-context-menu-item',
          { 'danger': item.danger }
        ]"
        @click="handleContextMenuAction(item)"
      >
        <component :is="item.icon" class="w-4 h-4" />
        <span>{{ item.label }}</span>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-if="showEmptyState"
      class="absolute inset-0 flex items-center justify-center z-10"
    >
      <div class="text-center">
        <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
          <Plus class="w-8 h-8 text-gray-400" />
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Drop a Trigger to start</h3>
        <p class="text-gray-500 mb-4">Drag nodes from the palette to begin building your workflow</p>
        <div class="flex gap-2 justify-center">
          <button
            v-for="quickNode in quickNodes"
            :key="quickNode.type"
            @click="addQuickNode(quickNode)"
            class="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            {{ quickNode.label }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Maximize2,
  Plus,
  MousePointer,
  Hand,
  GitBranch
} from 'lucide-vue-next'

const props = defineProps({
  theme: {
    type: String,
    default: 'light',
    validator: (value) => ['light', 'dark'].includes(value)
  },
  showMinimap: {
    type: Boolean,
    default: true
  },
  nodeCount: {
    type: Number,
    default: 0
  },
  edgeCount: {
    type: Number,
    default: 0
  },
  showEmptyState: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'canvas-click',
  'canvas-context-menu',
  'zoom-change',
  'pan-change',
  'node-drop',
  'quick-node-add'
])

const canvasContainer = ref(null)
const zoom = ref(1)
const pan = ref({ x: 0, y: 0 })
const isConnecting = ref(false)
const isPanning = ref(false)
const isSelecting = ref(false)
const isDragging = ref(false)
const dragStart = ref(null)

// Snap guides
const snapGuides = ref({
  show: false,
  guides: []
})

// Connection preview
const connectionPreview = ref({
  show: false,
  path: '',
  color: '#6C5CE7'
})

// Context menu
const contextMenu = ref({
  show: false,
  x: 0,
  y: 0,
  items: []
})

// Quick nodes for empty state
const quickNodes = [
  { type: 'trigger', label: 'Gmail Trigger', icon: 'Mail' },
  { type: 'action', label: 'Send Email', icon: 'Send' },
  { type: 'condition', label: 'Filter', icon: 'Filter' }
]

// Computed properties
const canvasTransform = computed(() => ({
  transform: `translate(${pan.value.x}px, ${pan.value.y}px) scale(${zoom.value})`
}))

const modeIndicatorClass = computed(() => {
  if (isConnecting.value) return 'bg-blue-100 text-blue-700'
  if (isPanning.value) return 'bg-gray-100 text-gray-700'
  if (isSelecting.value) return 'bg-purple-100 text-purple-700'
  return 'bg-green-100 text-green-700'
})

const modeIndicatorText = computed(() => {
  if (isConnecting.value) return 'Connecting'
  if (isPanning.value) return 'Pan Mode'
  if (isSelecting.value) return 'Select Mode'
  return 'Ready'
})

const minimapStyle = computed(() => ({
  transform: `scale(${0.1})`,
  transformOrigin: 'top left'
}))

const viewportIndicator = computed(() => ({
  left: `${-pan.value.x * 0.1}px`,
  top: `${-pan.value.y * 0.1}px`,
  width: `${canvasContainer.value?.clientWidth * 0.1}px`,
  height: `${canvasContainer.value?.clientHeight * 0.1}px`
}))

// Event handlers
const handleMouseDown = (event) => {
  if (event.button === 0) { // Left click
    if (event.ctrlKey || event.metaKey) {
      isSelecting.value = true
    } else {
      isPanning.value = true
    }
    isDragging.value = true
    dragStart.value = { x: event.clientX, y: event.clientY }
  }
}

const handleMouseMove = (event) => {
  if (isDragging.value && dragStart.value) {
    const deltaX = event.clientX - dragStart.value.x
    const deltaY = event.clientY - dragStart.value.y
    
    if (isPanning.value) {
      pan.value.x += deltaX
      pan.value.y += deltaY
      emit('pan-change', pan.value)
    }
    
    dragStart.value = { x: event.clientX, y: event.clientY }
  }
  
  // Auto-pan when near edges
  if (isConnecting.value) {
    autoPan(event)
  }
}

const handleMouseUp = () => {
  isDragging.value = false
  isPanning.value = false
  isSelecting.value = false
  dragStart.value = null
}

const handleWheel = (event) => {
  event.preventDefault()
  
  if (event.ctrlKey || event.metaKey) {
    // Zoom
    const delta = event.deltaY > 0 ? 0.9 : 1.1
    const newZoom = Math.max(0.1, Math.min(3, zoom.value * delta))
    zoom.value = newZoom
    emit('zoom-change', newZoom)
  } else {
    // Pan
    pan.value.x -= event.deltaX
    pan.value.y -= event.deltaY
    emit('pan-change', pan.value)
  }
}

const handleKeyDown = (event) => {
  switch (event.key) {
    case ' ':
      event.preventDefault()
      isPanning.value = !isPanning.value
      break
    case 'Escape':
      isConnecting.value = false
      isPanning.value = false
      isSelecting.value = false
      break
    case 'Delete':
    case 'Backspace':
      // Delete selected items
      break
    case 'a':
      if (event.ctrlKey || event.metaKey) {
        event.preventDefault()
        // Select all
      }
      break
  }
}

const handleDrop = (event) => {
  event.preventDefault()
  const nodeData = JSON.parse(event.dataTransfer.getData('application/json'))
  const rect = canvasContainer.value.getBoundingClientRect()
  const x = (event.clientX - rect.left - pan.value.x) / zoom.value
  const y = (event.clientY - rect.top - pan.value.y) / zoom.value
  
  emit('node-drop', { nodeData, position: { x, y } })
}

const handleDragOver = (event) => {
  event.preventDefault()
}

const handleDragEnter = (event) => {
  event.preventDefault()
}

const handleDragLeave = (event) => {
  event.preventDefault()
}

// Zoom controls
const zoomIn = () => {
  const newZoom = Math.min(3, zoom.value * 1.2)
  zoom.value = newZoom
  emit('zoom-change', newZoom)
}

const zoomOut = () => {
  const newZoom = Math.max(0.1, zoom.value / 1.2)
  zoom.value = newZoom
  emit('zoom-change', newZoom)
}

const resetZoom = () => {
  zoom.value = 1
  emit('zoom-change', 1)
}

const fitToContent = () => {
  // This would calculate the optimal zoom and pan to fit all content
  emit('fit-to-content')
}

// Auto-pan functionality
const autoPan = (event) => {
  if (!canvasContainer.value) return
  
  const rect = canvasContainer.value.getBoundingClientRect()
  const threshold = 100
  const panSpeed = 10
  
  if (event.clientX < rect.left + threshold) {
    pan.value.x += panSpeed
  } else if (event.clientX > rect.right - threshold) {
    pan.value.x -= panSpeed
  }
  
  if (event.clientY < rect.top + threshold) {
    pan.value.y += panSpeed
  } else if (event.clientY > rect.bottom - threshold) {
    pan.value.y -= panSpeed
  }
}

// Quick node addition
const addQuickNode = (node) => {
  emit('quick-node-add', node)
}

// Context menu handling
const handleContextMenuAction = (item) => {
  contextMenu.value.show = false
  // Handle the action
}

// Snap guides
const showSnapGuides = (guides) => {
  snapGuides.value = {
    show: true,
    guides
  }
}

const hideSnapGuides = () => {
  snapGuides.value.show = false
}

// Connection preview
const showConnectionPreview = (path, color = '#6C5CE7') => {
  connectionPreview.value = {
    show: true,
    path,
    color
  }
}

const hideConnectionPreview = () => {
  connectionPreview.value.show = false
}

// Expose methods
defineExpose({
  zoom,
  pan,
  zoomIn,
  zoomOut,
  resetZoom,
  fitToContent,
  showSnapGuides,
  hideSnapGuides,
  showConnectionPreview,
  hideConnectionPreview
})

onMounted(() => {
  // Focus the canvas for keyboard events
  canvasContainer.value?.focus()
})

onUnmounted(() => {
  // Cleanup
})
</script>

<style scoped>
.workflow-canvas {
  outline: none;
}

.workflow-canvas:focus {
  outline: none;
}

.workflow-canvas.connecting {
  cursor: crosshair;
}

.workflow-canvas.panning {
  cursor: grab;
}

.workflow-canvas.panning:active {
  cursor: grabbing;
}

.workflow-canvas-grid {
  background-image: 
    linear-gradient(var(--grid-color) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid-color) 1px, transparent 1px);
  background-size: var(--grid-size) var(--grid-size);
}

.workflow-canvas-grid::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(var(--grid-major-color) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid-major-color) 1px, transparent 1px);
  background-size: var(--grid-major) var(--grid-major);
  pointer-events: none;
}

/* Smooth transitions */
.transform-gpu {
  transform: translateZ(0);
}

/* Selection rectangle */
.selection-rect {
  position: absolute;
  border: 1px solid var(--color-primary);
  background: rgb(108 92 231 / 0.1);
  pointer-events: none;
  z-index: 1000;
}
</style>
