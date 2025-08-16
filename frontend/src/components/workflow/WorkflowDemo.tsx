import React, { useState } from 'react';
import { Node, Edge } from 'reactflow';
import { WorkflowEditorWrapper } from './WorkflowEditor';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Play, 
  Pause, 
  Save, 
  Download, 
  Upload, 
  Settings,
  Zap,
  GitBranch,
  Code,
  AlertCircle,
  CheckCircle,
  Plus
} from 'lucide-react';

// Sample workflow data
const sampleNodes: Node[] = [
  {
    id: '1',
    type: 'workflowNode',
    position: { x: 100, y: 100 },
    data: {
      label: 'Gmail Trigger',
      type: 'trigger',
      status: 'success',
      inputs: [],
      outputs: [
        { id: 'email', label: 'Email', type: 'object', required: false, description: 'Full email object with headers and body' },
        { id: 'subject', label: 'Subject', type: 'string', required: false, description: 'Email subject line' },
        { id: 'sender', label: 'Sender', type: 'string', required: false, description: 'Email sender address' },
      ],
    },
  },
  {
    id: '2',
    type: 'workflowNode',
    position: { x: 400, y: 100 },
    data: {
      label: 'Filter Important',
      type: 'condition',
      status: 'idle',
      inputs: [
        { id: 'email', label: 'Email', type: 'object', required: true, description: 'Email to filter' },
      ],
      outputs: [
        { id: 'true', label: 'Important', type: 'object', required: false, description: 'Important emails' },
        { id: 'false', label: 'Not Important', type: 'object', required: false, description: 'Non-important emails' },
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
      inputs: [
        { id: 'email', label: 'Email', type: 'object', required: true, description: 'Important email to alert about' },
      ],
      outputs: [
        { id: 'message', label: 'Message', type: 'object', required: false, description: 'Slack message sent' },
      ],
    },
  },
  {
    id: '4',
    type: 'workflowNode',
    position: { x: 700, y: 150 },
    data: {
      label: 'Archive Email',
      type: 'action',
      status: 'idle',
      inputs: [
        { id: 'email', label: 'Email', type: 'object', required: true, description: 'Email to archive' },
      ],
      outputs: [
        { id: 'archived', label: 'Archived', type: 'object', required: false, description: 'Archived email result' },
      ],
    },
  },
  {
    id: '5',
    type: 'workflowNode',
    position: { x: 1000, y: 100 },
    data: {
      label: 'Extract Data',
      type: 'transform',
      status: 'idle',
      inputs: [
        { id: 'email', label: 'Email', type: 'object', required: true, description: 'Email to extract data from' },
      ],
      outputs: [
        { id: 'data', label: 'Extracted Data', type: 'object', required: false, description: 'Structured data from email' },
      ],
    },
  },
];

const sampleEdges: Edge[] = [
  {
    id: 'e1-2',
    source: '1',
    sourceHandle: 'email',
    target: '2',
    targetHandle: 'email',
    type: 'smartEdge',
    data: {
      label: 'Email → Filter',
      type: 'default',
    },
  },
  {
    id: 'e2-3',
    source: '2',
    sourceHandle: 'true',
    target: '3',
    targetHandle: 'email',
    type: 'smartEdge',
    data: {
      label: 'Important → Slack',
      type: 'conditional',
      condition: 'true',
    },
  },
  {
    id: 'e2-4',
    source: '2',
    sourceHandle: 'false',
    target: '4',
    targetHandle: 'email',
    type: 'smartEdge',
    data: {
      label: 'Not Important → Archive',
      type: 'conditional',
      condition: 'false',
    },
  },
  {
    id: 'e3-5',
    source: '3',
    sourceHandle: 'message',
    target: '5',
    targetHandle: 'email',
    type: 'smartEdge',
    data: {
      label: 'Message → Extract',
      type: 'default',
    },
  },
];

export const WorkflowDemo: React.FC = () => {
  const [nodes, setNodes] = useState<Node[]>(sampleNodes);
  const [edges, setEdges] = useState<Edge[]>(sampleEdges);
  const [isRunning, setIsRunning] = useState(false);
  const [workflowStatus, setWorkflowStatus] = useState<'idle' | 'running' | 'success' | 'error'>('idle');

  const handleSave = (newNodes: Node[], newEdges: Edge[]) => {
    setNodes(newNodes);
    setEdges(newEdges);
    console.log('Workflow saved:', { nodes: newNodes, edges: newEdges });
    
    // Simulate save success
    setWorkflowStatus('success');
    setTimeout(() => setWorkflowStatus('idle'), 2000);
  };

  const handleRun = () => {
    setIsRunning(true);
    setWorkflowStatus('running');
    
    // Simulate workflow execution
    setTimeout(() => {
      setIsRunning(false);
      setWorkflowStatus('success');
      
      // Update node statuses
      setNodes(prev => prev.map(node => ({
        ...node,
        data: {
          ...node.data,
          status: 'success' as const,
        },
      })));
      
      setTimeout(() => {
        setWorkflowStatus('idle');
        setNodes(prev => prev.map(node => ({
          ...node,
          data: {
            ...node.data,
            status: 'idle' as const,
          },
        })));
      }, 3000);
    }, 2000);
  };

  const handleExport = () => {
    const workflowData = { nodes, edges };
    const blob = new Blob([JSON.stringify(workflowData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'worqly-workflow.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const workflowData = JSON.parse(e.target?.result as string);
        setNodes(workflowData.nodes);
        setEdges(workflowData.edges);
      } catch (error) {
        console.error('Failed to import workflow:', error);
      }
    };
    reader.readAsText(file);
  };

  const getStatusIcon = () => {
    switch (workflowStatus) {
      case 'running': return <Play className="w-4 h-4 animate-pulse" />;
      case 'success': return <CheckCircle className="w-4 h-4" />;
      case 'error': return <AlertCircle className="w-4 h-4" />;
      default: return <Zap className="w-4 h-4" />;
    }
  };

  const getStatusColor = () => {
    switch (workflowStatus) {
      case 'running': return 'text-blue-500';
      case 'success': return 'text-green-500';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-gray-900">Worqly Workflow Editor</h1>
            <Badge variant="outline" className={getStatusColor()}>
              {getStatusIcon()}
              <span className="ml-1 capitalize">{workflowStatus}</span>
            </Badge>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant={isRunning ? "destructive" : "default"}
              onClick={handleRun}
              disabled={isRunning}
            >
              {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              {isRunning ? 'Stop' : 'Run Workflow'}
            </Button>
            
            <Button size="sm" variant="outline" onClick={() => handleSave(nodes, edges)}>
              <Save className="w-4 h-4" />
              Save
            </Button>
            
            <Button size="sm" variant="outline" onClick={handleExport}>
              <Download className="w-4 h-4" />
              Export
            </Button>
            
            <Button size="sm" variant="outline" asChild>
              <label>
                <Upload className="w-4 h-4" />
                Import
                <input
                  type="file"
                  accept=".json"
                  onChange={handleImport}
                  className="hidden"
                />
              </label>
            </Button>
            
            <Button size="sm" variant="outline">
              <Settings className="w-4 h-4" />
              Settings
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Sidebar */}
        <aside className="w-80 bg-white border-r border-gray-200 p-4 overflow-y-auto">
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Node Types</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center gap-2 p-2 rounded-lg bg-blue-50 border border-blue-200">
                  <Play className="w-4 h-4 text-blue-500" />
                  <span className="text-sm font-medium">Triggers</span>
                  <Badge variant="secondary" className="ml-auto">3</Badge>
                </div>
                <div className="flex items-center gap-2 p-2 rounded-lg bg-green-50 border border-green-200">
                  <Zap className="w-4 h-4 text-green-500" />
                  <span className="text-sm font-medium">Actions</span>
                  <Badge variant="secondary" className="ml-auto">12</Badge>
                </div>
                <div className="flex items-center gap-2 p-2 rounded-lg bg-purple-50 border border-purple-200">
                  <GitBranch className="w-4 h-4 text-purple-500" />
                  <span className="text-sm font-medium">Conditions</span>
                  <Badge variant="secondary" className="ml-auto">8</Badge>
                </div>
                <div className="flex items-center gap-2 p-2 rounded-lg bg-orange-50 border border-orange-200">
                  <Code className="w-4 h-4 text-orange-500" />
                  <span className="text-sm font-medium">Transforms</span>
                  <Badge variant="secondary" className="ml-auto">6</Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Workflow Stats</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Nodes:</span>
                  <span className="font-medium">{nodes.length}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Connections:</span>
                  <span className="font-medium">{edges.length}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Execution Time:</span>
                  <span className="font-medium">~2.3s</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Success Rate:</span>
                  <span className="font-medium text-green-600">98.5%</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button size="sm" variant="outline" className="w-full justify-start">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Gmail Trigger
                </Button>
                <Button size="sm" variant="outline" className="w-full justify-start">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Slack Action
                </Button>
                <Button size="sm" variant="outline" className="w-full justify-start">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Filter Condition
                </Button>
              </CardContent>
            </Card>
          </div>
        </aside>

        {/* Workflow Editor */}
        <main className="flex-1">
          <WorkflowEditorWrapper
            workflowId="demo-workflow"
            onSave={handleSave}
            onRun={handleRun}
          />
        </main>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 px-6 py-3">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center gap-4">
            <span>Worqly v1.0.0</span>
            <span>•</span>
            <span>React Flow v11.0.0</span>
            <span>•</span>
            <span>TypeScript v5.0.0</span>
          </div>
          
          <div className="flex items-center gap-4">
            <span>Last saved: 2 minutes ago</span>
            <span>•</span>
            <span>Auto-save enabled</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
