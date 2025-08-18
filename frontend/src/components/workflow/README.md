# Workflow Canvas Implementation

This directory contains the enhanced workflow canvas implementation with drawing/connection mode, validation, and undo/redo functionality.

## Features

### ✅ Implemented

- **Graph Schema**: Type-safe workflow definition with ports and data types
- **Connection Mode**: Drag and drop connections between compatible ports
- **Validation**: Real-time validation with visual feedback
- **Undo/Redo**: History management with keyboard shortcuts
- **Mock API**: localStorage-based persistence for development
- **Simulation**: Mock workflow execution with trace visualization
- **Keyboard Shortcuts**: Delete/Backspace, Ctrl+Z/Ctrl+Shift+Z, Ctrl+S

### 🎯 Core Components

1. **Graph Types** (`src/types/graph.ts`)
   - `DType`: 'event' | 'json' | 'text' | 'any'
   - `Port`: Input/output ports with type and capacity constraints
   - `NodeModel`: Nodes with ports and parameters
   - `EdgeModel`: Connections between ports
   - `Workflow`: Complete workflow definition

2. **Validation** (`src/utils/validation.ts`)
   - `isValidConnection()`: Connection validation rules
   - `validateGraph()`: Graph-wide validation
   - Type matching and capacity checking

3. **State Management** (`src/store/workflowStore.ts`)
   - Zustand store with undo/redo
   - Node and edge management
   - Validation state tracking

4. **Canvas** (`src/components/WorkflowCanvas.tsx`)
   - React Flow integration
   - Connection handling
   - Keyboard shortcuts
   - Toolbar with Save/Validate/Simulate

5. **Custom Node** (`src/components/WorkflowNode.tsx`)
   - Port visualization
   - Issue badges
   - Type indicators

## Usage

### Basic Setup

```tsx
import { WorkflowCanvasWrapper } from '@/components/WorkflowCanvas'

function App() {
  return (
    <WorkflowCanvasWrapper workflowId="my-workflow" />
  )
}
```

### Adding Nodes

```tsx
const { addNode } = useWorkflowStore()

// Add a trigger node
addNode('trigger', { x: 100, y: 100 })

// Add an action node
addNode('action', { x: 300, y: 100 })
```

### Validation

```tsx
const { validateGraph, issues } = useWorkflowStore()

// Manual validation
validateGraph()

// Check issues for a specific node
const nodeIssues = issues['node-id']
```

### Undo/Redo

```tsx
const { undo, redo } = useWorkflowStore()

// Keyboard shortcuts: Ctrl+Z, Ctrl+Shift+Z
// Or programmatically:
undo()
redo()
```

## Connection Rules

1. **No self-loops**: Cannot connect a node to itself
2. **No duplicates**: Cannot create identical connections
3. **Type matching**: Source dtype must match target dtype (or target is 'any')
4. **Capacity limits**: Non-multi ports can only have one connection

## Node Types

- **trigger**: No inputs, event output
- **action**: Any input, json output
- **condition**: Any input, true/false outputs
- **transformer**: Any input, json output
- **webhook**: Any input, json output

## Development

### Adding New Node Types

1. Update `getDefaultPorts()` in `workflowStore.ts`
2. Update `getDefaultParams()` in `workflowStore.ts`
3. Add validation rules in `validation.ts`

### Custom Validation

```tsx
// Add custom validation rules
function customValidation(workflow: Workflow): ValidationIssues {
  const issues: ValidationIssues = {}
  
  // Your validation logic here
  
  return issues
}
```

### Mock API Extension

```tsx
// Add new endpoints in mocks/workflows.ts
export const workflowAPI = {
  // ... existing endpoints
  
  newEndpoint: async (id: string) => {
    // Implementation
  }
}
```

## Testing

Run the validation tests:

```bash
npm test src/utils/validation.test.ts
```

## Keyboard Shortcuts

- `Delete` / `Backspace`: Remove selected node/edge
- `Ctrl+Z`: Undo
- `Ctrl+Shift+Z`: Redo
- `Ctrl+S`: Save workflow

## Future Enhancements

- [ ] Edge context menu
- [ ] Port tooltips
- [ ] Node parameter editing
- [ ] Workflow templates
- [ ] Export/import functionality
- [ ] Real backend integration
