import { create } from 'zustand'
import { Node, Edge, Connection, addEdge, applyNodeChanges, applyEdgeChanges, NodeChange, EdgeChange } from 'reactflow'
import { Workflow, WFNode, WFEdge, ExecutionResult } from '@/types/workflow'
import { workflowAPI } from '@/services/api'

interface WorkflowState {
  // React Flow state
  nodes: Node[]
  edges: Edge[]
  selectedNode: Node | null
  selectedEdge: Edge | null
  
  // Workflow state
  workflow: Workflow | null
  isDirty: boolean
  loading: boolean
  error: string | null
  
  // Actions
  setNodes: (nodes: Node[]) => void
  setEdges: (edges: Edge[]) => void
  onNodesChange: (changes: NodeChange[]) => void
  onEdgesChange: (changes: EdgeChange[]) => void
  onConnect: (connection: Connection) => void
  onEdgeUpdate: (oldEdge: Edge, newConnection: Connection) => void
  
  // Workflow actions
  loadWorkflow: (id: string) => Promise<void>
  saveWorkflow: (isAutosave?: boolean) => Promise<void>
  testWorkflow: () => Promise<ExecutionResult | null>
  
  // Utility actions
  addNode: (type: string, position: { x: number; y: number }) => void
  deleteNode: (nodeId: string) => void
  deleteEdge: (edgeId: string) => void
  markDirty: () => void
  clearError: () => void
}

// Debounced save function
let saveTimeout: NodeJS.Timeout | null = null

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  // Initial state
  nodes: [],
  edges: [],
  selectedNode: null,
  selectedEdge: null,
  workflow: null,
  isDirty: false,
  loading: false,
  error: null,

  // React Flow callbacks
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),

  onNodesChange: (changes) => {
    set((state) => ({
      nodes: applyNodeChanges(changes, state.nodes),
      isDirty: true
    }))
    
    // Trigger autosave
    const { saveWorkflow } = get()
    saveWorkflow(true)
  },

  onEdgesChange: (changes) => {
    set((state) => ({
      edges: applyEdgeChanges(changes, state.edges),
      isDirty: true
    }))
    
    // Trigger autosave
    const { saveWorkflow } = get()
    saveWorkflow(true)
  },

  onConnect: (connection) => {
    if (!connection.source || !connection.target) return

    // Generate deterministic edge ID
    const edgeId = `e_${connection.source}-${connection.sourceHandle || 'out'}_${connection.target}-${connection.targetHandle || 'in'}`
    
    const newEdge: Edge = {
      id: edgeId,
      source: connection.source,
      sourceHandle: connection.sourceHandle || 'out',
      target: connection.target,
      targetHandle: connection.targetHandle || 'in',
      type: 'smoothstep',
      animated: false,
      style: { stroke: '#6C5CE7', strokeWidth: 2 }
    }

    // Validate connection
    if (!isValidConnection(connection, get().edges)) {
      return
    }

    set((state) => ({
      edges: addEdge(newEdge, state.edges),
      isDirty: true
    }))

    // Trigger autosave
    const { saveWorkflow } = get()
    saveWorkflow(true)
  },

  onEdgeUpdate: (oldEdge, newConnection) => {
    if (!newConnection.source || !newConnection.target) return

    set((state) => ({
      edges: state.edges.map((edge) =>
        edge.id === oldEdge.id
          ? {
              ...edge,
              source: newConnection.source!,
              sourceHandle: newConnection.sourceHandle,
              target: newConnection.target!,
              targetHandle: newConnection.targetHandle,
            }
          : edge
      ),
      isDirty: true
    }))

    // Trigger autosave
    const { saveWorkflow } = get()
    saveWorkflow(true)
  },

  // Workflow actions
  loadWorkflow: async (id: string) => {
    set({ loading: true, error: null })
    
    try {
      const response = await workflowAPI.getWorkflow(id)
      const workflow = response.data
      
      // Convert to React Flow format
      const nodes: Node[] = workflow.nodes.map((node: WFNode) => ({
        id: node.id,
        type: node.type,
        position: node.position,
        data: node.data,
        style: getNodeStyle(node.type)
      }))

      const edges: Edge[] = workflow.edges.map((edge: WFEdge) => ({
        id: edge.id,
        source: edge.source,
        sourceHandle: edge.sourceHandle || 'out',
        target: edge.target,
        targetHandle: edge.targetHandle || 'in',
        type: 'smoothstep',
        animated: false,
        style: { stroke: '#6C5CE7', strokeWidth: 2 },
        label: edge.label
      }))

      set({
        workflow,
        nodes,
        edges,
        isDirty: false,
        loading: false
      })
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to load workflow',
        loading: false 
      })
    }
  },

  saveWorkflow: async (isAutosave = false) => {
    const { workflow, nodes, edges, isDirty } = get()
    
    if (!workflow || !isDirty) return

    if (isAutosave) {
      // Debounce autosave
      if (saveTimeout) {
        clearTimeout(saveTimeout)
      }
      saveTimeout = setTimeout(() => get().saveWorkflow(false), 800)
      return
    }

    set({ loading: true, error: null })

    try {
      // Convert React Flow format to API format
      const workflowData = {
        id: workflow.id,
        name: workflow.name,
        nodes: nodes.map(node => ({
          id: node.id,
          type: node.type,
          position: node.position,
          data: node.data
        })),
        edges: edges.map(edge => ({
          id: edge.id,
          source: edge.source,
          sourceHandle: edge.sourceHandle,
          target: edge.target,
          targetHandle: edge.targetHandle,
          label: edge.label
        }))
      }

      await workflowAPI.saveWorkflow(workflow.id, workflowData)
      
      set({ isDirty: false, loading: false })
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to save workflow',
        loading: false 
      })
    }
  },

  testWorkflow: async () => {
    const { workflow, nodes, edges } = get()
    
    if (!workflow) return null

    set({ loading: true, error: null })

    try {
      // Convert React Flow format to API format
      const workflowData = {
        nodes: nodes.map(node => ({
          id: node.id,
          type: node.type,
          position: node.position,
          data: node.data
        })),
        edges: edges.map(edge => ({
          id: edge.id,
          source: edge.source,
          sourceHandle: edge.sourceHandle,
          target: edge.target,
          targetHandle: edge.targetHandle,
          label: edge.label
        }))
      }

      const response = await workflowAPI.testWorkflow(workflow.id, {
        test_mode: true,
        trigger_data: { test: true }
      })

      set({ loading: false })
      return response.data
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to test workflow',
        loading: false 
      })
      return null
    }
  },

  // Utility actions
  addNode: (type, position) => {
    const nodeId = `node_${Date.now()}`
    const newNode: Node = {
      id: nodeId,
      type,
      position,
      data: { 
        name: `${type.charAt(0).toUpperCase() + type.slice(1)} ${get().nodes.length + 1}`,
        config: {}
      },
      style: getNodeStyle(type)
    }

    set((state) => ({
      nodes: [...state.nodes, newNode],
      isDirty: true
    }))

    // Trigger autosave
    const { saveWorkflow } = get()
    saveWorkflow(true)
  },

  deleteNode: (nodeId) => {
    set((state) => ({
      nodes: state.nodes.filter(node => node.id !== nodeId),
      edges: state.edges.filter(edge => 
        edge.source !== nodeId && edge.target !== nodeId
      ),
      isDirty: true
    }))

    // Trigger autosave
    const { saveWorkflow } = get()
    saveWorkflow(true)
  },

  deleteEdge: (edgeId) => {
    set((state) => ({
      edges: state.edges.filter(edge => edge.id !== edgeId),
      isDirty: true
    }))

    // Trigger autosave
    const { saveWorkflow } = get()
    saveWorkflow(true)
  },

  markDirty: () => set({ isDirty: true }),
  clearError: () => set({ error: null })
}))

// Helper functions
function isValidConnection(connection: Connection, edges: Edge[]): boolean {
  if (!connection.source || !connection.target || connection.source === connection.target) {
    return false
  }

  // 1. Prevent duplicate identical edge
  if (edges.some(e => 
    e.source === connection.source && 
    e.target === connection.target && 
    e.sourceHandle === connection.sourceHandle && 
    e.targetHandle === connection.targetHandle
  )) {
    return false
  }

  // 2. Enforce single input per 'in' handle
  if (edges.some(e => 
    e.target === connection.target && 
    e.targetHandle === (connection.targetHandle || 'in')
  )) {
    return false
  }

  return true
}

function getNodeStyle(type: string) {
  const colorMap: Record<string, string> = {
    trigger: '#10B981',
    action: '#3B82F6',
    condition: '#F59E0B',
    transformer: '#8B5CF6',
    webhook: '#EF4444'
  }

  return {
    border: `2px solid ${colorMap[type] || '#6B7280'}`,
    borderRadius: '8px',
    padding: '12px',
    background: 'white'
  }
}
