# Workflow Builder Components

A comprehensive drag-and-drop workflow builder with a modern design system, built with Vue 3 and TypeScript.

## 🎨 Design System

### Color Palette
- **Primary**: #6C5CE7 (Worqly Purple)
- **Surface**: #0B0D12 (dark) / #F8FAFC (light)
- **Node Types**:
  - Trigger: #2ECC71
  - Action: #377DFF
  - Condition: #F4D03F
  - Transformer: #8E44AD
  - Webhook: #E74C3C

### Design Tokens
All design tokens are defined in `@/assets/workflow-tokens.css`:
- Spacing: 12/16/24 grid system
- Border radius: 16px (nodes), 8px (chips)
- Shadows: sm/md/lg with low opacity
- Transitions: 150-200ms ease
- Focus rings: ring-2 ring-purple-400/60

## 🧩 Components

### CanvasShell.vue
The main canvas container with grid, minimap, and controls.

**Features:**
- Grid background with snap guides
- Zoom controls (in/out/reset/fit)
- MiniMap with viewport indicator
- Auto-pan when dragging near edges
- Keyboard shortcuts (Space = pan, Esc = cancel)
- Empty state with quick-add buttons

**Props:**
```typescript
interface CanvasShellProps {
  theme: 'light' | 'dark'
  showMinimap: boolean
  nodeCount: number
  edgeCount: number
  showEmptyState: boolean
}
```

**Events:**
- `canvas-click`: Canvas background click
- `canvas-context-menu`: Right-click on canvas
- `zoom-change`: Zoom level changed
- `pan-change`: Pan position changed
- `node-drop`: Node dropped on canvas
- `quick-node-add`: Quick node button clicked

### NodeCard.vue
Individual workflow nodes with ports and interactions.

**Features:**
- Rounded corners (16px) with soft shadows
- Gradient backgrounds by node type
- Input/output ports with tooltips
- Hover and selection states
- Context menu actions (configure, duplicate, delete)
- Keyboard navigation support
- Springy drop animations

**Props:**
```typescript
interface NodeCardProps {
  id: string
  data: {
    label: string
    type: 'trigger' | 'action' | 'condition' | 'transformer' | 'webhook'
    status: 'idle' | 'running' | 'success' | 'error'
    inputs: HandleData[]
    outputs: HandleData[]
    description?: string
  }
  selected: boolean
  dragging: boolean
  isConnecting: boolean
}
```

**Events:**
- `node-click`: Node clicked
- `node-context-menu`: Right-click on node
- `start-connection`: Port connection started
- `configure`: Configure node
- `duplicate`: Duplicate node
- `delete`: Delete node

### Edge.vue
Connection lines between nodes with labels and interactions.

**Features:**
- Orthogonal routing with rounded corners
- Edge labels with condition chips
- Hover effects with glow
- Context menu for edge actions
- Error states with tooltips
- Arrow markers

**Props:**
```typescript
interface EdgeProps {
  id: string
  sourceX: number
  sourceY: number
  targetX: number
  targetY: number
  sourcePosition: string
  targetPosition: string
  data: {
    label?: string
    condition?: string
    type?: 'default' | 'conditional' | 'error' | 'success'
    errorMessage?: string
  }
  selected: boolean
}
```

**Events:**
- `edge-click`: Edge clicked
- `edge-context-menu`: Right-click on edge
- `edge-label-edit`: Edit edge label
- `edge-rename`: Rename edge
- `edge-delete`: Delete edge

## 🎯 Interaction Model

### Drag & Drop
1. **Drag from palette**: Drag node types to canvas
2. **Auto-snap**: Nodes snap to grid (8px)
3. **Springy drop**: Elastic animation on drop
4. **Magnetic snapping**: Visual guides for alignment

### Connections
1. **Drag-to-connect**: Drag from output port to input port
2. **Click-to-connect**: Click output → wire mode → click input
3. **Visual feedback**: Valid targets glow, invalid show ✕
4. **Auto-reroute**: Edges avoid node overlap

### Keyboard Navigation
- **Tab**: Cycle through nodes and ports
- **Enter**: Start connection or activate
- **Escape**: Cancel current operation
- **Delete/Backspace**: Delete selected items
- **Space**: Toggle pan mode
- **Ctrl/Cmd + A**: Select all
- **Ctrl/Cmd + Z/Y**: Undo/Redo

### Context Menus
**Node Menu:**
- Configure
- Duplicate
- Insert before/after
- Convert type
- Delete

**Edge Menu:**
- Rename
- Add waypoint
- Insert node
- Delete

## 🚀 Usage

### Basic Setup
```vue
<template>
  <CanvasShell
    :theme="theme"
    :show-minimap="true"
    :node-count="nodes.length"
    :edge-count="edges.length"
    @node-drop="handleNodeDrop"
  >
    <NodeCard
      v-for="node in nodes"
      :key="node.id"
      :id="node.id"
      :data="node.data"
      :selected="selectedNode === node.id"
      @node-click="handleNodeClick"
    />
    
    <Edge
      v-for="edge in edges"
      :key="edge.id"
      :id="edge.id"
      :source-x="edge.sourceX"
      :source-y="edge.sourceY"
      :target-x="edge.targetX"
      :target-y="edge.targetY"
      :data="edge.data"
      @edge-click="handleEdgeClick"
    />
  </CanvasShell>
</template>
```

### Node Data Structure
```typescript
const nodeData = {
  label: 'Gmail Trigger',
  type: 'trigger',
  status: 'idle',
  description: 'Triggers when new email arrives',
  inputs: [],
  outputs: [
    {
      id: 'email',
      label: 'Email',
      type: 'object',
      required: false,
      description: 'Email data object'
    }
  ]
}
```

### Edge Data Structure
```typescript
const edgeData = {
  label: 'Email → Filter',
  type: 'default',
  condition: 'True',
  errorMessage: null
}
```

## 🎨 Styling

### CSS Custom Properties
All design tokens are available as CSS custom properties:

```css
.workflow-node {
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-md);
  transition: all var(--transition-normal);
}

.workflow-handle {
  width: var(--handle-size);
  height: var(--handle-size);
  border: var(--handle-border-width) solid var(--color-gray-300);
}
```

### Theme Support
The components support light and dark themes:

```vue
<CanvasShell theme="dark" />
```

### Custom Node Types
Add custom node types by extending the color palette:

```css
.node-custom {
  background: linear-gradient(135deg, #your-color, #your-color-dark);
  border-color: #your-color;
}
```

## 🔧 Configuration

### Grid Settings
```css
:root {
  --grid-size: 8px;
  --grid-major: 32px;
  --grid-color: rgb(156 163 175 / 0.1);
  --grid-major-color: rgb(156 163 175 / 0.2);
}
```

### Animation Settings
```css
:root {
  --transition-fast: 150ms ease;
  --transition-normal: 200ms ease;
  --transition-slow: 300ms ease;
}
```

### Handle Settings
```css
:root {
  --handle-size: 16px;
  --handle-hit-area: 24px;
  --handle-border-width: 2px;
}
```

## ♿ Accessibility

### ARIA Support
- `role="application"` on canvas
- `role="button"` on nodes and ports
- `aria-label` for screen readers
- `tabindex` for keyboard navigation

### Keyboard Navigation
- Tab to cycle through interactive elements
- Enter to activate connections
- Escape to cancel operations
- Arrow keys for fine positioning

### Visual Indicators
- Focus rings on all interactive elements
- High contrast colors for status states
- Non-color cues for states (icons, patterns)

## 🧪 Testing

### Acceptance Criteria
- Time-to-first-connection under 3 seconds
- Mis-connection rate reduced via clear affordances
- Edge labels readable at 50-200% zoom
- Handles accessible via keyboard and screen reader

### Performance
- Smooth 60fps animations
- Efficient rendering with virtual scrolling for large workflows
- Optimized hit detection for ports and edges

## 🔮 Future Enhancements

### Planned Features
- Multi-select with marquee selection
- Undo/Redo system
- Workflow templates
- Advanced routing algorithms
- Real-time collaboration
- Workflow validation
- Export to various formats

### Integration Points
- Backend API for workflow persistence
- Real-time execution status updates
- Integration with external services
- Plugin system for custom node types
