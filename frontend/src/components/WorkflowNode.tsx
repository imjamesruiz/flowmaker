import React, { memo } from 'react'
import { Handle, Position, NodeProps } from 'reactflow'
import { NodeModel } from '@/types/graph'

interface WorkflowNodeData {
  node: NodeModel
  issues: string[]
  isSelected: boolean
}

const WorkflowNode: React.FC<NodeProps<WorkflowNodeData>> = ({ data, selected }) => {
  const { node, issues, isSelected } = data
  const hasIssues = issues.length > 0

  return (
    <div
      className={`
        relative bg-white border-2 rounded-lg p-4 min-w-[200px] shadow-lg
        ${isSelected ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-300'}
        ${hasIssues ? 'border-red-500' : ''}
      `}
    >
      {/* Issue badge */}
      {hasIssues && (
        <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center">
          !
        </div>
      )}

      {/* Node header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          {/* Integration Icon */}
          {node.params?.icon && (
            <div 
              className="w-6 h-6 rounded-lg flex items-center justify-center text-sm"
              style={{ backgroundColor: node.params.icon.bgColor.replace('bg-', '').replace('-50', '') + '20' }}
            >
              <span style={{ color: node.params.icon.color.replace('text-', '').replace('-600', '') }}>
                {node.params.icon.name}
              </span>
            </div>
          )}
          <h3 className="font-semibold text-gray-900 text-sm">{node.label}</h3>
        </div>
        <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded">
          {node.type}
        </span>
      </div>

      {/* Input ports */}
      <div className="space-y-2 mb-3">
        {node.ports.in.map((port) => (
          <div key={port.id} className="flex items-center">
            <Handle
              type="target"
              position={Position.Left}
              id={port.id}
              className={`
                w-3 h-3 border-2 border-white
                ${port.required ? 'bg-red-400' : 'bg-gray-400'}
                ${port.multi ? 'ring-2 ring-blue-300' : ''}
              `}
            />
            <div className="ml-2 flex-1">
              <span className="text-xs font-medium text-gray-700">{port.id}</span>
              <div className="flex items-center space-x-1">
                <span className="text-xs text-gray-500">{port.dtype}</span>
                {port.required && (
                  <span className="text-xs text-red-500">*</span>
                )}
                {port.multi && (
                  <span className="text-xs text-blue-500">[multi]</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Output ports */}
      <div className="space-y-2">
        {node.ports.out.map((port) => (
          <div key={port.id} className="flex items-center justify-end">
            <div className="mr-2 flex-1 text-right">
              <span className="text-xs font-medium text-gray-700">{port.id}</span>
              <div className="flex items-center justify-end space-x-1">
                <span className="text-xs text-gray-500">{port.dtype}</span>
                {port.required && (
                  <span className="text-xs text-red-500">*</span>
                )}
                {port.multi && (
                  <span className="text-xs text-blue-500">[multi]</span>
                )}
              </div>
            </div>
            <Handle
              type="source"
              position={Position.Right}
              id={port.id}
              className="w-3 h-3 border-2 border-white bg-green-400"
            />
          </div>
        ))}
      </div>

      {/* Issue tooltip */}
      {hasIssues && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-red-50 border border-red-200 rounded p-2 z-10">
          <div className="text-xs text-red-800">
            {issues.map((issue, index) => (
              <div key={index} className="mb-1">
                • {issue}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default memo(WorkflowNode)
