import React, { useCallback, useEffect, useRef, useState } from 'react'
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
  NodeTypes,
  EdgeTypes,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { useWorkflowStore } from '@/store/workflowStore'
import { workflowAPI } from '@/mocks/workflows'
import { isValidConnection } from '@/utils/validation'
import { EdgeModel } from '@/types/graph'
import WorkflowNode from './WorkflowNode'
import TriggerActionManager from './TriggerActionManager.vue'
import { nanoid } from 'nanoid'

// Node types
const nodeTypes: NodeTypes = {
  workflowNode: WorkflowNode,
}

interface WorkflowCanvasProps {
  workflowId: string
}

export const WorkflowCanvas: React.FC<WorkflowCanvasProps> = ({ workflowId }) => {
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const [simulationPanel, setSimulationPanel] = useState(false)
  const [simulationTrace, setSimulationTrace] = useState<any[]>([])
  const [isSimulating, setIsSimulating] = useState(false)
  
  const {
    workflow,
    issues,
    selectedId,
    addNode,
    updateNode,
    removeNode,
    addEdge,
    removeEdge,
    edgeExists,
    validateGraph,
    serialize,
    load,
    undo,
    redo,
    setSelectedId,
  } = useWorkflowStore()

  const { project } = useReactFlow()

  // Convert workflow to React Flow format
  const nodes: Node[] = workflow.nodes.map((node) => ({
    id: node.id,
    type: 'workflowNode',
    position: { x: 0, y: 0 }, // Position will be set by React Flow
    data: {
      node,
      issues: issues[node.id] || [],
      isSelected: selectedId === node.id,
    },
  }))

  const edges: Edge[] = workflow.edges.map((edge) => ({
    id: edge.id,
    source: edge.from.node,
    sourceHandle: edge.from.port,
    target: edge.to.node,
    targetHandle: edge.to.port,
    type: 'smoothstep',
    animated: false,
    style: { stroke: '#6C5CE7', strokeWidth: 2 },
  }))

  const [reactFlowNodes, setReactFlowNodes, onNodesChange] = useNodesState(nodes)
  const [reactFlowEdges, setReactFlowEdges, onEdgesChange] = useEdgesState(edges)

  // Sync React Flow state with our store
  useEffect(() => {
    setReactFlowNodes(nodes)
  }, [nodes, setReactFlowNodes])

  useEffect(() => {
    setReactFlowEdges(edges)
  }, [edges, setReactFlowEdges])

  // Load workflow on mount
  useEffect(() => {
    const loadWorkflow = async () => {
      try {
        const response = await workflowAPI.getWorkflow(workflowId)
        load(response.data)
      } catch (error) {
        console.error('Failed to load workflow:', error)
        // Use default seeded workflow if loading fails
      }
    }
    loadWorkflow()
  }, [workflowId, load])

  // Handle connection
  const onConnect: OnConnect = useCallback(
    (connection) => {
      if (!connection.source || !connection.target) return

      const edge: EdgeModel = {
        id: nanoid(),
        from: {
          node: connection.source,
          port: connection.sourceHandle || 'out',
        },
        to: {
          node: connection.target,
          port: connection.targetHandle || 'in',
        },
      }

      const success = addEdge(edge)
      if (!success) {
        // Show error toast or tooltip
        console.warn('Invalid connection')
      }
    },
    [addEdge]
  )

  // Handle edge updates
  const onEdgeUpdate: OnEdgeUpdate = useCallback(
    (oldEdge, newConnection) => {
      if (!newConnection.source || !newConnection.target) return

      // Remove old edge and add new one
      removeEdge(oldEdge.id)
      
      const newEdge: EdgeModel = {
        id: nanoid(),
        from: {
          node: newConnection.source,
          port: newConnection.sourceHandle || 'out',
        },
        to: {
          node: newConnection.target,
          port: newConnection.targetHandle || 'in',
        },
      }

      addEdge(newEdge)
    },
    [removeEdge, addEdge]
  )

  // Connection validation
  const isValidConnectionHandler: ValidConnection = useCallback(
    (connection) => {
      if (!connection.source || !connection.target) return false
      
      return isValidConnection(
        {
          source: connection.source,
          sourceHandle: connection.sourceHandle || 'out',
          target: connection.target,
          targetHandle: connection.targetHandle || 'in',
        },
        workflow
      )
    },
    [workflow]
  )

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

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Delete' || event.key === 'Backspace') {
        if (selectedId) {
          // Check if it's an edge or node
          const isEdge = workflow.edges.some(edge => edge.id === selectedId)
          if (isEdge) {
            removeEdge(selectedId)
          } else {
            removeNode(selectedId)
          }
          setSelectedId(undefined)
        }
      } else if (event.ctrlKey || event.metaKey) {
        if (event.key === 'z') {
          event.preventDefault()
          if (event.shiftKey) {
            redo()
          } else {
            undo()
          }
        } else if (event.key === 's') {
          event.preventDefault()
          handleSave()
        }
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [selectedId, removeEdge, removeNode, setSelectedId, undo, redo, workflow.edges])

  // Handle save
  const handleSave = useCallback(async () => {
    try {
      await workflowAPI.saveWorkflow(workflowId, workflow)
      console.log('Workflow saved successfully')
    } catch (error) {
      console.error('Failed to save workflow:', error)
    }
  }, [workflowId, workflow])

  // Handle validate
  const handleValidate = useCallback(async () => {
    try {
      const response = await workflowAPI.validateWorkflow(workflowId)
      console.log('Validation issues:', response.data.issues)
      // The store will automatically update with validation results
    } catch (error) {
      console.error('Failed to validate workflow:', error)
    }
  }, [workflowId])

  // Handle simulate
  const handleSimulate = useCallback(async () => {
    setIsSimulating(true)
    try {
      const response = await workflowAPI.simulateWorkflow(workflowId)
      setSimulationTrace(response.data.trace)
      setSimulationPanel(true)
    } catch (error) {
      console.error('Failed to simulate workflow:', error)
    } finally {
      setIsSimulating(false)
    }
  }, [workflowId])

  return (
    <div className="h-full w-full flex">
      <div className="flex-1" ref={reactFlowWrapper}>
        <ReactFlow
          nodes={reactFlowNodes}
          edges={reactFlowEdges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onEdgeUpdate={onEdgeUpdate}
          onDragOver={onDragOver}
          onDrop={onDrop}
          nodeTypes={nodeTypes}
          connectionMode={ConnectionMode.Loose}
          isValidConnection={isValidConnectionHandler}
          onNodeClick={(_, node) => setSelectedId(node.id)}
          onEdgeClick={(_, edge) => setSelectedId(edge.id)}
          onPaneClick={() => setSelectedId(undefined)}
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
          
          {/* Top toolbar */}
          <Panel position="top-left" className="bg-white p-4 rounded-lg shadow-lg">
            <div className="flex gap-2">
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                Save
              </button>
              <button
                onClick={handleValidate}
                className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 transition-colors"
              >
                Validate
              </button>
              <button
                onClick={handleSimulate}
                disabled={isSimulating}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                {isSimulating ? 'Simulating...' : 'Simulate'}
              </button>
            </div>
          </Panel>

          {/* Trigger/Action Creation Panel */}
          <Panel position="top-center" className="bg-white p-4 rounded-lg shadow-lg">
            <TriggerActionManager />
          </Panel>

          {/* Undo/Redo panel */}
          <Panel position="top-right" className="bg-white p-4 rounded-lg shadow-lg">
            <div className="flex gap-2">
              <button
                onClick={undo}
                className="px-3 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
              >
                Undo
              </button>
              <button
                onClick={redo}
                className="px-3 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
              >
                Redo
              </button>
            </div>
          </Panel>

          {/* Instructions panel */}
          <Panel position="bottom-left" className="bg-white p-4 rounded-lg shadow-lg">
            <div className="text-sm text-gray-600">
              <p>• Drag nodes from palette to create connections</p>
              <p>• Delete/Backspace removes selected items</p>
              <p>• Ctrl+Z/Ctrl+Shift+Z for undo/redo</p>
            </div>
          </Panel>
        </ReactFlow>
      </div>

      {/* Simulation panel */}
      {simulationPanel && (
        <div className="w-80 bg-white border-l border-gray-200 p-4 overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Simulation Results</h3>
            <button
              onClick={() => setSimulationPanel(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          
          <div className="space-y-3">
            {simulationTrace.map((step, index) => (
              <div key={index} className="border border-gray-200 rounded p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-sm">{step.node_name}</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    step.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {step.status}
                  </span>
                </div>
                <div className="text-xs text-gray-600">
                  <p>Type: {step.node_type}</p>
                  <p>Duration: {step.execution_time.toFixed(0)}ms</p>
                  {step.error && (
                    <p className="text-red-600">Error: {step.error}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
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
