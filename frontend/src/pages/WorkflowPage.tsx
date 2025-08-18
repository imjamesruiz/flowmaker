import React from 'react'
import { WorkflowCanvasWrapper } from '@/components/WorkflowCanvas'

interface WorkflowPageProps {
  workflowId?: string
}

const WorkflowPage: React.FC<WorkflowPageProps> = ({ workflowId = 'default-workflow' }) => {
  return (
    <div className="h-screen w-full bg-gray-50">
      <div className="h-full">
        <WorkflowCanvasWrapper workflowId={workflowId} />
      </div>
    </div>
  )
}

export default WorkflowPage
