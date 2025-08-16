import React from 'react'
import { Handle, Position, NodeProps } from 'reactflow'
import { NodeKind } from '@/types/workflow'

interface NodeCardData {
  name: string
  config?: any
  ports?: {
    in?: string[]
    out?: string[]
  }
}

const getNodeColor = (type: NodeKind): string => {
  const colorMap: Record<NodeKind, string> = {
    trigger: '#10B981',
    action: '#3B82F6',
    condition: '#F59E0B',
    transformer: '#8B5CF6',
    webhook: '#EF4444'
  }
  return colorMap[type] || '#6B7280'
}

const getNodeIcon = (type: NodeKind): string => {
  const iconMap: Record<NodeKind, string> = {
    trigger: '⚡',
    action: '⚙️',
    condition: '❓',
    transformer: '🔄',
    webhook: '🌐'
  }
  return iconMap[type] || '📦'
}

export const NodeCard: React.FC<NodeProps<NodeCardData>> = ({ 
  id, 
  type, 
  data, 
  selected 
}) => {
  const nodeType = type as NodeKind
  const color = getNodeColor(nodeType)
  const icon = getNodeIcon(nodeType)

  return (
    <div
      className={`
        relative bg-white border-2 rounded-lg p-4 min-w-[200px] shadow-lg
        ${selected ? 'ring-2 ring-blue-500' : ''}
        hover:shadow-xl transition-all duration-200
      `}
      style={{ borderColor: color }}
    >
      {/* Input Handles */}
      {data.ports?.in && data.ports.in.length > 0 ? (
        data.ports.in.map((portId) => (
          <Handle
            key={`in-${portId}`}
            type="target"
            position={Position.Left}
            id={portId}
            className="w-6 h-6 bg-gray-400 border-2 border-white hover:bg-gray-500 transition-colors"
            style={{ 
              top: '50%', 
              transform: 'translateY(-50%)',
              left: '-12px'
            }}
          />
        ))
      ) : (
        // Default input handle for most nodes
        <Handle
          type="target"
          position={Position.Left}
          id="in"
          className="w-6 h-6 bg-gray-400 border-2 border-white hover:bg-gray-500 transition-colors"
          style={{ 
            top: '50%', 
            transform: 'translateY(-50%)',
            left: '-12px'
          }}
        />
      )}

      {/* Node Content */}
      <div className="flex items-center gap-2 mb-2">
        <span className="text-lg">{icon}</span>
        <span className="font-semibold text-gray-800 capitalize">
          {nodeType}
        </span>
      </div>
      
      <div className="text-sm text-gray-600 mb-2">
        {data.name}
      </div>

      {/* Node Status */}
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
        <span className="text-xs text-gray-500">Idle</span>
      </div>

      {/* Output Handles */}
      {nodeType === 'condition' ? (
        // Condition nodes have true/false outputs
        <div className="absolute right-0 top-1/2 transform -translate-y-1/2 flex flex-col gap-2">
          <Handle
            type="source"
            position={Position.Right}
            id="true"
            className="w-6 h-6 bg-green-500 border-2 border-white hover:bg-green-600 transition-colors"
            style={{ 
              top: '0',
              right: '-12px'
            }}
          />
          <Handle
            type="source"
            position={Position.Right}
            id="false"
            className="w-6 h-6 bg-red-500 border-2 border-white hover:bg-red-600 transition-colors"
            style={{ 
              top: '20px',
              right: '-12px'
            }}
          />
        </div>
      ) : data.ports?.out && data.ports.out.length > 0 ? (
        // Custom output ports
        data.ports.out.map((portId) => (
          <Handle
            key={`out-${portId}`}
            type="source"
            position={Position.Right}
            id={portId}
            className="w-6 h-6 bg-gray-400 border-2 border-white hover:bg-gray-500 transition-colors"
            style={{ 
              top: '50%', 
              transform: 'translateY(-50%)',
              right: '-12px'
            }}
          />
        ))
      ) : (
        // Default output handle
        <Handle
          type="source"
          position={Position.Right}
          id="out"
          className="w-6 h-6 bg-gray-400 border-2 border-white hover:bg-gray-500 transition-colors"
          style={{ 
            top: '50%', 
            transform: 'translateY(-50%)',
            right: '-12px'
          }}
        />
      )}

      {/* Node Actions (shown on hover/select) */}
      {selected && (
        <div className="absolute -top-8 left-0 right-0 flex justify-center gap-1">
          <button
            className="w-6 h-6 bg-blue-500 text-white rounded text-xs hover:bg-blue-600 transition-colors"
            title="Configure"
          >
            ⚙️
          </button>
          <button
            className="w-6 h-6 bg-green-500 text-white rounded text-xs hover:bg-green-600 transition-colors"
            title="Duplicate"
          >
            📋
          </button>
          <button
            className="w-6 h-6 bg-red-500 text-white rounded text-xs hover:bg-red-600 transition-colors"
            title="Delete"
          >
            🗑️
          </button>
        </div>
      )}
    </div>
  )
}
