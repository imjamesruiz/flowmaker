import React, { useState, useRef, useCallback } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Play, 
  Settings, 
  Code, 
  GitBranch, 
  Zap,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';

interface NodeData {
  label: string;
  type: 'trigger' | 'action' | 'condition' | 'transform';
  status: 'idle' | 'running' | 'success' | 'error';
  inputs: HandleData[];
  outputs: HandleData[];
  config?: Record<string, any>;
}

interface HandleData {
  id: string;
  label: string;
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  required: boolean;
  description?: string;
}

const nodeTypeIcons = {
  trigger: Play,
  action: Zap,
  condition: GitBranch,
  transform: Code,
};

const nodeTypeColors = {
  trigger: 'border-blue-500 bg-blue-50',
  action: 'border-green-500 bg-green-50',
  condition: 'border-purple-500 bg-purple-50',
  transform: 'border-orange-500 bg-orange-50',
};

const statusColors = {
  idle: 'text-gray-500',
  running: 'text-blue-500',
  success: 'text-green-500',
  error: 'text-red-500',
};

export const WorkflowNode: React.FC<NodeProps<NodeData>> = ({
  id,
  data,
  selected,
  xPos,
  yPos,
  dragging,
}) => {
  const [hoveredHandle, setHoveredHandle] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const nodeRef = useRef<HTMLDivElement>(null);

  const handleMouseEnter = useCallback(() => {
    // Show all handles when hovering over node
  }, []);

  const handleMouseLeave = useCallback(() => {
    if (!selected) {
      setHoveredHandle(null);
    }
  }, [selected]);

  const getHandleIcon = (type: string) => {
    switch (type) {
      case 'string': return '📝';
      case 'number': return '🔢';
      case 'boolean': return '✅';
      case 'object': return '📦';
      case 'array': return '📋';
      default: return '📄';
    }
  };

  const getStatusIcon = () => {
    switch (data.status) {
      case 'running': return <Play className="w-4 h-4 animate-pulse" />;
      case 'success': return <CheckCircle className="w-4 h-4" />;
      case 'error': return <XCircle className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  return (
    <div
      ref={nodeRef}
      className={cn(
        'relative group transition-all duration-200',
        selected && 'ring-2 ring-blue-500 ring-offset-2',
        dragging && 'cursor-grabbing'
      )}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* Input Handles */}
      {data.inputs.map((input, index) => (
        <Handle
          key={`input-${input.id}`}
          type="target"
          position={Position.Left}
          id={input.id}
          className={cn(
            'w-6 h-6 border-2 border-gray-300 bg-white rounded-full transition-all duration-200',
            'hover:scale-110 hover:border-blue-500 hover:bg-blue-50',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
            selected && 'border-blue-500 bg-blue-50',
            hoveredHandle === input.id && 'scale-110 border-blue-500 bg-blue-50'
          )}
          style={{
            top: `${(index + 1) * 25}%`,
            left: '-12px',
          }}
          onMouseEnter={() => setHoveredHandle(input.id)}
          onMouseLeave={() => setHoveredHandle(null)}
        >
          <div className="absolute right-8 top-1/2 transform -translate-y-1/2 bg-white border border-gray-200 rounded-lg px-2 py-1 text-xs shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
            <div className="flex items-center gap-1">
              <span>{getHandleIcon(input.type)}</span>
              <span className="font-medium">{input.label}</span>
              {input.required && <span className="text-red-500">*</span>}
            </div>
            {input.description && (
              <div className="text-gray-500 mt-1">{input.description}</div>
            )}
          </div>
        </Handle>
      ))}

      {/* Node Content */}
      <Card
        className={cn(
          'w-64 transition-all duration-200 cursor-grab active:cursor-grabbing',
          'hover:shadow-lg hover:scale-105',
          nodeTypeColors[data.type],
          selected && 'shadow-xl scale-105'
        )}
      >
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              {React.createElement(nodeTypeIcons[data.type], { className: 'w-4 h-4' })}
              {data.label}
            </CardTitle>
            <div className={cn('flex items-center gap-1', statusColors[data.status])}>
              {getStatusIcon()}
            </div>
          </div>
          <Badge variant="outline" className="text-xs">
            {data.type}
          </Badge>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="text-xs text-gray-600">
            {data.inputs.length} inputs • {data.outputs.length} outputs
          </div>
        </CardContent>
      </Card>

      {/* Output Handles */}
      {data.outputs.map((output, index) => (
        <Handle
          key={`output-${output.id}`}
          type="source"
          position={Position.Right}
          id={output.id}
          className={cn(
            'w-6 h-6 border-2 border-gray-300 bg-white rounded-full transition-all duration-200',
            'hover:scale-110 hover:border-green-500 hover:bg-green-50',
            'focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2',
            selected && 'border-green-500 bg-green-50',
            hoveredHandle === output.id && 'scale-110 border-green-500 bg-green-50'
          )}
          style={{
            top: `${(index + 1) * 25}%`,
            right: '-12px',
          }}
          onMouseEnter={() => setHoveredHandle(output.id)}
          onMouseLeave={() => setHoveredHandle(null)}
        >
          <div className="absolute left-8 top-1/2 transform -translate-y-1/2 bg-white border border-gray-200 rounded-lg px-2 py-1 text-xs shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
            <div className="flex items-center gap-1">
              <span>{getHandleIcon(output.type)}</span>
              <span className="font-medium">{output.label}</span>
            </div>
            {output.description && (
              <div className="text-gray-500 mt-1">{output.description}</div>
            )}
          </div>
        </Handle>
      ))}

      {/* Node Actions (visible on hover/select) */}
      {(selected || hoveredHandle) && (
        <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 flex items-center gap-1 bg-white border border-gray-200 rounded-lg px-2 py-1 shadow-lg">
          <Button size="sm" variant="ghost" className="h-6 w-6 p-0">
            <Settings className="w-3 h-3" />
          </Button>
          <Button size="sm" variant="ghost" className="h-6 w-6 p-0">
            <Code className="w-3 h-3" />
          </Button>
        </div>
      )}
    </div>
  );
};
