import { Workflow } from '@/types/graph'
import { validateGraph } from '@/utils/validation'

// Mock API endpoints for workflow operations
const STORAGE_KEY = 'flowmaker_workflows'

// Helper to get workflows from localStorage
function getWorkflowsFromStorage(): Record<string, Workflow> {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : {}
  } catch {
    return {}
  }
}

// Helper to save workflows to localStorage
function saveWorkflowsToStorage(workflows: Record<string, Workflow>): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(workflows))
  } catch (error) {
    console.error('Failed to save workflows to localStorage:', error)
  }
}

// Mock API functions
export const workflowAPI = {
  // GET /api/workflows/:id
  getWorkflow: async (id: string): Promise<{ data: Workflow }> => {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 100))
    
    const workflows = getWorkflowsFromStorage()
    const workflow = workflows[id]
    
    if (!workflow) {
      throw new Error(`Workflow with id ${id} not found`)
    }
    
    return { data: workflow }
  },

  // POST /api/workflows/:id
  saveWorkflow: async (id: string, workflow: Workflow): Promise<{ data: Workflow }> => {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 200))
    
    const workflows = getWorkflowsFromStorage()
    workflows[id] = workflow
    saveWorkflowsToStorage(workflows)
    
    return { data: workflow }
  },

  // POST /api/workflows/:id/validate
  validateWorkflow: async (id: string): Promise<{ data: { issues: Record<string, string[]> } }> => {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 150))
    
    const workflows = getWorkflowsFromStorage()
    const workflow = workflows[id]
    
    if (!workflow) {
      throw new Error(`Workflow with id ${id} not found`)
    }
    
    const issues = validateGraph(workflow)
    
    return { data: { issues } }
  },

  // POST /api/workflows/:id/simulate
  simulateWorkflow: async (id: string): Promise<{ data: { trace: any[] } }> => {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const workflows = getWorkflowsFromStorage()
    const workflow = workflows[id]
    
    if (!workflow) {
      throw new Error(`Workflow with id ${id} not found`)
    }
    
    // Generate a mock execution trace
    const trace = generateMockTrace(workflow)
    
    return { data: { trace } }
  }
}

// Helper to generate mock execution trace
function generateMockTrace(workflow: Workflow): any[] {
  const trace = []
  const startTime = new Date()
  
  // Find trigger nodes (nodes with no input ports)
  const triggerNodes = workflow.nodes.filter(node => node.ports.in.length === 0)
  
  for (const trigger of triggerNodes) {
    trace.push({
      node_id: trigger.id,
      node_type: trigger.type,
      node_name: trigger.label,
      status: 'success',
      start_time: startTime.toISOString(),
      execution_time: Math.random() * 100 + 50, // 50-150ms
      input: { event: 'webhook_triggered', data: { test: true } },
      output: { event_id: 'evt_123', timestamp: startTime.toISOString() },
      context_patch: { trigger_data: { event_id: 'evt_123' } }
    })
    
    // Find connected nodes and simulate their execution
    const connectedEdges = workflow.edges.filter(edge => edge.from.node === trigger.id)
    
    for (const edge of connectedEdges) {
      const targetNode = workflow.nodes.find(n => n.id === edge.to.node)
      if (targetNode) {
        const nodeStartTime = new Date(startTime.getTime() + 100)
        
        trace.push({
          node_id: targetNode.id,
          node_type: targetNode.type,
          node_name: targetNode.label,
          status: 'success',
          start_time: nodeStartTime.toISOString(),
          execution_time: Math.random() * 200 + 100, // 100-300ms
          input: { event_id: 'evt_123', data: { processed: true } },
          output: { result: 'success', message: 'Action completed successfully' },
          context_patch: { action_result: { success: true } }
        })
      }
    }
  }
  
  return trace
}

// Export for use in components
export default workflowAPI
