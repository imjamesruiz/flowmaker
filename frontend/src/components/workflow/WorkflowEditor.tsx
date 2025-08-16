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

// Sample node data
const initialNodes: Node[] = [
  {
    id: '1',
    type: 'workflowNode',
    position: { x: 100, y: 100 },
    data: {
      label: 'Gmail Trigger',
      type: 'trigger',
      status: 'idle',
      inputs: [],
      outputs: [
        { id: 'email', label: 'Email', type: 'object', required: false },
        { id: 'subject', label: 'Subject', type: 'string', required: false },
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
      inputs: [
        { id: 'email', label: 'Email', type: 'object', required: true },
      ],
      outputs: [
        { id: 'true', label: 'True', type: 'object', required: false },
        { id: 'false', label: 'False', type: 'object', required: false },
      ],
    },
  },
];

const initialEdges: Edge[] = [];

interface WorkflowEditorProps {
  workflowId?: string;
  onSave?: (nodes: Node[], edges: Edge[]) => void;
  onRun?: () => void;
}

export const WorkflowEditor: React.FC<WorkflowEditorProps> = ({
  workflowId,
  onSave,
  onRun,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStart, setConnectionStart] = useState<{ nodeId: string; handleId: string } | null>(null);
  const [isPanning, setIsPanning] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [selectedNodes, setSelectedNodes] = useState<string[]>([]);
  const [selectedEdges, setSelectedEdges] = useState<string[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [insertTarget, setInsertTarget] = useState<{ edgeId: string; position: { x: number; y: number } } | null>(null);

  const reactFlowInstance = useReactFlow();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);

  // Auto-pan when dragging near edges
  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      if (!reactFlowWrapper.current || !isConnecting) return;

      const rect = reactFlowWrapper.current.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      const { width, height } = rect;

      const panThreshold = 100;
      const panSpeed = 10;

      if (x < panThreshold) {
        reactFlowInstance.panBy({ x: -panSpeed, y: 0 });
      } else if (x > width - panThreshold) {
        reactFlowInstance.panBy({ x: panSpeed, y: 0 });
      }

      if (y < panThreshold) {
        reactFlowInstance.panBy({ x: 0, y: -panSpeed });
      } else if (y > height - panThreshold) {
        reactFlowInstance.panBy({ x: 0, y: panSpeed });
      }
    };

    if (isConnecting) {
      document.addEventListener('mousemove', handleMouseMove);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
    };
  }, [isConnecting, reactFlowInstance]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (event.key) {
        case 'Delete':
        case 'Backspace':
          // Delete selected nodes/edges
          break;
        case 'Escape':
          setIsConnecting(false);
          setConnectionStart(null);
          break;
        case ' ':
          event.preventDefault();
          setIsPanning(!isPanning);
          break;
        case 'z':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            // Undo
          }
          break;
        case 'y':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            // Redo
          }
          break;
        case 's':
          if (event.ctrlKey || event.metaKey) {
            event.preventDefault();
            onSave?.(nodes, edges);
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isPanning, nodes, edges, onSave]);

  // Connection handling
  const onConnectStart = useCallback((event: any, { nodeId, handleId }: any) => {
    setIsConnecting(true);
    setConnectionStart({ nodeId, handleId });
  }, []);

  const onConnectEnd = useCallback((event: any) => {
    setIsConnecting(false);
    setConnectionStart(null);
  }, []);

  const onConnect = useCallback((params: Connection) => {
    // Validate connection
    const sourceNode = nodes.find(n => n.id === params.source);
    const targetNode = nodes.find(n => n.id === params.target);
    
    if (sourceNode && targetNode) {
      const sourceOutput = sourceNode.data.outputs?.find(o => o.id === params.sourceHandle);
      const targetInput = targetNode.data.inputs?.find(i => i.id === params.targetHandle);
      
      // Check type compatibility
      const isValid = sourceOutput && targetInput && sourceOutput.type === targetInput.type;
      
      const newEdge: Edge = {
        ...params,
        id: `e${params.source}-${params.target}`,
        type: 'smartEdge',
        data: {
          label: `${sourceOutput?.label} → ${targetInput?.label}`,
          type: isValid ? 'default' : 'error',
          errorMessage: isValid ? undefined : `Cannot connect ${sourceOutput?.type} to ${targetInput?.type}`,
        },
      };
      
      setEdges((eds) => addEdge(newEdge, eds));
    }
  }, [nodes, setEdges]);

  // Insert node on edge
  const handleInsertOnEdge = useCallback((edgeId: string, nodeType: string) => {
    const edge = edges.find(e => e.id === edgeId);
    if (!edge) return;

    const sourceNode = nodes.find(n => n.id === edge.source);
    const targetNode = nodes.find(n => n.id === edge.target);
    
    if (!sourceNode || !targetNode) return;

    // Create new node at midpoint
    const midX = (sourceNode.position.x + targetNode.position.x) / 2;
    const midY = (sourceNode.position.y + targetNode.position.y) / 2;

    const newNodeId = `node-${Date.now()}`;
    const newNode: Node = {
      id: newNodeId,
      type: 'workflowNode',
      position: { x: midX, y: midY },
      data: {
        label: `New ${nodeType}`,
        type: nodeType as any,
        status: 'idle',
        inputs: [{ id: 'input', label: 'Input', type: 'object', required: true }],
        outputs: [{ id: 'output', label: 'Output', type: 'object', required: false }],
      },
    };

    // Update edges
    const newEdges = edges.filter(e => e.id !== edgeId);
    newEdges.push(
      {
        ...edge,
        id: `${edge.source}-${newNodeId}`,
        target: newNodeId,
        targetHandle: 'input',
      },
      {
        ...edge,
        id: `${newNodeId}-${edge.target}`,
        source: newNodeId,
        sourceHandle: 'output',
      }
    );

    setNodes(nds => [...nds, newNode]);
    setEdges(newEdges);
    setInsertTarget(null);
  }, [nodes, edges, setNodes, setEdges]);

  // Node selection
  const onNodeClick = useCallback((event: any, node: Node) => {
    setSelectedNodes(prev => 
      event.ctrlKey || event.metaKey
        ? prev.includes(node.id) 
          ? prev.filter(id => id !== node.id)
          : [...prev, node.id]
        : [node.id]
    );
  }, []);

  const onEdgeClick = useCallback((event: any, edge: Edge) => {
    setSelectedEdges(prev => 
      event.ctrlKey || event.metaKey
        ? prev.includes(edge.id) 
          ? prev.filter(id => id !== edge.id)
          : [...prev, edge.id]
        : [edge.id]
    );
  }, []);

  // Canvas click
  const onPaneClick = useCallback(() => {
    setSelectedNodes([]);
    setSelectedEdges([]);
  }, []);

  return (
    <div className="h-full w-full relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onConnectStart={onConnectStart}
        onConnectEnd={onConnectEnd}
        onNodeClick={onNodeClick}
        onEdgeClick={onEdgeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        connectionMode={ConnectionMode.Loose}
        snapToGrid={true}
        snapGrid={[15, 15]}
        fitView
        className={cn(
          'bg-gray-50',
          isPanning && 'cursor-grab active:cursor-grabbing'
        )}
      >
        <Background />
        <Controls />
        <MiniMap />
        
        {/* Top Toolbar */}
        <Panel position="top-left" className="flex items-center gap-2 p-2 bg-white border border-gray-200 rounded-lg shadow-lg">
          <Button
            size="sm"
            variant={isRunning ? "destructive" : "default"}
            onClick={() => {
              setIsRunning(!isRunning);
              onRun?.();
            }}
          >
            {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            {isRunning ? 'Stop' : 'Run'}
          </Button>
          
          <Button size="sm" variant="outline" onClick={() => onSave?.(nodes, edges)}>
            <Save className="w-4 h-4" />
            Save
          </Button>
          
          <div className="w-px h-6 bg-gray-300" />
          
          <Button size="sm" variant="outline">
            <Undo className="w-4 h-4" />
          </Button>
          <Button size="sm" variant="outline">
            <Redo className="w-4 h-4" />
          </Button>
          
          <div className="w-px h-6 bg-gray-300" />
          
          <Button size="sm" variant="outline">
            <ZoomIn className="w-4 h-4" />
          </Button>
          <Button size="sm" variant="outline">
            <ZoomOut className="w-4 h-4" />
          </Button>
          <Button size="sm" variant="outline">
            <RotateCcw className="w-4 h-4" />
          </Button>
        </Panel>

        {/* Bottom Status Bar */}
        <Panel position="bottom-left" className="flex items-center gap-4 p-2 bg-white border border-gray-200 rounded-lg shadow-lg">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span>{nodes.length} nodes</span>
            <span>•</span>
            <span>{edges.length} connections</span>
            <span>•</span>
            <span>Zoom: {Math.round(zoom * 100)}%</span>
          </div>
          
          {isConnecting && (
            <Badge variant="secondary" className="bg-blue-100 text-blue-700">
              Connecting...
            </Badge>
          )}
          
          {isPanning && (
            <Badge variant="secondary" className="bg-gray-100 text-gray-700">
              Pan Mode
            </Badge>
          )}
        </Panel>

        {/* Insert-on-Edge Toolbar */}
        {insertTarget && (
          <Panel
            position="top"
            style={{
              left: insertTarget.position.x,
              top: insertTarget.position.y,
              transform: 'translate(-50%, -100%)',
            }}
            className="bg-white border border-gray-200 rounded-lg shadow-lg p-2"
          >
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Insert:</span>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleInsertOnEdge(insertTarget.edgeId, 'action')}
              >
                <Zap className="w-3 h-3 mr-1" />
                Action
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleInsertOnEdge(insertTarget.edgeId, 'condition')}
              >
                <GitBranch className="w-3 h-3 mr-1" />
                Condition
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => handleInsertOnEdge(insertTarget.edgeId, 'transform')}
              >
                <Code className="w-3 h-3 mr-1" />
                Transform
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setInsertTarget(null)}
              >
                ✕
              </Button>
            </div>
          </Panel>
        )}
      </ReactFlow>
    </div>
  );
};

// Wrapper component for ReactFlowProvider
export const WorkflowEditorWrapper: React.FC<WorkflowEditorProps> = (props) => {
  return (
    <ReactFlowProvider>
      <WorkflowEditor {...props} />
    </ReactFlowProvider>
  );
};
