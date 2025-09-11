# Trigger & Action Creation System

This directory contains the new trigger and action creation interface for FlowMaker, providing a modern, user-friendly way to add integrations to workflows.

## Components Overview

### Core Components

1. **TriggerActionModal.vue** - Main modal for selecting triggers and actions
2. **IntegrationList.vue** - Displays available integrations with expandable sections
3. **ConfigurationPanel.vue** - Side panel for configuring selected triggers/actions
4. **SchemaForm.vue** - Dynamic form generator based on field schemas
5. **TriggerActionManager.vue** - Main orchestrator component

### Supporting Files

- **types/integrations.ts** - Type definitions and integration schemas
- **store/workflowStore.ts** - Updated with new node creation methods

## Features

### 🎯 Trigger/Action Selection
- **Searchable Integration List**: Find integrations quickly with real-time search
- **Category Filtering**: Browse by categories (Communication, Productivity, etc.)
- **Popular/New Badges**: Highlight trending and new integrations
- **Expandable Cards**: Clean, organized display of available options

### ⚙️ Dynamic Configuration
- **Schema-Driven Forms**: Automatically generated forms based on integration schemas
- **Multiple Field Types**: Support for text, email, password, number, boolean, select, multiselect, textarea, OAuth, and URL fields
- **Real-time Validation**: Instant feedback on form validation
- **Default Values**: Smart defaults for all field types

### 🎨 Modern UI/UX
- **Smooth Animations**: Framer Motion-style transitions throughout
- **Clean Design**: Modern Tailwind styling with rounded corners and subtle shadows
- **Responsive Layout**: Works on all screen sizes
- **Accessibility**: Proper ARIA labels and keyboard navigation

### 🔧 Integration Support
- **OAuth Authentication**: Built-in OAuth connection management
- **API Key Support**: Secure API key handling
- **No-Auth Integrations**: Support for webhooks and other no-auth services
- **Custom Icons**: Branded icons for each integration

## Usage

### Basic Implementation

```vue
<template>
  <TriggerActionManager />
</template>

<script setup>
import TriggerActionManager from '@/components/TriggerActionManager.vue'
</script>
```

### Advanced Usage with Custom Handlers

```vue
<template>
  <div>
    <TriggerActionModal
      :is-open="showModal"
      mode="trigger"
      @close="showModal = false"
      @select-trigger="handleTriggerSelect"
    />
    
    <ConfigurationPanel
      :is-open="showConfig"
      :integration="selectedIntegration"
      :selected-item="selectedTrigger"
      @submit="handleConfigSubmit"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useWorkflowStore } from '@/store/workflowStore'

const { addIntegrationNode } = useWorkflowStore()

const handleTriggerSelect = (integration, trigger) => {
  // Handle trigger selection
}

const handleConfigSubmit = (config) => {
  // Add node to workflow
  addIntegrationNode(integration, trigger, config, { x: 100, y: 100 })
}
</script>
```

## Integration Schema

### Adding New Integrations

To add a new integration, update the `INTEGRATIONS` array in `types/integrations.ts`:

```typescript
{
  id: 'my_integration',
  name: 'My Integration',
  description: 'Description of what this integration does',
  category: 'productivity',
  icon: { name: '🔧', color: 'text-blue-600', bgColor: 'bg-blue-50' },
  authType: 'oauth',
  isPopular: true,
  triggers: [
    {
      id: 'new_item',
      name: 'New Item',
      description: 'Trigger when a new item is created',
      icon: '📝',
      fields: [
        {
          id: 'webhook_url',
          type: 'url',
          label: 'Webhook URL',
          description: 'URL to receive notifications',
          required: true,
          placeholder: 'https://example.com/webhook'
        }
      ],
      outputSchema: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          name: { type: 'string' },
          created_at: { type: 'string' }
        }
      }
    }
  ],
  actions: [
    {
      id: 'create_item',
      name: 'Create Item',
      description: 'Create a new item',
      icon: '➕',
      fields: [
        {
          id: 'name',
          type: 'text',
          label: 'Item Name',
          required: true,
          placeholder: 'Enter item name'
        }
      ],
      inputSchema: {
        type: 'object',
        properties: {
          name: { type: 'string' }
        }
      }
    }
  ]
}
```

### Field Types

The system supports the following field types:

- **text**: Basic text input
- **email**: Email input with validation
- **password**: Password input with show/hide toggle
- **number**: Numeric input with min/max validation
- **boolean**: Checkbox input
- **select**: Dropdown selection
- **multiselect**: Multiple checkbox selection
- **textarea**: Multi-line text input
- **oauth**: OAuth connection selector
- **url**: URL input with validation

## Styling

The components use Tailwind CSS with custom design tokens:

- **Colors**: Indigo primary, green for triggers, blue for actions
- **Spacing**: Consistent 4px grid system
- **Shadows**: Subtle shadows for depth
- **Border Radius**: 8px (rounded-lg) for cards, 12px (rounded-xl) for modals
- **Transitions**: 200ms ease-in-out for all interactions

## Testing

Visit `/demo/trigger-action` to test the complete trigger/action creation flow.

## Future Enhancements

- [ ] Integration marketplace
- [ ] Custom field types
- [ ] Advanced validation rules
- [ ] Integration testing
- [ ] Bulk operations
- [ ] Integration analytics
