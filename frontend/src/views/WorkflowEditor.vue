<template>
  <div class="h-screen flex flex-col bg-gray-50">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <router-link
            to="/workflows"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <ArrowLeft class="w-6 h-6" />
          </router-link>
          <div>
            <input
              v-model="workflow.name"
              type="text"
              class="text-xl font-semibold text-gray-900 bg-transparent border-none focus:outline-none focus:ring-0"
              placeholder="Untitled Workflow"
              @blur="saveWorkflow"
            />
            <p class="text-sm text-gray-500">{{ workflow.description || 'No description' }}</p>
          </div>
        </div>
        
        <div class="flex items-center space-x-3">
          <!-- Validation Status -->
          <div v-if="!validateAllConnections().valid" class="flex items-center text-red-600 text-sm">
            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            Invalid connections
          </div>
          
          <button
            @click="testWorkflow"
            :disabled="!workflow.nodes.length"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Play class="w-4 h-4 mr-2" />
            Test
          </button>
          <button
            @click="saveWorkflow"
            :disabled="saving || !validateAllConnections().valid"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Save class="w-4 h-4 mr-2" />
            {{ saving ? 'Saving...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex">
      <!-- Sidebar -->
      <div class="w-64 bg-white border-r border-gray-200 flex flex-col">
        <!-- Node Palette -->
        <div class="p-4 border-b border-gray-200">
          <h3 class="text-sm font-medium text-gray-900 mb-3">Nodes</h3>
          <div class="space-y-2">
            <div
              v-for="nodeType in nodeTypes"
              :key="nodeType.type"
              class="flex items-center p-3 border border-gray-200 rounded-lg cursor-move hover:bg-gray-50 hover:border-gray-300 transition-all duration-200"
              draggable="true"
              @dragstart="handleDragStart($event, nodeType)"
            >
              <div class="w-3 h-3 rounded-full mr-3" :class="nodeType.colorClass"></div>
              <div class="flex-1">
                <span class="text-sm font-medium text-gray-700">{{ nodeType.label }}</span>
                <p class="text-xs text-gray-500">{{ nodeType.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Properties Panel -->
        <div class="flex-1 p-4 overflow-y-auto">
          <h3 class="text-sm font-medium text-gray-900 mb-3">Properties</h3>
          <div v-if="selectedNode" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
              <input
                v-model="selectedNode.name"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                @blur="updateNode"
              />
            </div>
            
            <div v-if="selectedNode.node_type === 'trigger'">
              <label class="block text-sm font-medium text-gray-700 mb-1">Trigger Type</label>
              <select
                v-model="selectedNode.config.trigger_type"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                @change="updateNode"
              >
                <option value="webhook">Webhook</option>
                <option value="schedule">Schedule</option>
                <option value="gmail_new_email">Gmail - New Email</option>
                <option value="slack_message">Slack - New Message</option>
              </select>
            </div>
            
            <div v-if="selectedNode.node_type === 'action'">
              <label class="block text-sm font-medium text-gray-700 mb-1">Action Type</label>
              <select
                v-model="selectedNode.config.action_type"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                @change="updateNode"
              >
                <option value="gmail_send_email">Gmail - Send Email</option>
                <option value="slack_send_message">Slack - Send Message</option>
                <option value="sheets_update">Google Sheets - Update</option>
                <option value="http_request">HTTP Request</option>
              </select>
            </div>
            
            <div v-if="selectedNode.node_type === 'condition'">
              <label class="block text-sm font-medium text-gray-700 mb-1">Condition Type</label>
              <select
                v-model="selectedNode.config.condition_type"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                @change="updateNode"
              >
                <option value="simple">Simple</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <!-- Node Status -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <div class="flex items-center space-x-2">
                <div class="w-2 h-2 rounded-full" :class="statusColorClass"></div>
                <span class="text-sm text-gray-600 capitalize">{{ selectedNode.status || 'idle' }}</span>
              </div>
            </div>
          </div>
          <div v-else class="text-sm text-gray-500 text-center py-8">
            <MousePointer class="w-8 h-8 mx-auto mb-2 text-gray-400" />
            <p>Select a node to edit its properties</p>
          </div>
        </div>
      </div>

      <!-- Canvas -->
      <div class="flex-1 relative bg-gray-100 overflow-hidden">
        <!-- Canvas Container -->
        <div
          ref="canvasContainer"
          class="w-full h-full relative"
          @mousedown="handleCanvasMouseDown"
          @mousemove="handleCanvasMouseMove"
          @mouseup="handleCanvasMouseUp"
          @drop="handleCanvasDrop"
          @dragover="handleCanvasDragOver"
          @dragenter="handleCanvasDragEnter"
          @dragleave="handleCanvasDragLeave"
          @wheel="handleCanvasWheel"
          @click="handleCanvasClick"
        >
          <!-- Grid Background -->
          <div class="absolute inset-0 bg-grid-pattern opacity-20"></div>
          
          <!-- Connection Preview -->
          <svg
            v-if="connectionPreview.show"
            class="absolute inset-0 pointer-events-none z-10"
          >
            <path
              :d="connectionPreview.path"
              :stroke="connectionPreview.color"
              stroke-width="3"
              fill="none"
              stroke-dasharray="8,4"
              opacity="0.8"
              marker-end="url(#arrowhead)"
            />
            <defs>
              <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="7"
                refX="9"
                refY="3.5"
                orient="auto"
              >
                <polygon
                  points="0 0, 10 3.5, 0 7"
                  :fill="connectionPreview.color"
                />
              </marker>
            </defs>
          </svg>

          <!-- Nodes -->
          <div
            v-for="node in workflow.nodes"
            :key="node.node_id"
            :data-node-id="node.node_id"
            :style="{
              position: 'absolute',
              left: `${node.position_x}px`,
              top: `${node.position_y}px`,
              zIndex: selectedNode?.node_id === node.node_id ? 20 : 10
            }"
            class="node-container"
            @mousedown.stop="handleNodeMouseDown($event, node)"
            @click.stop="handleNodeClick(node)"
          >
            <NodeCard
              :id="node.node_id"
              :data="getNodeData(node)"
              :selected="selectedNode?.node_id === node.node_id"
              :dragging="draggedNode?.node_id === node.node_id"
              :is-connecting="isConnecting"
              @start-connection="handleStartConnection"
              @configure="handleNodeConfigure"
              @duplicate="handleNodeDuplicate"
              @delete="handleNodeDelete"
            />
          </div>

          <!-- Connections -->
          <svg class="absolute inset-0 pointer-events-none z-5">
            <Edge
              v-for="connection in workflow.connections"
              :key="connection.id"
              :id="connection.id"
              :source-x="getPortPosition(connection.source_node_id, 'output').x"
              :source-y="getPortPosition(connection.source_node_id, 'output').y"
              :target-x="getPortPosition(connection.target_node_id, 'input').x"
              :target-y="getPortPosition(connection.target_node_id, 'input').y"
              :data="getEdgeData(connection)"
              :selected="selectedConnection?.id === connection.id"
              @edge-click="handleEdgeClick"
              @edge-context-menu="handleEdgeContextMenu"
              @edge-label-edit="handleEdgeLabelEdit"
              @edge-rename="handleEdgeRename"
              @edge-delete="handleEdgeDelete"
            />
          </svg>
        </div>

        <!-- Zoom Controls -->
        <div class="absolute top-4 left-4 flex flex-col gap-2 z-30">
          <button
            @click="zoomIn"
            class="p-2 bg-white border border-gray-300 rounded-lg shadow-lg hover:bg-gray-50 transition-colors"
            title="Zoom In"
          >
            <ZoomIn class="w-4 h-4 text-gray-600" />
          </button>
          <button
            @click="zoomOut"
            class="p-2 bg-white border border-gray-300 rounded-lg shadow-lg hover:bg-gray-50 transition-colors"
            title="Zoom Out"
          >
            <ZoomOut class="w-4 h-4 text-gray-600" />
          </button>
          <button
            @click="resetZoom"
            class="p-2 bg-white border border-gray-300 rounded-lg shadow-lg hover:bg-gray-50 transition-colors"
            title="Reset Zoom"
          >
            <RotateCcw class="w-4 h-4 text-gray-600" />
          </button>
        </div>

        <!-- Connection Mode Indicator -->
        <div
          v-if="isConnecting"
          class="absolute top-4 right-4 px-3 py-2 bg-blue-600 text-white rounded-lg shadow-lg z-30"
        >
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 bg-white rounded-full animate-pulse"></div>
            <span class="text-sm font-medium">Connecting...</span>
            <button
              @click="cancelConnection"
              class="ml-2 text-white/80 hover:text-white"
            >
              <X class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Empty State -->
        <div
          v-if="workflow.nodes.length === 0"
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
                v-for="quickNode in nodeTypes.slice(0, 3)"
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
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useWorkflowsStore } from '@/stores/workflows'
import { useToast } from 'vue-toastification'
import {
  ArrowLeft,
  Play,
  Save,
  MousePointer,
  Plus,
  Settings,
  Copy,
  Trash2,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  X
} from 'lucide-vue-next'

// Import components
import NodeCard from '@/components/workflow/NodeCard.vue'
import Edge from '@/components/workflow/Edge.vue'

const route = useRoute()
const router = useRouter()
const workflowsStore = useWorkflowsStore()
const toast = useToast()

// Canvas refs
const canvasContainer = ref(null)
const selectedNode = ref(null)
const selectedConnection = ref(null)
const saving = ref(false)
const isConnecting = ref(false)
const theme = ref('light')

// Canvas state
const zoom = ref(1)
const pan = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const isPanning = ref(false)
const draggedNode = ref(null)
const dragStart = ref({ x: 0, y: 0 })

// Connection state
const connectionPreview = ref({
  show: false,
  path: '',
  color: '#6C5CE7'
})
const connectionStart = ref(null)

const workflow = reactive({
  id: null,
  name: 'Untitled Workflow',
  description: '',
  nodes: [],
  connections: []
})

const nodeTypes = [
  {
    type: 'trigger',
    label: 'Trigger',
    description: 'Start your workflow',
    colorClass: 'bg-green-500'
  },
  {
    type: 'action',
    label: 'Action',
    description: 'Perform an action',
    colorClass: 'bg-blue-500'
  },
  {
    type: 'condition',
    label: 'Condition',
    description: 'Make decisions',
    colorClass: 'bg-yellow-500'
  },
  {
    type: 'transformer',
    label: 'Transformer',
    description: 'Transform data',
    colorClass: 'bg-purple-500'
  },
  {
    type: 'webhook',
    label: 'Webhook',
    description: 'External trigger',
    colorClass: 'bg-red-500'
  }
]

// Node data mapping
const getNodeData = (node) => {
  const typeMap = {
    trigger: {
      inputs: [],
      outputs: [
        { id: 'trigger', label: 'Trigger', type: 'object', required: false }
      ]
    },
    action: {
      inputs: [
        { id: 'input', label: 'Input', type: 'object', required: true }
      ],
      outputs: [
        { id: 'output', label: 'Output', type: 'object', required: false }
      ]
    },
    condition: {
      inputs: [
        { id: 'input', label: 'Input', type: 'object', required: true }
      ],
      outputs: [
        { id: 'true', label: 'True', type: 'object', required: false },
        { id: 'false', label: 'False', type: 'object', required: false }
      ]
    },
    transformer: {
      inputs: [
        { id: 'input', label: 'Input', type: 'object', required: true }
      ],
      outputs: [
        { id: 'output', label: 'Output', type: 'object', required: false }
      ]
    },
    webhook: {
      inputs: [],
      outputs: [
        { id: 'webhook', label: 'Webhook', type: 'object', required: false }
      ]
    }
  }

  return {
    label: node.name,
    type: node.node_type,
    status: node.status || 'idle',
    description: node.description,
    ...typeMap[node.node_type] || typeMap.action
  }
}

const getEdgeData = (connection) => {
  return {
    label: connection.label || 'Connection',
    type: connection.is_valid ? 'default' : 'error',
    errorMessage: connection.is_valid ? null : 'Invalid connection'
  }
}

const getNodePosition = (nodeId) => {
  const node = workflow.nodes.find(n => n.node_id === nodeId)
  return node ? { x: node.position_x, y: node.position_y } : { x: 0, y: 0 }
}

const getPortPosition = (nodeId, portDirection) => {
  const node = workflow.nodes.find(n => n.node_id === nodeId)
  if (!node) return { x: 0, y: 0 }
  
  // Calculate port position based on node position and direction
  const nodeWidth = 280
  const nodeHeight = 120
  const portOffset = 16
  
  if (portDirection === 'output') {
    // Output port on right side
    return {
      x: node.position_x + nodeWidth + portOffset,
      y: node.position_y + nodeHeight / 2
    }
  } else {
    // Input port on left side
    return {
      x: node.position_x - portOffset,
      y: node.position_y + nodeHeight / 2
    }
  }
}

const statusColorClass = computed(() => {
  if (!selectedNode.value) return 'bg-gray-400'
  
  const statusMap = {
    idle: 'bg-gray-400',
    running: 'bg-blue-500',
    success: 'bg-green-500',
    error: 'bg-red-500'
  }
  return statusMap[selectedNode.value.status] || 'bg-gray-400'
})

// Canvas event handlers
const handleCanvasMouseDown = (event) => {
  if (event.button === 0) { // Left click
    if (event.altKey || event.metaKey) {
      // Start panning
      isPanning.value = true
      dragStart.value = { x: event.clientX, y: event.clientY }
    } else {
      // Deselect nodes
      selectedNode.value = null
      selectedConnection.value = null
    }
  }
}

const handleCanvasMouseMove = (event) => {
  if (isPanning.value) {
    const deltaX = event.clientX - dragStart.value.x
    const deltaY = event.clientY - dragStart.value.y
    pan.value.x += deltaX
    pan.value.y += deltaY
    dragStart.value = { x: event.clientX, y: event.clientY }
  }
  
  if (isDragging.value && draggedNode.value) {
    const deltaX = event.clientX - dragStart.value.x
    const deltaY = event.clientY - dragStart.value.y
    
    draggedNode.value.position_x += deltaX / zoom.value
    draggedNode.value.position_y += deltaY / zoom.value
    
    dragStart.value = { x: event.clientX, y: event.clientY }
  }
  
  if (isConnecting.value && connectionStart.value) {
    updateConnectionPreview(event.clientX, event.clientY)
  }
}

const handleCanvasMouseUp = () => {
  if (isDragging.value && draggedNode.value) {
    // Save the workflow after dragging
    saveWorkflow()
  }
  
  isPanning.value = false
  isDragging.value = false
  draggedNode.value = null
}

const handleCanvasDrop = (event) => {
  event.preventDefault()
  const nodeType = JSON.parse(event.dataTransfer.getData('application/json'))
  const rect = canvasContainer.value.getBoundingClientRect()
  const x = (event.clientX - rect.left - pan.value.x) / zoom.value
  const y = (event.clientY - rect.top - pan.value.y) / zoom.value
  
  addNode(nodeType, { x, y })
}

const handleCanvasDragOver = (event) => {
  event.preventDefault()
}

const handleCanvasDragEnter = (event) => {
  event.preventDefault()
}

const handleCanvasDragLeave = (event) => {
  event.preventDefault()
}

const handleCanvasWheel = (event) => {
  if (event.ctrlKey || event.metaKey) {
    event.preventDefault()
    const delta = event.deltaY > 0 ? 0.9 : 1.1
    zoom.value = Math.max(0.1, Math.min(3, zoom.value * delta))
  }
}

const handleCanvasClick = () => {
  selectedNode.value = null
  selectedConnection.value = null
}

// Node event handlers
const handleNodeMouseDown = (event, node) => {
  if (event.button === 0) { // Left click
    isDragging.value = true
    draggedNode.value = node
    dragStart.value = { x: event.clientX, y: event.clientY }
    selectedNode.value = node
  }
}

const handleNodeClick = (node) => {
  selectedNode.value = node
  selectedConnection.value = null
}

// Connection handlers
const handleStartConnection = ({ nodeId, portId, direction, port }) => {
  console.log('Starting connection:', { nodeId, portId, direction, port })
  isConnecting.value = true
  connectionStart.value = { nodeId, portId, direction, port }
  
  // Add event listeners for connection
  document.addEventListener('mousemove', handleConnectionMouseMove)
  document.addEventListener('mouseup', handleConnectionMouseUp)
}

const handleConnectionMouseMove = (event) => {
  if (isConnecting.value && connectionStart.value) {
    updateConnectionPreview(event.clientX, event.clientY)
  }
}

const handleConnectionMouseUp = (event) => {
  if (isConnecting.value) {
    // Find target node and port
    const targetElement = event.target.closest('.workflow-handle')
    if (targetElement && connectionStart.value) {
      const targetNodeContainer = targetElement.closest('.node-container')
      if (targetNodeContainer) {
        const targetNodeId = targetNodeContainer.getAttribute('data-node-id')
        const targetPortId = targetElement.getAttribute('data-port-id')
        const targetDirection = targetElement.getAttribute('data-port-direction')
        
        console.log('Connection attempt:', {
          sourceNode: connectionStart.value.nodeId,
          sourcePort: connectionStart.value.portId,
          sourceDirection: connectionStart.value.direction,
          targetNode: targetNodeId,
          targetPort: targetPortId,
          targetDirection: targetDirection
        })
        
        // Validate connection
        if (isValidConnection(connectionStart.value.nodeId, connectionStart.value.portId, targetNodeId, targetPortId)) {
          createConnection(connectionStart.value.nodeId, connectionStart.value.portId, targetNodeId, targetPortId)
          toast.success('Connection created')
        } else {
          console.log('Invalid connection attempt')
          toast.error('Invalid connection')
        }
      }
    }
    
    cancelConnection()
  }
  
  document.removeEventListener('mousemove', handleConnectionMouseMove)
  document.removeEventListener('mouseup', handleConnectionMouseUp)
}

const isValidConnection = (sourceNodeId, sourcePortId, targetNodeId, targetPortId) => {
  // 1. Prevent self-loops
  if (sourceNodeId === targetNodeId) {
    return false
  }
  
  // 2. Only allow connections from output to input
  const sourceNode = workflow.nodes.find(n => n.node_id === sourceNodeId)
  const targetNode = workflow.nodes.find(n => n.node_id === targetNodeId)
  
  if (!sourceNode || !targetNode) {
    return false
  }
  
  // 3. Validate port directions - only output to input connections are allowed
  if (sourcePortId === 'input' || targetPortId === 'output') {
    return false
  }
  
  // 4. Check if target port already has a connection
  const existingConnection = workflow.connections.find(
    c => c.target_node_id === targetNodeId && c.target_port === targetPortId
  )
  
  if (existingConnection) {
    return false
  }
  
  // 5. Check if this exact connection already exists
  const duplicateConnection = workflow.connections.find(
    c => c.source_node_id === sourceNodeId && 
         c.source_port === sourcePortId && 
         c.target_node_id === targetNodeId && 
         c.target_port === targetPortId
  )
  
  if (duplicateConnection) {
    return false
  }
  
  // 6. Validate port types for condition nodes
  if (targetNode.node_type === 'condition' && targetPortId === 'input') {
    // Condition nodes can only have one input
    const conditionInputs = workflow.connections.filter(
      c => c.target_node_id === targetNodeId && c.target_port === 'input'
    )
    if (conditionInputs.length > 0) {
      return false
    }
  }
  
  return true
}

const updateConnectionPreview = (mouseX, mouseY) => {
  if (!connectionStart.value) return
  
  const startNode = workflow.nodes.find(n => n.node_id === connectionStart.value.nodeId)
  if (!startNode) return
  
  // Calculate start position using the same logic as getPortPosition
  const nodeWidth = 280
  const nodeHeight = 120
  const portOffset = 16
  const startX = startNode.position_x + nodeWidth + portOffset
  const startY = startNode.position_y + nodeHeight / 2
  
  // Calculate end position (mouse position)
  const rect = canvasContainer.value.getBoundingClientRect()
  const endX = (mouseX - rect.left - pan.value.x) / zoom.value
  const endY = (mouseY - rect.top - pan.value.y) / zoom.value
  
  // Create orthogonal path with better routing
  const midX = startX + Math.max(50, (endX - startX) / 2)
  const path = `M ${startX} ${startY} L ${midX} ${startY} L ${midX} ${endY} L ${endX} ${endY}`
  
  connectionPreview.value = {
    show: true,
    path,
    color: '#6C5CE7'
  }
}

const cancelConnection = () => {
  isConnecting.value = false
  connectionStart.value = null
  connectionPreview.value.show = false
}

const createConnection = (sourceNodeId, sourcePortId, targetNodeId, targetPortId) => {
  const connectionId = `conn_${Date.now()}`
  const newConnection = {
    id: connectionId,
    source_node_id: sourceNodeId,
    target_node_id: targetNodeId,
    source_port: sourcePortId,
    target_port: targetPortId,
    is_valid: true
  }
  
  workflow.connections.push(newConnection)
  saveWorkflow(true) // Trigger autosave
}

// Node management
const handleDragStart = (event, nodeType) => {
  event.dataTransfer.setData('application/json', JSON.stringify(nodeType))
}

const addNode = (nodeType, position) => {
  const nodeId = `node_${Date.now()}`
  const newNode = {
    node_id: nodeId,
    node_type: nodeType.type,
    name: `${nodeType.label} ${workflow.nodes.length + 1}`,
    position_x: position.x,
    position_y: position.y,
    status: 'idle',
    config: {}
  }

  workflow.nodes.push(newNode)
  selectedNode.value = newNode
  saveWorkflow(true) // Trigger autosave
}

const addQuickNode = (nodeType) => {
  const position = { x: 100, y: 100 }
  addNode(nodeType, position)
}

const handleNodeConfigure = ({ nodeId }) => {
  // Open configuration modal
}

const handleNodeDuplicate = ({ nodeId }) => {
  const node = workflow.nodes.find(n => n.node_id === nodeId)
  if (node) {
    const newNode = {
      ...node,
      node_id: `node_${Date.now()}`,
      name: `${node.name} (Copy)`,
      position_x: node.position_x + 50,
      position_y: node.position_y + 50
    }
    workflow.nodes.push(newNode)
    selectedNode.value = newNode
    saveWorkflow(true) // Trigger autosave
  }
}

const handleNodeDelete = ({ nodeId }) => {
  const index = workflow.nodes.findIndex(n => n.node_id === nodeId)
  if (index > -1) {
    workflow.nodes.splice(index, 1)
    // Remove related connections
    workflow.connections = workflow.connections.filter(
      c => c.source_node_id !== nodeId && c.target_node_id !== nodeId
    )
    if (selectedNode.value?.node_id === nodeId) {
      selectedNode.value = null
    }
    saveWorkflow(true) // Trigger autosave
  }
}

// Edge handlers
const handleEdgeClick = ({ edgeId }) => {
  selectedConnection.value = workflow.connections.find(c => c.id === edgeId)
  selectedNode.value = null
}

const handleEdgeContextMenu = ({ edgeId }) => {
  // Show edge context menu
}

const handleEdgeLabelEdit = ({ edgeId, label }) => {
  // Edit edge label
}

const handleEdgeRename = ({ edgeId }) => {
  // Rename edge
}

const handleEdgeDelete = ({ edgeId }) => {
  const index = workflow.connections.findIndex(c => c.id === edgeId)
  if (index > -1) {
    workflow.connections.splice(index, 1)
    if (selectedConnection.value?.id === edgeId) {
      selectedConnection.value = null
    }
    saveWorkflow(true) // Trigger autosave
  }
}

// Zoom controls
const zoomIn = () => {
  zoom.value = Math.min(3, zoom.value * 1.2)
}

const zoomOut = () => {
  zoom.value = Math.max(0.1, zoom.value / 1.2)
}

const resetZoom = () => {
  zoom.value = 1
  pan.value = { x: 0, y: 0 }
}

// API functions
const updateNode = async () => {
  if (!selectedNode.value) return

  try {
    // Find the backend node ID by matching node_id
    const existingWorkflow = await workflowsStore.fetchWorkflow(workflow.id)
    const backendNode = existingWorkflow.nodes.find(n => n.node_id === selectedNode.value.node_id)
    
    if (backendNode) {
      await workflowsStore.updateNode(workflow.id, backendNode.id, {
        name: selectedNode.value.name,
        config: selectedNode.value.config
      })
      toast.success('Node updated successfully')
    } else {
      toast.error('Node not found')
    }
  } catch (error) {
    console.error('Update node error:', error)
    toast.error('Failed to update node')
  }
}

// Save workflow with debouncing
let saveTimeout = null
const saveWorkflow = async (isAutosave = false) => {
  if (saveTimeout) {
    clearTimeout(saveTimeout)
  }
  
  if (isAutosave) {
    // Debounce autosave by 800ms
    saveTimeout = setTimeout(() => performSave(), 800)
  } else {
    // Manual save - perform immediately
    await performSave()
  }
}

const validateAllConnections = () => {
  const errors = []
  
  for (const connection of workflow.connections) {
    if (!isValidConnection(
      connection.source_node_id,
      connection.source_port,
      connection.target_node_id,
      connection.target_port
    )) {
      // Provide more specific error messages
      if (connection.source_node_id === connection.target_node_id) {
        errors.push(`Self-loop detected: Node ${connection.source_node_id} cannot connect to itself`)
      } else if (connection.source_port === 'input' || connection.target_port === 'output') {
        errors.push(`Invalid connection direction: Cannot connect ${connection.source_port} to ${connection.target_port}`)
      } else {
        errors.push(`Invalid connection from ${connection.source_node_id} to ${connection.target_node_id}`)
      }
    }
  }
  
  return {
    valid: errors.length === 0,
    errors
  }
}

const performSave = async () => {
  if (saving.value) return
  
  // Validate connections before saving
  const validation = validateAllConnections()
  if (!validation.valid) {
    console.error('Invalid workflow connections. Save aborted.')
    toast.error(`Cannot save workflow: ${validation.errors.join(', ')}`)
    return
  }
  
  saving.value = true
  
  try {
    if (!workflow.id || workflow.id === 'new') {
      // Create new workflow
      const newWorkflow = await workflowsStore.createWorkflow({
        name: workflow.name,
        description: workflow.description
      })
      workflow.id = newWorkflow.id
      router.replace(`/workflows/${newWorkflow.id}`)
      
      // Add nodes and connections to the new workflow
      for (const node of workflow.nodes) {
        await workflowsStore.createNode(workflow.id, {
          node_id: node.node_id,
          node_type: node.node_type,
          name: node.name,
          position_x: node.position_x,
          position_y: node.position_y,
          config: node.config || {}
        })
      }
      
      for (const connection of workflow.connections) {
        await workflowsStore.createConnection(workflow.id, {
          connection_id: connection.id,
          source_node_id: connection.source_node_id,
          target_node_id: connection.target_node_id,
          source_port: connection.source_port,
          target_port: connection.target_port,
          condition: connection.condition
        })
      }
    } else {
      // Update existing workflow
      // Convert to the format expected by the backend
      const nodes = workflow.nodes.map(node => ({
        id: node.node_id,
        type: node.node_type,
        position: { x: node.position_x, y: node.position_y },
        data: {
          name: node.name,
          config: node.config || {}
        }
      }))
      
      const edges = workflow.connections.map(connection => ({
        id: connection.id,
        source: connection.source_node_id,
        target: connection.target_node_id,
        sourceHandle: connection.source_port,
        targetHandle: connection.target_port,
        label: connection.condition ? 'Condition' : undefined
      }))
      
      const bulkData = {
        name: workflow.name,
        description: workflow.description,
        nodes: nodes,
        edges: edges
      }
      
      console.log('Sending bulk update data:', JSON.stringify(bulkData, null, 2))
      
      await workflowsStore.updateWorkflowBulk(workflow.id, bulkData)
    }
    
    toast.success('Workflow saved successfully')
  } catch (error) {
    console.error('Save error:', error)
    toast.error('Failed to save workflow')
  } finally {
    saving.value = false
  }
}

const testWorkflow = async () => {
  try {
    const result = await workflowsStore.testWorkflow(workflow.id, { 
      test_mode: true,
      trigger_data: { test: true }
    })
    
    if (result.success) {
      toast.success('Workflow test completed successfully')
      console.log('Test results:', result)
    } else {
      toast.error(`Workflow test failed: ${result.error}`)
      console.error('Test error:', result)
    }
  } catch (error) {
    toast.error('Failed to test workflow')
    console.error('Test error:', error)
  }
}

const loadWorkflow = async () => {
  if (route.params.id && route.params.id !== 'new') {
    try {
      const workflowData = await workflowsStore.fetchWorkflow(route.params.id)
      
      // Map backend data to frontend format
      workflow.id = workflowData.id
      workflow.name = workflowData.name
      workflow.description = workflowData.description || ''
      
      // Map nodes from backend format to frontend format
      workflow.nodes = workflowData.nodes.map(node => ({
        node_id: node.node_id,
        node_type: node.node_type,
        name: node.name,
        position_x: node.position_x,
        position_y: node.position_y,
        status: node.status || 'idle',
        config: node.config || {}
      }))
      
      // Map connections from backend format to frontend format
      workflow.connections = workflowData.connections.map(connection => ({
        id: connection.connection_id,
        source_node_id: connection.source_node_id,
        target_node_id: connection.target_node_id,
        source_port: connection.source_port,
        target_port: connection.target_port,
        condition: connection.condition,
        is_valid: true // Default to valid
      }))
    } catch (error) {
      console.error('Load error:', error)
      toast.error('Failed to load workflow')
      router.push('/workflows')
    }
  }
}

onMounted(() => {
  loadWorkflow()
})

onUnmounted(() => {
  // Cleanup event listeners
  document.removeEventListener('mousemove', handleConnectionMouseMove)
  document.removeEventListener('mouseup', handleConnectionMouseUp)
})
</script>

<style scoped>
/* Import the workflow design tokens */
@import '@/assets/workflow-tokens.css';

.bg-grid-pattern {
  background-image: 
    linear-gradient(rgba(0,0,0,0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,0,0,0.1) 1px, transparent 1px);
  background-size: 20px 20px;
}

.node-container {
  cursor: grab;
}

.node-container:active {
  cursor: grabbing;
}

/* Connection preview styles */
.workflow-canvas.connecting {
  cursor: crosshair;
}

/* Node selection styles */
.workflow-node.selected {
  box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.3);
}

/* Port handle styles */
.workflow-handle {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: white;
  border: 2px solid #6C5CE7;
  cursor: pointer;
  transition: all 0.2s ease;
}

.workflow-handle:hover {
  transform: scale(1.2);
  box-shadow: 0 0 0 4px rgba(108, 92, 231, 0.2);
}

.workflow-handle.valid-target {
  background: #6C5CE7;
  border-color: #6C5CE7;
  box-shadow: 0 0 0 4px rgba(108, 92, 231, 0.3);
}
</style> 