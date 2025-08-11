<template>
  <div class="h-screen flex flex-col">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <router-link
            to="/workflows"
            class="text-gray-400 hover:text-gray-600"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
            </svg>
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
          <button
            @click="testWorkflow"
            :disabled="!workflow.nodes.length"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Test
          </button>
          <button
            @click="saveWorkflow"
            :disabled="saving"
            class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
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
              class="flex items-center p-2 border border-gray-200 rounded cursor-move hover:bg-gray-50"
              draggable="true"
              @dragstart="handleDragStart($event, nodeType)"
            >
              <div class="w-4 h-4 rounded mr-2" :class="nodeType.color"></div>
              <span class="text-sm text-gray-700">{{ nodeType.label }}</span>
            </div>
          </div>
        </div>

        <!-- Properties Panel -->
        <div class="flex-1 p-4">
          <h3 class="text-sm font-medium text-gray-900 mb-3">Properties</h3>
          <div v-if="selectedNode" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Name</label>
              <input
                v-model="selectedNode.name"
                type="text"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                @blur="updateNode"
              />
            </div>
            
            <div v-if="selectedNode.node_type === 'trigger'">
              <label class="block text-sm font-medium text-gray-700">Trigger Type</label>
              <select
                v-model="selectedNode.config.trigger_type"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                @change="updateNode"
              >
                <option value="webhook">Webhook</option>
                <option value="schedule">Schedule</option>
                <option value="gmail_new_email">Gmail - New Email</option>
                <option value="slack_message">Slack - New Message</option>
              </select>
            </div>
            
            <div v-if="selectedNode.node_type === 'action'">
              <label class="block text-sm font-medium text-gray-700">Action Type</label>
              <select
                v-model="selectedNode.config.action_type"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                @change="updateNode"
              >
                <option value="gmail_send_email">Gmail - Send Email</option>
                <option value="slack_send_message">Slack - Send Message</option>
                <option value="sheets_update">Google Sheets - Update</option>
                <option value="http_request">HTTP Request</option>
              </select>
            </div>
            
            <div v-if="selectedNode.node_type === 'condition'">
              <label class="block text-sm font-medium text-gray-700">Condition Type</label>
              <select
                v-model="selectedNode.config.condition_type"
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                @change="updateNode"
              >
                <option value="simple">Simple</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
          </div>
          <div v-else class="text-sm text-gray-500">
            Select a node to edit its properties
          </div>
        </div>
      </div>

      <!-- Canvas -->
      <div class="flex-1 relative">
        <div
          ref="canvasContainer"
          class="w-full h-full bg-gray-50"
        ></div>
        
        <!-- Canvas Toolbar -->
        <div class="absolute top-4 left-4 flex space-x-2">
          <button
            @click="zoomIn"
            class="p-2 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50"
            title="Zoom In"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"></path>
            </svg>
          </button>
          <button
            @click="zoomOut"
            class="p-2 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50"
            title="Zoom Out"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"></path>
            </svg>
          </button>
          <button
            @click="fitToContent"
            class="p-2 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50"
            title="Fit to Content"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useWorkflowsStore } from '@/stores/workflows'
import { useToast } from 'vue-toastification'
import * as joint from 'jointjs'

const route = useRoute()
const router = useRouter()
const workflowsStore = useWorkflowsStore()
const toast = useToast()

const canvasContainer = ref(null)
const graph = ref(null)
const paper = ref(null)
const selectedNode = ref(null)
const saving = ref(false)

const workflow = reactive({
  id: null,
  name: 'Untitled Workflow',
  description: '',
  nodes: [],
  connections: []
})

const nodeTypes = [
  { type: 'trigger', label: 'Trigger', color: 'bg-green-500' },
  { type: 'action', label: 'Action', color: 'bg-blue-500' },
  { type: 'condition', label: 'Condition', color: 'bg-yellow-500' },
  { type: 'transformer', label: 'Transformer', color: 'bg-purple-500' },
  { type: 'webhook', label: 'Webhook', color: 'bg-red-500' }
]

const handleDragStart = (event, nodeType) => {
  event.dataTransfer.setData('application/json', JSON.stringify(nodeType))
}

const initializeCanvas = () => {
  if (!canvasContainer.value) return

  // Create graph
  graph.value = new joint.dia.Graph()

  // Create paper
  paper.value = new joint.dia.Paper({
    el: canvasContainer.value,
    model: graph.value,
    width: '100%',
    height: '100%',
    gridSize: 10,
    drawGrid: true,
    background: {
      color: '#f9fafb'
    },
    interactive: {
      vertexAdd: false,
      vertexMove: true,
      vertexRemove: false,
      arrowheadMove: false,
      labelMove: false
    }
  })

  // Handle node selection
  paper.value.on('cell:pointerclick', (cellView) => {
    if (cellView.model.isElement()) {
      selectedNode.value = workflow.nodes.find(n => n.node_id === cellView.model.id)
    }
  })

  // Handle canvas click to deselect
  paper.value.on('blank:pointerclick', () => {
    selectedNode.value = null
  })

  // Handle node drops
  canvasContainer.value.addEventListener('dragover', (e) => {
    e.preventDefault()
  })

  canvasContainer.value.addEventListener('drop', (e) => {
    e.preventDefault()
    const nodeType = JSON.parse(e.dataTransfer.getData('application/json'))
    const position = paper.value.clientToLocalPoint(e.clientX, e.clientY)
    addNode(nodeType, position)
  })
}

const addNode = (nodeType, position) => {
  const nodeId = `node_${Date.now()}`
  const nodeData = {
    node_id: nodeId,
    node_type: nodeType.type,
    name: `${nodeType.label} ${workflow.nodes.length + 1}`,
    position_x: position.x,
    position_y: position.y,
    config: {}
  }

  // Create Joint.js element
  const element = new joint.shapes.standard.Rectangle({
    id: nodeId,
    position: { x: position.x, y: position.y },
    size: { width: 120, height: 60 },
    attrs: {
      body: {
        fill: nodeType.color.replace('bg-', '').replace('-500', ''),
        stroke: '#374151',
        strokeWidth: 2
      },
      label: {
        text: nodeData.name,
        fill: 'white',
        fontSize: 12,
        fontWeight: 'bold'
      }
    },
    ports: {
      groups: {
        in: {
          position: 'left',
          attrs: {
            circle: {
              r: 4,
              magnet: true,
              stroke: '#5f6368',
              strokeWidth: 1,
              fill: '#fff'
            }
          }
        },
        out: {
          position: 'right',
          attrs: {
            circle: {
              r: 4,
              magnet: true,
              stroke: '#5f6368',
              strokeWidth: 1,
              fill: '#fff'
            }
          }
        }
      },
      items: [
        { group: 'in', id: 'in' },
        { group: 'out', id: 'out' }
      ]
    }
  })

  graph.value.addCell(element)
  workflow.nodes.push(nodeData)
}

const updateNode = async () => {
  if (!selectedNode.value) return

  try {
    await workflowsStore.updateNode(workflow.id, selectedNode.value.id, {
      name: selectedNode.value.name,
      config: selectedNode.value.config
    })

    // Update Joint.js element
    const element = graph.value.getCell(selectedNode.value.node_id)
    if (element) {
      element.attr('label/text', selectedNode.value.name)
    }

    toast.success('Node updated successfully')
  } catch (error) {
    toast.error('Failed to update node')
  }
}

const saveWorkflow = async () => {
  saving.value = true
  
  try {
    if (workflow.id) {
      await workflowsStore.updateWorkflow(workflow.id, {
        name: workflow.name,
        description: workflow.description
      })
    } else {
      const newWorkflow = await workflowsStore.createWorkflow({
        name: workflow.name,
        description: workflow.description
      })
      workflow.id = newWorkflow.id
      router.replace(`/workflows/${newWorkflow.id}`)
    }
    
    toast.success('Workflow saved successfully')
  } catch (error) {
    toast.error('Failed to save workflow')
  } finally {
    saving.value = false
  }
}

const testWorkflow = async () => {
  try {
    await workflowsStore.executeWorkflow(workflow.id, { test_mode: true })
    toast.success('Workflow test started')
  } catch (error) {
    toast.error('Failed to test workflow')
  }
}

const zoomIn = () => {
  const zoom = paper.value.scale().sx
  paper.value.scale(zoom * 1.2, zoom * 1.2)
}

const zoomOut = () => {
  const zoom = paper.value.scale().sx
  paper.value.scale(zoom / 1.2, zoom / 1.2)
}

const fitToContent = () => {
  paper.value.fitToContent()
}

const loadWorkflow = async () => {
  if (route.params.id && route.params.id !== 'new') {
    try {
      const workflowData = await workflowsStore.fetchWorkflow(route.params.id)
      Object.assign(workflow, workflowData)
      
      // Load nodes and connections into canvas
      nextTick(() => {
        workflow.nodes.forEach(node => {
          const nodeType = nodeTypes.find(nt => nt.type === node.node_type)
          if (nodeType) {
            addNode(nodeType, { x: node.position_x, y: node.position_y })
          }
        })
      })
    } catch (error) {
      toast.error('Failed to load workflow')
      router.push('/workflows')
    }
  }
}

onMounted(() => {
  initializeCanvas()
  loadWorkflow()
})

onUnmounted(() => {
  if (paper.value) {
    paper.value.remove()
  }
})
</script> 