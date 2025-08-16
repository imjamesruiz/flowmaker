import React from 'react'
import { NodeKind } from '@/types/workflow'

interface NodeType {
  type: NodeKind
  label: string
  description: string
  icon: string
  color: string
}

const nodeTypes: NodeType[] = [
  {
    type: 'trigger',
    label: 'Trigger',
    description: 'Start workflow execution',
    icon: '⚡',
    color: '#10B981'
  },
  {
    type: 'action',
    label: 'Action',
    description: 'Perform an action',
    icon: '⚙️',
    color: '#3B82F6'
  },
  {
    type: 'condition',
    label: 'Condition',
    description: 'Make decisions',
    icon: '❓',
    color: '#F59E0B'
  },
  {
    type: 'transformer',
    label: 'Transformer',
    description: 'Transform data',
    icon: '🔄',
    color: '#8B5CF6'
  },
  {
    type: 'webhook',
    label: 'Webhook',
    description: 'External trigger',
    icon: '🌐',
    color: '#EF4444'
  }
]

export const NodePalette: React.FC = () => {
  const onDragStart = (event: React.DragEvent, nodeType: NodeKind) => {
    event.dataTransfer.setData('application/reactflow', nodeType)
    event.dataTransfer.effectAllowed = 'move'
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-lg">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Node Types</h3>
      
      <div className="space-y-2">
        {nodeTypes.map((nodeType) => (
          <div
            key={nodeType.type}
            className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-grab active:cursor-grabbing transition-colors"
            draggable
            onDragStart={(event) => onDragStart(event, nodeType.type)}
          >
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center text-white text-lg"
              style={{ backgroundColor: nodeType.color }}
            >
              {nodeType.icon}
            </div>
            
            <div className="flex-1">
              <div className="font-medium text-gray-800">
                {nodeType.label}
              </div>
              <div className="text-sm text-gray-500">
                {nodeType.description}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 text-xs text-gray-500 text-center">
        Drag nodes to the canvas to create connections
      </div>
    </div>
  )
}
