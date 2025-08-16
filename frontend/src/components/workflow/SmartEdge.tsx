import React, { useState, useRef, useCallback } from 'react';
import { EdgeProps, getBezierPath, getSmoothStepPath } from 'reactflow';
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
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { 
  MoreHorizontal, 
  Edit, 
  Trash2, 
  Copy, 
  GitBranch,
  ArrowRight,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

interface EdgeData {
  label?: string;
  condition?: string;
  type?: 'default' | 'conditional' | 'error' | 'success';
  isValid?: boolean;
  errorMessage?: string;
}

export const SmartEdge: React.FC<EdgeProps<EdgeData>> = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
  style,
  markerEnd,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(data?.label || '');
  const [isHovered, setIsHovered] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Calculate orthogonal path
  const getOrthogonalPath = useCallback(() => {
    const offset = 50;
    const midX = (sourceX + targetX) / 2;
    
    // Create orthogonal path with rounded corners
    const path = [
      `M ${sourceX} ${sourceY}`,
      `L ${sourceX + offset} ${sourceY}`,
      `L ${sourceX + offset} ${targetY}`,
      `L ${targetX} ${targetY}`,
    ].join(' ');
    
    return path;
  }, [sourceX, sourceY, targetX, targetY]);

  const edgePath = getOrthogonalPath();

  const getEdgeColor = () => {
    if (data?.type === 'error') return '#ef4444';
    if (data?.type === 'success') return '#22c55e';
    if (data?.type === 'conditional') return '#8b5cf6';
    if (selected) return '#3b82f6';
    if (isHovered) return '#6b7280';
    return '#9ca3af';
  };

  const getEdgeWidth = () => {
    if (selected) return 3;
    if (isHovered) return 2.5;
    return 2;
  };

  const handleLabelClick = () => {
    setIsEditing(true);
    setEditValue(data?.label || '');
    setTimeout(() => inputRef.current?.focus(), 0);
  };

  const handleLabelSave = () => {
    // Here you would typically call an update function
    setIsEditing(false);
  };

  const handleLabelCancel = () => {
    setIsEditing(false);
    setEditValue(data?.label || '');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleLabelSave();
    } else if (e.key === 'Escape') {
      handleLabelCancel();
    }
  };

  const getEdgeIcon = () => {
    if (data?.type === 'conditional') return <GitBranch className="w-3 h-3" />;
    if (data?.type === 'error') return <AlertCircle className="w-3 h-3" />;
    if (data?.type === 'success') return <CheckCircle className="w-3 h-3" />;
    return <ArrowRight className="w-3 h-3" />;
  };

  return (
    <>
      {/* Main Edge Path */}
      <path
        d={edgePath}
        stroke={getEdgeColor()}
        strokeWidth={getEdgeWidth()}
        fill="none"
        className="transition-all duration-200"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      />

      {/* Edge Label */}
      {data?.label && (
        <foreignObject
          width={120}
          height={40}
          x={(sourceX + targetX) / 2 - 60}
          y={(sourceY + targetY) / 2 - 20}
          className="pointer-events-none"
        >
          <div className="flex items-center justify-center h-full">
            {isEditing ? (
              <div className="bg-white border border-gray-200 rounded-lg px-2 py-1 shadow-lg">
                <Input
                  ref={inputRef}
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  onBlur={handleLabelSave}
                  className="h-6 text-xs border-none p-0 focus:ring-0"
                  autoFocus
                />
              </div>
            ) : (
              <div
                className={cn(
                  'bg-white border border-gray-200 rounded-lg px-2 py-1 shadow-lg cursor-pointer',
                  'hover:border-blue-500 hover:shadow-md transition-all duration-200',
                  'flex items-center gap-1 text-xs font-medium'
                )}
                onClick={handleLabelClick}
              >
                {getEdgeIcon()}
                <span className="truncate">{data.label}</span>
                {data?.type === 'conditional' && (
                  <Badge variant="outline" className="ml-1 text-xs">
                    {data.condition}
                  </Badge>
                )}
              </div>
            )}
          </div>
        </foreignObject>
      )}

      {/* Edge Context Menu */}
      {isHovered && (
        <foreignObject
          width={40}
          height={40}
          x={(sourceX + targetX) / 2 + 70}
          y={(sourceY + targetY) / 2 - 20}
          className="pointer-events-auto"
        >
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                size="sm"
                variant="ghost"
                className="h-8 w-8 p-0 bg-white border border-gray-200 shadow-lg hover:bg-gray-50"
              >
                <MoreHorizontal className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={handleLabelClick}>
                <Edit className="w-4 h-4 mr-2" />
                Rename
              </DropdownMenuItem>
              <DropdownMenuItem>
                <GitBranch className="w-4 h-4 mr-2" />
                Add Condition
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Copy className="w-4 h-4 mr-2" />
                Duplicate
              </DropdownMenuItem>
              <DropdownMenuItem className="text-red-600">
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </foreignObject>
      )}

      {/* Error Tooltip */}
      {data?.type === 'error' && data?.errorMessage && (
        <foreignObject
          width={200}
          height={60}
          x={(sourceX + targetX) / 2 - 100}
          y={(sourceY + targetY) / 2 + 30}
          className="pointer-events-none"
        >
          <Popover>
            <PopoverTrigger asChild>
              <div className="bg-red-50 border border-red-200 rounded-lg px-2 py-1 text-xs text-red-700 cursor-help">
                ⚠️ Type mismatch
              </div>
            </PopoverTrigger>
            <PopoverContent className="w-80">
              <div className="space-y-2">
                <h4 className="font-medium text-red-700">Connection Error</h4>
                <p className="text-sm text-gray-600">{data.errorMessage}</p>
                <Button size="sm" className="w-full">
                  Auto-add Transform
                </Button>
              </div>
            </PopoverContent>
          </Popover>
        </foreignObject>
      )}

      {/* Edge Arrow */}
      <defs>
        <marker
          id={`arrow-${id}`}
          viewBox="0 0 10 10"
          refX="5"
          refY="5"
          markerWidth="6"
          markerHeight="6"
          orient="auto-start-reverse"
        >
          <path
            d="M 0 0 L 10 5 L 0 10 z"
            fill={getEdgeColor()}
          />
        </marker>
      </defs>
    </>
  );
};
