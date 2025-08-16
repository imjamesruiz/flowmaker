import React, { useCallback, useEffect, useRef } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Connection,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap,
  Panel,
  useReactFlow,
  ReactFlowProvider,
  ConnectionMode,
  OnConnect,
  OnEdgesChange,
  OnNodesChange,
  OnEdgeUpdate,
  ValidConnection,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { useWorkflowStore } from '@/stores/useWorkflowStore'
import { NodeCard } from './NodeCard'
import { useToast } from '@/hooks/useToast'

const nodeTypes = {
  trigger: NodeCard,
  action: NodeCard,
  condition: NodeCard,
  transformer: NodeCard,
  webhook: NodeCard,
}

interface WorkflowCanvasProps {
  workflowId: string
}

export const WorkflowCanvas: React.FC<WorkflowCanvasProps> = ({ workflowId }) => {
  const toast = useToast()
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const {
    nodes,
    edges,
    loading,
    error,
    onNodesChange,
    onEdgesChange,
    onConnect,
    onEdgeUpdate,
    loadWorkflow,
    saveWorkflow,
    testWorkflow,
    addNode,
    deleteNode,
    deleteEdge,
    markDirty,
    clearError,
  } = useWorkflowStore()

  const { project } = useReactFlow()

  // Load workflow on mount
  useEffect(() => {
    loadWorkflow(workflowId)
  }, [workflowId, loadWorkflow])

  // Handle errors
  useEffect(() => {
    if (error) {
      toast.error(error)
      clearError()
    }
  }, [error, toast, clearError])

  // Handle manual save
  const handleSave = useCallback(async () => {
    try {
      await saveWorkflow(false)
      toast.success('Workflow saved successfully')
    } catch (error) {
      toast.error('Failed to save workflow')
    }
  }, [saveWorkflow, toast])

  // Handle test workflow
  const handleTest = useCallback(async () => {
    try {
      const result = await testWorkflow()
      if (result?.success) {
        toast.success('Workflow test completed successfully')
        console.log('Test results:', result)
      } else {
        toast.error(`Workflow test failed: ${result?.error}`)
      }
    } catch (error) {
      toast.error('Failed to test workflow')
    }
  }, [testWorkflow, toast])

  // Handle drag and drop
  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()

      const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect()
      if (!reactFlowBounds) return

      const type = event.dataTransfer.getData('application/reactflow')
      if (!type) return

      const position = project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      })

      addNode(type, position)
    },
    [project, addNode]
  )

  // Handle node deletion
  const onNodeDelete = useCallback((nodeId: string) => {
    deleteNode(nodeId)
  }, [deleteNode])

  // Handle edge deletion
  const onEdgeDelete = useCallback((edgeId: string) => {
    deleteEdge(edgeId)
  }, [deleteEdge])

  // Connection validation
  const isValidConnection: ValidConnection = useCallback(
    ({ source, target, sourceHandle, targetHandle }) => {
      if (!source || !target || source === target) {
        toast.error('Cannot connect a node to itself')
        return false
      }

      // Prevent duplicate identical edge
      const existingEdge = edges.find(
        (e) =>
          e.source === source &&
          e.target === target &&
          e.sourceHandle === sourceHandle &&
          e.targetHandle === targetHandle
      )
      if (existingEdge) {
        toast.error('Connection already exists')
        return false
      }

      // Enforce single input per 'in' handle
      const existingInput = edges.find(
        (e) => e.target === target && e.targetHandle === (targetHandle || 'in')
      )
      if (existingInput) {
        toast.error('Target node already has an input connection')
        return false
      }

      // Validate condition node connections
      const targetNode = nodes.find(n => n.id === target)
      if (targetNode?.type === 'condition') {
        const validHandles = ['in']
        if (targetHandle && !validHandles.includes(targetHandle)) {
          toast.error('Invalid target handle for condition node')
          return false
        }
      }

      // Validate source node connections
      const sourceNode = nodes.find(n => n.id === source)
      if (sourceNode?.type === 'condition') {
        const validHandles = ['true', 'false']
        if (sourceHandle && !validHandles.includes(sourceHandle)) {
          toast.error('Invalid source handle for condition node')
          return false
        }
      }

      return true
    },
    [edges, nodes, toast]
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading workflow...</span>
      </div>
    )
  }

  return (
    <div className="h-full w-full" ref={reactFlowWrapper}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onEdgeUpdate={onEdgeUpdate}
        onDragOver={onDragOver}
        onDrop={onDrop}
        nodeTypes={nodeTypes}
        connectionMode={ConnectionMode.Loose}
        isValidConnection={isValidConnection}
        fitView
        attributionPosition="bottom-left"
        defaultEdgeOptions={{
          type: 'smoothstep',
          animated: false,
          style: { stroke: '#6C5CE7', strokeWidth: 2 }
        }}
      >
        <Controls />
        <Background />
        <MiniMap />
        
        <Panel position="top-left" className="bg-white p-4 rounded-lg shadow-lg">
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Save
            </button>
            <button
              onClick={handleTest}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
            >
              Test
            </button>
          </div>
        </Panel>

        <Panel position="top-right" className="bg-white p-4 rounded-lg shadow-lg">
          <div className="text-sm text-gray-600">
            Drag nodes from the palette to create connections
          </div>
        </Panel>
      </ReactFlow>
    </div>
  )
}

// Wrapper component with ReactFlowProvider
export const WorkflowCanvasWrapper: React.FC<WorkflowCanvasProps> = (props) => {
  return (
    <ReactFlowProvider>
      <WorkflowCanvas {...props} />
    </ReactFlowProvider>
  )
}
