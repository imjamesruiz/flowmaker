import { EdgeModel, NodeModel, Workflow, DType } from '@/types/graph'

export interface Connection {
  source: string
  sourceHandle: string
  target: string
  targetHandle: string
}

export interface ValidationIssues {
  [nodeId: string]: string[]
}

export function isValidConnection(
  conn: Connection,
  workflow: Workflow
): boolean {
  const { source, sourceHandle, target, targetHandle } = conn

  // No self-loops
  if (source === target) {
    return false
  }

  // Find source and target nodes
  const sourceNode = workflow.nodes.find(n => n.id === source)
  const targetNode = workflow.nodes.find(n => n.id === target)

  if (!sourceNode || !targetNode) {
    return false
  }

  // Find source and target ports
  const sourcePort = sourceNode.ports.out.find(p => p.id === sourceHandle)
  const targetPort = targetNode.ports.in.find(p => p.id === targetHandle)

  if (!sourcePort || !targetPort) {
    return false
  }

  // Check for duplicate edges
  const existingEdge = workflow.edges.find(
    e => e.from.node === source && 
         e.from.port === sourceHandle && 
         e.to.node === target && 
         e.to.port === targetHandle
  )

  if (existingEdge) {
    return false
  }

  // Check input port capacity (if multi !== true then max 1)
  if (!targetPort.multi) {
    const existingInputs = workflow.edges.filter(
      e => e.to.node === target && e.to.port === targetHandle
    )
    if (existingInputs.length >= 1) {
      return false
    }
  }

  // Check dtype match (src.dtype === dst.dtype || dst.dtype === 'any')
  if (sourcePort.dtype !== targetPort.dtype && targetPort.dtype !== 'any') {
    return false
  }

  return true
}

export function validateGraph(workflow: Workflow): ValidationIssues {
  const issues: ValidationIssues = {}

  // Initialize issues object for all nodes
  workflow.nodes.forEach(node => {
    issues[node.id] = []
  })

  // Check for missing required inputs
  workflow.nodes.forEach(node => {
    node.ports.in.forEach(port => {
      if (port.required) {
        const hasInput = workflow.edges.some(
          edge => edge.to.node === node.id && edge.to.port === port.id
        )
        if (!hasInput) {
          issues[node.id].push(`Missing required input: ${port.id}`)
        }
      }
    })
  })

  // Check for type mismatches
  workflow.edges.forEach(edge => {
    const sourceNode = workflow.nodes.find(n => n.id === edge.from.node)
    const targetNode = workflow.nodes.find(n => n.id === edge.to.node)

    if (sourceNode && targetNode) {
      const sourcePort = sourceNode.ports.out.find(p => p.id === edge.from.port)
      const targetPort = targetNode.ports.in.find(p => p.id === edge.to.port)

      if (sourcePort && targetPort) {
        if (sourcePort.dtype !== targetPort.dtype && targetPort.dtype !== 'any') {
          issues[targetNode.id].push(
            `Type mismatch: ${sourcePort.dtype} → ${targetPort.dtype} on port ${targetPort.id}`
          )
        }
      }
    }
  })

  // Check for unconfigured required params
  workflow.nodes.forEach(node => {
    if (node.params) {
      // This is a simplified check - in a real implementation you'd have
      // a schema for each node type defining required params
      const requiredParams = getRequiredParamsForNodeType(node.type)
      requiredParams.forEach(param => {
        if (!node.params || !node.params[param]) {
          issues[node.id].push(`Missing required parameter: ${param}`)
        }
      })
    }
  })

  return issues
}

// Helper function to get required params for a node type
function getRequiredParamsForNodeType(nodeType: string): string[] {
  // This would be defined based on your node type schemas
  const paramSchemas: Record<string, string[]> = {
    trigger: ['name'],
    action: ['name'],
    condition: ['condition'],
    transformer: ['transformation'],
    webhook: ['url']
  }
  
  return paramSchemas[nodeType] || []
}

export function getCompatiblePorts(
  sourcePort: { dtype: DType },
  workflow: Workflow
): { nodeId: string; portId: string }[] {
  const compatible: { nodeId: string; portId: string }[] = []

  workflow.nodes.forEach(node => {
    node.ports.in.forEach(port => {
      if (port.dtype === sourcePort.dtype || port.dtype === 'any') {
        compatible.push({ nodeId: node.id, portId: port.id })
      }
    })
  })

  return compatible
}
