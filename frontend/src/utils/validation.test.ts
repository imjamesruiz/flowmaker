import { isValidConnection, validateGraph } from './validation'
import { Workflow, NodeModel } from '@/types/graph'

// Test data
const createTestWorkflow = (): Workflow => ({
  id: 'test-workflow',
  nodes: [
    {
      id: 'trigger-1',
      type: 'trigger',
      label: 'Trigger 1',
      ports: {
        in: [],
        out: [{ id: 'out', dtype: 'event', required: false }]
      },
      params: { name: 'Test Trigger' }
    },
    {
      id: 'action-1',
      type: 'action',
      label: 'Action 1',
      ports: {
        in: [{ id: 'in', dtype: 'event', required: true }],
        out: [{ id: 'out', dtype: 'json', required: false }]
      },
      params: { name: 'Test Action' }
    }
  ],
  edges: []
})

describe('Validation Functions', () => {
  describe('isValidConnection', () => {
    it('should allow valid connections', () => {
      const workflow = createTestWorkflow()
      const connection = {
        source: 'trigger-1',
        sourceHandle: 'out',
        target: 'action-1',
        targetHandle: 'in'
      }
      
      expect(isValidConnection(connection, workflow)).toBe(true)
    })

    it('should prevent self-loops', () => {
      const workflow = createTestWorkflow()
      const connection = {
        source: 'trigger-1',
        sourceHandle: 'out',
        target: 'trigger-1',
        targetHandle: 'in'
      }
      
      expect(isValidConnection(connection, workflow)).toBe(false)
    })

    it('should prevent type mismatches', () => {
      const workflow = createTestWorkflow()
      // Add a node with incompatible type
      workflow.nodes.push({
        id: 'action-2',
        type: 'action',
        label: 'Action 2',
        ports: {
          in: [{ id: 'in', dtype: 'json', required: true }],
          out: [{ id: 'out', dtype: 'text', required: false }]
        },
        params: { name: 'Test Action 2' }
      })
      
      const connection = {
        source: 'trigger-1',
        sourceHandle: 'out', // dtype: 'event'
        target: 'action-2',
        targetHandle: 'in'   // dtype: 'json'
      }
      
      expect(isValidConnection(connection, workflow)).toBe(false)
    })
  })

  describe('validateGraph', () => {
    it('should detect missing required inputs', () => {
      const workflow = createTestWorkflow()
      const issues = validateGraph(workflow)
      
      expect(issues['action-1']).toContain('Missing required input: in')
    })

    it('should return empty issues for valid workflow', () => {
      const workflow = createTestWorkflow()
      // Add a valid connection
      workflow.edges.push({
        id: 'edge-1',
        from: { node: 'trigger-1', port: 'out' },
        to: { node: 'action-1', port: 'in' }
      })
      
      const issues = validateGraph(workflow)
      expect(issues['action-1']).toHaveLength(0)
    })
  })
})
