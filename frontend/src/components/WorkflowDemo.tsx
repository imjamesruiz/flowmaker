import React from 'react'
import WorkflowPage from '@/pages/WorkflowPage'

const WorkflowDemo: React.FC = () => {
  return (
    <div className="h-screen w-full">
      <WorkflowPage workflowId="demo-workflow" />
    </div>
  )
}

export default WorkflowDemo
