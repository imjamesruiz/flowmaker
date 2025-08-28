import React, { useState, useCallback, useRef, useEffect } from 'react';
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
  ReactFlowProvider,
  useReactFlow,
  Panel,
  ConnectionMode,
  NodeTypes,
  EdgeTypes,
  ConnectionLineType,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  Plus,
  Play,
  Pause,
  Save,
  Undo,
  Redo,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Settings,
  MousePointer,
  Hand,
  GitBranch,
  Zap,
  Code,
  AlertCircle,
  Trash2,
  Copy,
  Download,
  Upload,
} from 'lucide-react';

import { WorkflowNode } from './Node';
import { SmartEdge } from './SmartEdge';

// Node and Edge types
const nodeTypes: NodeTypes = {
  workflowNode: WorkflowNode,
};

const edgeTypes: EdgeTypes = {
  smartEdge: SmartEdge,
};

// Sample node data with proper data flow structure
const initialNodes: Node[] = [
  {
    id: '1',
    type: 'workflowNode',
    position: { x: 100, y: 100 },
    data: {
      label: 'Gmail Trigger',
      type: 'trigger',
      status: 'idle',
      integration: 'gmail',
      config: {
        trigger_type: 'new_email',
        label: 'INBOX',
        from_address: '',
        subject_contains: ''
      },
      inputs: [],
      outputs: [
        { id: 'email', label: 'Email', type: 'object', required: false },
        { id: 'subject', label: 'Subject', type: 'string', required: false },
        { id: 'from', label: 'From', type: 'string', required: false },
      ],
    },
  },
  {
    id: '2',
    type: 'workflowNode',
    position: { x: 400, y: 100 },
    data: {
      label: 'Filter Emails',
      type: 'condition',
      status: 'idle',
      config: {
        condition_type: 'simple',
        field: 'subject',
        operator: 'contains',
        value: 'urgent'
      },
      inputs: [
        { id: 'email', label: 'Email', type: 'object', required: true },
        { id: 'subject', label: 'Subject', type: 'string', required: false },
      ],
      outputs: [
        { id: 'true', label: 'True', type: 'object', required: false },
        { id: 'false', label: 'False', type: 'object', required: false },
      ],
    },
  },
  {
    id: '3',
    type: 'workflowNode',
    position: { x: 700, y: 50 },
    data: {
      label: 'Send Slack Alert',
      type: 'action',
      status: 'idle',
      integration: 'slack',
      config: {
        action_type: 'send_message',
        channel: '#alerts',
        text: 'Urgent email received: {{subject}}',
        integration_provider: 'slack'
      },
      inputs: [
        { id: 'email', label: 'Email', type: 'object', required: true },
        { id: 'subject', label: 'Subject', type: 'string', required: false },
      ],
      outputs: [
        { id: 'message_id', label: 'Message ID', type: 'string', required: false },
        { id: 'channel', label: 'Channel', type: 'string', required: false },
      ],
    },
  },
  {
    id: '4',
    type: 'workflowNode',
    position: { x: 700, y: 150 },
    data: {
      label: 'Send Email Response',
      type: 'action',
      status: 'idle',
      integration: 'gmail',
      config: {
        action_type: 'send_email',
        to: '{{from}}',
        subject: 'Re: {{subject}}',
        body: 'Thank you for your email. We will get back to you soon.',
        integration_provider: 'gmail'
      },
      inputs: [
        { id: 'email', label: 'Email', type: 'object', required: true },
        { id: 'from', label: 'From', type: 'string', required: false },
        { id: 'subject', label: 'Subject', type: 'string', required: false },
      ],
      outputs: [
        { id: 'message_id', label: 'Message ID', type: 'string', required: false },
        { id: 'thread_id', label: 'Thread ID', type: 'string', required: false },
      ],
    },
  },
];

const initialEdges: Edge[] = [
  {
    id: 'e1-2',
    source: '1',
    target: '2',
    sourceHandle: 'email',
    targetHandle: 'email',
    type: 'smartEdge',
    data: {
      label: 'Email Data',
      dataMapping: {
        'email': 'email',
        'subject': 'subject'
      }
    },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      width: 20,
      height: 20,
      color: '#2563eb',
    },
    style: {
      strokeWidth: 2,
      stroke: '#2563eb',
    },
  },
  {
    id: 'e2-3',
    source: '2',
    target: '3',
    sourceHandle: 'true',
    targetHandle: 'email',
    type: 'smartEdge',
    data: {
      label: 'Urgent Email',
      condition: 'true'
    },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      width: 20,
      height: 20,
      color: '#dc2626',
    },
    style: {
      strokeWidth: 2,
      stroke: '#dc2626',
    },
  },
  {
    id: 'e2-4',
    source: '2',
    target: '4',
    sourceHandle: 'false',
    targetHandle: 'email',
    type: 'smartEdge',
    data: {
      label: 'Regular Email',
      condition: 'false'
    },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      width: 20,
      height: 20,
      color: '#059669',
    },
    style: {
      strokeWidth: 2,
      stroke: '#059669',
    },
  },
];

interface WorkflowEditorProps {
  workflowId?: string;
  onSave?: (workflow: any) => void;
  onExecute?: (workflow: any) => void;
  readOnly?: boolean;
}

export function WorkflowEditor({ 
  workflowId, 
  onSave, 
  onExecute, 
  readOnly = false 
}: WorkflowEditorProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [workflowName, setWorkflowName] = useState('Email Processing Workflow');
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionStatus, setExecutionStatus] = useState<'idle' | 'running' | 'completed' | 'error'>('idle');
  
  const reactFlowInstance = useReactFlow();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);

  // Handle node selection
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  // Handle edge connections
  const onConnect = useCallback((params: Connection) => {
    // Validate connection
    const sourceNode = nodes.find(n => n.id === params.source);
    const targetNode = nodes.find(n => n.id === params.target);
    
    if (sourceNode && targetNode) {
      // Check if output and input types are compatible
      const sourceOutput = sourceNode.data.outputs?.find((o: any) => o.id === params.sourceHandle);
      const targetInput = targetNode.data.inputs?.find((i: any) => i.id === params.targetHandle);
      
      if (sourceOutput && targetInput) {
        // Add the connection
        const newEdge: Edge = {
          id: `e${params.source}-${params.target}`,
          source: params.source!,
          target: params.target!,
          sourceHandle: params.sourceHandle!,
          targetHandle: params.targetHandle!,
          type: 'smartEdge',
          data: {
            label: `${sourceOutput.label} → ${targetInput.label}`,
            dataMapping: {
              [sourceOutput.id]: targetInput.id
            }
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            width: 20,
            height: 20,
            color: '#2563eb',
          },
          style: {
            strokeWidth: 2,
            stroke: '#2563eb',
          },
        };
        
        setEdges((eds) => addEdge(newEdge, eds));
      }
    }
  }, [nodes, setEdges]);

  // Handle edge deletion
  const onEdgeDelete = useCallback((edge: Edge) => {
    setEdges((eds) => eds.filter((e) => e.id !== edge.id));
  }, [setEdges]);

  // Add new node
  const addNode = useCallback((nodeType: string, integration?: string) => {
    const newNode: Node = {
      id: `node-${Date.now()}`,
      type: 'workflowNode',
      position: { x: 200, y: 200 },
      data: {
        label: `New ${nodeType}`,
        type: nodeType,
        status: 'idle',
        integration,
        config: {},
        inputs: [],
        outputs: [],
      },
    };
    
    setNodes((nds) => [...nds, newNode]);
  }, [setNodes]);

  // Save workflow
  const saveWorkflow = useCallback(async () => {
    if (!workflowId) return;
    
    const workflowData = {
      id: workflowId,
      name: workflowName,
      nodes: nodes.map(node => ({
        id: node.id,
        type: node.data.type,
        name: node.data.label,
        position: node.position,
        config: node.data.config,
        integration: node.data.integration,
        inputs: node.data.inputs,
        outputs: node.data.outputs,
      })),
      edges: edges.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        sourceHandle: edge.sourceHandle,
        targetHandle: edge.targetHandle,
        data: edge.data,
      })),
    };
    
    if (onSave) {
      onSave(workflowData);
    }
  }, [workflowId, workflowName, nodes, edges, onSave]);

  // Execute workflow
  const executeWorkflow = useCallback(async () => {
    if (!workflowId) return;
    
    setIsExecuting(true);
    setExecutionStatus('running');
    
    try {
      const workflowData = {
        id: workflowId,
        nodes: nodes.map(node => ({
          id: node.id,
          type: node.data.type,
          config: node.data.config,
        })),
        edges: edges.map(edge => ({
          source: edge.source,
          target: edge.target,
          sourceHandle: edge.sourceHandle,
          targetHandle: edge.targetHandle,
        })),
      };
      
      if (onExecute) {
        await onExecute(workflowData);
      }
      
      setExecutionStatus('completed');
    } catch (error) {
      console.error('Workflow execution failed:', error);
      setExecutionStatus('error');
    } finally {
      setIsExecuting(false);
    }
  }, [workflowId, nodes, edges, onExecute]);

  // Zoom controls
  const onZoomIn = useCallback(() => {
    reactFlowInstance.zoomIn();
  }, [reactFlowInstance]);

  const onZoomOut = useCallback(() => {
    reactFlowInstance.zoomOut();
  }, [reactFlowInstance]);

  const onFitView = useCallback(() => {
    reactFlowInstance.fitView();
  }, [reactFlowInstance]);

  // Delete selected node
  const deleteSelectedNode = useCallback(() => {
    if (selectedNode) {
      setNodes((nds) => nds.filter((node) => node.id !== selectedNode.id));
      setEdges((eds) => eds.filter((edge) => edge.source !== selectedNode.id && edge.target !== selectedNode.id));
      setSelectedNode(null);
    }
  }, [selectedNode, setNodes, setEdges]);

  return (
    <div className="h-full w-full flex flex-col">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-4 border-b bg-white">
        <div className="flex items-center space-x-4">
          <Input
            value={workflowName}
            onChange={(e) => setWorkflowName(e.target.value)}
            className="w-64"
            placeholder="Workflow name"
          />
          
          <div className="flex items-center space-x-2">
            <Button
              onClick={saveWorkflow}
              disabled={readOnly}
              size="sm"
            >
              <Save className="w-4 h-4 mr-2" />
              Save
            </Button>
            
            <Button
              onClick={executeWorkflow}
              disabled={isExecuting || readOnly}
              size="sm"
              variant={executionStatus === 'running' ? 'secondary' : 'default'}
            >
              {isExecuting ? (
                <>
                  <Pause className="w-4 h-4 mr-2" />
                  Running...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Execute
                </>
              )}
            </Button>
          </div>
          
          {executionStatus === 'completed' && (
            <Badge variant="default" className="bg-green-100 text-green-800">
              Completed
            </Badge>
          )}
          
          {executionStatus === 'error' && (
            <Badge variant="destructive">
              <AlertCircle className="w-3 h-3 mr-1" />
              Error
            </Badge>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button size="sm" variant="outline">
                <Plus className="w-4 h-4 mr-2" />
                Add Node
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => addNode('trigger')}>
                <Zap className="w-4 h-4 mr-2" />
                Trigger
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => addNode('action')}>
                <Code className="w-4 h-4 mr-2" />
                Action
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => addNode('condition')}>
                <GitBranch className="w-4 h-4 mr-2" />
                Condition
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => addNode('transformer')}>
                <Settings className="w-4 h-4 mr-2" />
                Transformer
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          
          <Button
            onClick={deleteSelectedNode}
            disabled={!selectedNode || readOnly}
            size="sm"
            variant="outline"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>
      
      {/* Canvas */}
      <div className="flex-1 relative" ref={reactFlowWrapper}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          onEdgeClick={(event, edge) => onEdgeDelete(edge)}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          connectionMode={ConnectionMode.Loose}
          connectionLineType={ConnectionLineType.Bezier}
          snapToGrid={true}
          snapGrid={[15, 15]}
          fitView
          attributionPosition="bottom-left"
        >
          <Controls />
          <Background color="#aaa" gap={16} />
          <MiniMap
            nodeStrokeColor={(n) => {
              if (n.type === 'input') return '#0041d0';
              if (n.type === 'output') return '#ff0072';
              return '#1a192b';
            }}
            nodeColor={(n) => {
              if (n.data?.status === 'running') return '#fbbf24';
              if (n.data?.status === 'completed') return '#10b981';
              if (n.data?.status === 'error') return '#ef4444';
              return '#fff';
            }}
            nodeBorderRadius={2}
          />
          
          <Panel position="top-right" className="space-y-2">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    onClick={onZoomIn}
                    size="sm"
                    variant="outline"
                    className="w-8 h-8 p-0"
                  >
                    <ZoomIn className="w-4 h-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Zoom In</TooltipContent>
              </Tooltip>
            </TooltipProvider>
            
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    onClick={onZoomOut}
                    size="sm"
                    variant="outline"
                    className="w-8 h-8 p-0"
                  >
                    <ZoomOut className="w-4 h-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Zoom Out</TooltipContent>
              </Tooltip>
            </TooltipProvider>
            
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    onClick={onFitView}
                    size="sm"
                    variant="outline"
                    className="w-8 h-8 p-0"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Fit View</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </Panel>
        </ReactFlow>
      </div>
      
      {/* Properties Panel */}
      {selectedNode && (
        <div className="w-80 border-l bg-white p-4">
          <h3 className="font-semibold mb-4">Node Properties</h3>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Name</label>
              <Input
                value={selectedNode.data.label}
                onChange={(e) => {
                  setNodes((nds) =>
                    nds.map((node) =>
                      node.id === selectedNode.id
                        ? { ...node, data: { ...node.data, label: e.target.value } }
                        : node
                    )
                  );
                }}
                className="mt-1"
              />
            </div>
            
            <div>
              <label className="text-sm font-medium">Type</label>
              <Badge variant="outline" className="mt-1">
                {selectedNode.data.type}
              </Badge>
            </div>
            
            {selectedNode.data.integration && (
              <div>
                <label className="text-sm font-medium">Integration</label>
                <Badge variant="secondary" className="mt-1">
                  {selectedNode.data.integration}
                </Badge>
              </div>
            )}
            
            <div>
              <label className="text-sm font-medium">Status</label>
              <Badge 
                variant={
                  selectedNode.data.status === 'completed' ? 'default' :
                  selectedNode.data.status === 'error' ? 'destructive' :
                  selectedNode.data.status === 'running' ? 'secondary' : 'outline'
                }
                className="mt-1"
              >
                {selectedNode.data.status}
              </Badge>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Wrapper component for ReactFlowProvider
export const WorkflowEditorWrapper: React.FC<WorkflowEditorProps> = (props) => {
  return (
    <ReactFlowProvider>
      <WorkflowEditor {...props} />
    </ReactFlowProvider>
  );
};
