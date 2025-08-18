import { create } from 'zustand'
import { nanoid } from 'nanoid'
import { Workflow, NodeModel, EdgeModel } from '@/types/graph'
import { validateGraph, isValidConnection, Connection } from '@/utils/validation'

interface WorkflowState {
  // Core state
  workflow: Workflow
  selectedId?: string
  issues: Record<string, string[]>
  
  // Undo/Redo state
  history: Workflow[]
  historyIndex: number
  maxHistorySize: number
  
  // Actions
  addNode: (type: string, position: { x: number; y: number }) => void
  updateNode: (id: string, patch: Partial<NodeModel>) => void
  removeNode: (id: string) => void
  addEdge: (edge: EdgeModel) => void
  removeEdge: (id: string) => void
  edgeExists: (conn: Connection) => boolean
  
  // Validation and serialization
  validateGraph: () => void
  serialize: () => string
  load: (workflow: Workflow) => void
  
  // Undo/Redo
  undo: () => void
  redo: () => void
  
  // Selection
  setSelectedId: (id?: string) => void
  
  // Private helpers
  _addToHistory: () => void
  _canUndo: () => boolean
  _canRedo: () => boolean
}

// Create a seeded workflow with one trigger and one action
const createSeededWorkflow = (): Workflow => ({
  id: nanoid(),
  nodes: [
    {
      id: 'trigger-1',
      type: 'trigger',
      label: 'Trigger 1',
      ports: {
        in: [],
        out: [
          { id: 'out', dtype: 'event', required: false }
        ]
      },
      params: { name: 'Webhook Trigger' }
    },
    {
      id: 'action-1',
      type: 'action',
      label: 'Action 1',
      ports: {
        in: [
          { id: 'in', dtype: 'event', required: true }
        ],
        out: [
          { id: 'out', dtype: 'json', required: false }
        ]
      },
      params: { name: 'Send Email' }
    }
  ],
  edges: []
})

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  // Initial state
  workflow: createSeededWorkflow(),
  selectedId: undefined,
  issues: {},
  history: [createSeededWorkflow()],
  historyIndex: 0,
  maxHistorySize: 20,

  // Node actions
  addNode: (type, position) => {
    const { workflow } = get()
    const newNode: NodeModel = {
      id: nanoid(),
      type,
      label: `${type.charAt(0).toUpperCase() + type.slice(1)} ${workflow.nodes.length + 1}`,
      ports: getDefaultPorts(type),
      params: getDefaultParams(type)
    }

    set(state => ({
      workflow: {
        ...state.workflow,
        nodes: [...state.workflow.nodes, newNode]
      }
    }))

    get()._addToHistory()
    get().validateGraph()
  },

  updateNode: (id, patch) => {
    set(state => ({
      workflow: {
        ...state.workflow,
        nodes: state.workflow.nodes.map(node =>
          node.id === id ? { ...node, ...patch } : node
        )
      }
    }))

    get()._addToHistory()
    get().validateGraph()
  },

  removeNode: (id) => {
    set(state => ({
      workflow: {
        ...state.workflow,
        nodes: state.workflow.nodes.filter(node => node.id !== id),
        edges: state.workflow.edges.filter(
          edge => edge.from.node !== id && edge.to.node !== id
        )
      }
    }))

    get()._addToHistory()
    get().validateGraph()
  },

  // Edge actions
  addEdge: (edge) => {
    const { workflow } = get()
    
    // Validate the connection
    const conn: Connection = {
      source: edge.from.node,
      sourceHandle: edge.from.port,
      target: edge.to.node,
      targetHandle: edge.to.port
    }

    if (!isValidConnection(conn, workflow)) {
      return false
    }

    set(state => ({
      workflow: {
        ...state.workflow,
        edges: [...state.workflow.edges, edge]
      }
    }))

    get()._addToHistory()
    get().validateGraph()
    return true
  },

  removeEdge: (id) => {
    set(state => ({
      workflow: {
        ...state.workflow,
        edges: state.workflow.edges.filter(edge => edge.id !== id)
      }
    }))

    get()._addToHistory()
    get().validateGraph()
  },

  edgeExists: (conn) => {
    const { workflow } = get()
    return workflow.edges.some(
      edge => 
        edge.from.node === conn.source &&
        edge.from.port === conn.sourceHandle &&
        edge.to.node === conn.target &&
        edge.to.port === conn.targetHandle
    )
  },

  // Validation and serialization
  validateGraph: () => {
    const { workflow } = get()
    const issues = validateGraph(workflow)
    set({ issues })
  },

  serialize: () => {
    const { workflow } = get()
    return JSON.stringify(workflow, null, 2)
  },

  load: (workflow) => {
    set({
      workflow,
      issues: {},
      history: [workflow],
      historyIndex: 0
    })
    get().validateGraph()
  },

  // Undo/Redo
  undo: () => {
    const { history, historyIndex, maxHistorySize } = get()
    
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1
      const newWorkflow = history[newIndex]
      
      set({
        workflow: newWorkflow,
        historyIndex: newIndex,
        issues: {}
      })
      
      get().validateGraph()
    }
  },

  redo: () => {
    const { history, historyIndex } = get()
    
    if (historyIndex < history.length - 1) {
      const newIndex = historyIndex + 1
      const newWorkflow = history[newIndex]
      
      set({
        workflow: newWorkflow,
        historyIndex: newIndex,
        issues: {}
      })
      
      get().validateGraph()
    }
  },

  // Selection
  setSelectedId: (id) => {
    set({ selectedId: id })
  },

  // Private helpers
  _addToHistory: () => {
    const { workflow, history, historyIndex, maxHistorySize } = get()
    
    // Remove any future history if we're not at the end
    const newHistory = history.slice(0, historyIndex + 1)
    
    // Add current state
    newHistory.push(workflow)
    
    // Limit history size
    if (newHistory.length > maxHistorySize) {
      newHistory.shift()
    }
    
    set({
      history: newHistory,
      historyIndex: newHistory.length - 1
    })
  },

  _canUndo: () => {
    const { historyIndex } = get()
    return historyIndex > 0
  },

  _canRedo: () => {
    const { history, historyIndex } = get()
    return historyIndex < history.length - 1
  }
}))

// Helper functions for default ports and params
function getDefaultPorts(type: string) {
  const portSchemas: Record<string, { in: any[], out: any[] }> = {
    trigger: {
      in: [],
      out: [{ id: 'out', dtype: 'event', required: false }]
    },
    action: {
      in: [{ id: 'in', dtype: 'any', required: true }],
      out: [{ id: 'out', dtype: 'json', required: false }]
    },
    condition: {
      in: [{ id: 'in', dtype: 'any', required: true }],
      out: [
        { id: 'true', dtype: 'any', required: false },
        { id: 'false', dtype: 'any', required: false }
      ]
    },
    transformer: {
      in: [{ id: 'in', dtype: 'any', required: true }],
      out: [{ id: 'out', dtype: 'json', required: false }]
    },
    webhook: {
      in: [{ id: 'in', dtype: 'any', required: true }],
      out: [{ id: 'out', dtype: 'json', required: false }]
    }
  }
  
  return portSchemas[type] || { in: [], out: [] }
}

function getDefaultParams(type: string) {
  const paramSchemas: Record<string, Record<string, any>> = {
    trigger: { name: 'New Trigger' },
    action: { name: 'New Action' },
    condition: { condition: 'true' },
    transformer: { transformation: 'x => x' },
    webhook: { url: 'https://example.com/webhook' }
  }
  
  return paramSchemas[type] || {}
}
