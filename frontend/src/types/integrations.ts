// Integration Types and Schemas
export interface IntegrationIcon {
  name: string
  color: string
  bgColor: string
}

export interface IntegrationCategory {
  id: string
  name: string
  icon: string
  color: string
}

export interface FieldSchema {
  id: string
  type: 'text' | 'email' | 'password' | 'number' | 'boolean' | 'select' | 'multiselect' | 'textarea' | 'oauth' | 'url'
  label: string
  description?: string
  required?: boolean
  placeholder?: string
  options?: { value: string; label: string }[]
  validation?: {
    min?: number
    max?: number
    pattern?: string
    message?: string
  }
  defaultValue?: any
}

export interface TriggerSchema {
  id: string
  name: string
  description: string
  icon: string
  fields: FieldSchema[]
  outputSchema: {
    type: string
    properties: Record<string, any>
  }
}

export interface ActionSchema {
  id: string
  name: string
  description: string
  icon: string
  fields: FieldSchema[]
  inputSchema: {
    type: string
    properties: Record<string, any>
  }
}

export interface Integration {
  id: string
  name: string
  description: string
  category: string
  icon: IntegrationIcon
  authType: 'oauth' | 'api_key' | 'basic' | 'none'
  triggers: TriggerSchema[]
  actions: ActionSchema[]
  isPopular?: boolean
  isNew?: boolean
}

// Predefined categories
export const INTEGRATION_CATEGORIES: IntegrationCategory[] = [
  { id: 'communication', name: 'Communication', icon: '💬', color: 'blue' },
  { id: 'productivity', name: 'Productivity', icon: '📊', color: 'green' },
  { id: 'development', name: 'Development', icon: '⚡', color: 'purple' },
  { id: 'marketing', name: 'Marketing', icon: '📈', color: 'orange' },
  { id: 'data', name: 'Data & Analytics', icon: '📋', color: 'indigo' },
  { id: 'social', name: 'Social Media', icon: '🌐', color: 'pink' },
  { id: 'other', name: 'Other', icon: '🔧', color: 'gray' }
]

// Integration definitions
export const INTEGRATIONS: Integration[] = [
  {
    id: 'gmail',
    name: 'Gmail',
    description: 'Send and receive emails, manage labels and threads',
    category: 'communication',
    icon: { name: '📧', color: 'text-red-600', bgColor: 'bg-red-50' },
    authType: 'oauth',
    isPopular: true,
    triggers: [
      {
        id: 'new_email',
        name: 'New Email Received',
        description: 'Trigger when a new email is received',
        icon: '📨',
        fields: [
          {
            id: 'label',
            type: 'select',
            label: 'Label to Monitor',
            description: 'Choose which Gmail label to monitor',
            required: true,
            options: [
              { value: 'INBOX', label: 'Inbox' },
              { value: 'UNREAD', label: 'Unread' },
              { value: 'STARRED', label: 'Starred' },
              { value: 'IMPORTANT', label: 'Important' }
            ],
            defaultValue: 'INBOX'
          },
          {
            id: 'from_filter',
            type: 'text',
            label: 'From Filter (Optional)',
            description: 'Only trigger for emails from specific sender',
            placeholder: 'example@gmail.com'
          }
        ],
        outputSchema: {
          type: 'object',
          properties: {
            subject: { type: 'string' },
            from: { type: 'string' },
            body: { type: 'string' },
            date: { type: 'string' },
            threadId: { type: 'string' }
          }
        }
      }
    ],
    actions: [
      {
        id: 'send_email',
        name: 'Send Email',
        description: 'Send an email via Gmail',
        icon: '📤',
        fields: [
          {
            id: 'to',
            type: 'email',
            label: 'To',
            description: 'Recipient email address',
            required: true,
            placeholder: 'recipient@example.com'
          },
          {
            id: 'subject',
            type: 'text',
            label: 'Subject',
            description: 'Email subject line',
            required: true,
            placeholder: 'Your email subject'
          },
          {
            id: 'body',
            type: 'textarea',
            label: 'Message Body',
            description: 'Email content',
            required: true,
            placeholder: 'Your message here...'
          },
          {
            id: 'is_html',
            type: 'boolean',
            label: 'HTML Format',
            description: 'Send as HTML email',
            defaultValue: false
          }
        ],
        inputSchema: {
          type: 'object',
          properties: {
            to: { type: 'string' },
            subject: { type: 'string' },
            body: { type: 'string' }
          }
        }
      }
    ]
  },
  {
    id: 'slack',
    name: 'Slack',
    description: 'Send messages, create channels, and manage team communication',
    category: 'communication',
    icon: { name: '💬', color: 'text-purple-600', bgColor: 'bg-purple-50' },
    authType: 'oauth',
    isPopular: true,
    triggers: [
      {
        id: 'new_message',
        name: 'New Message',
        description: 'Trigger when a new message is posted',
        icon: '💬',
        fields: [
          {
            id: 'channel',
            type: 'select',
            label: 'Channel',
            description: 'Channel to monitor for messages',
            required: true,
            options: [
              { value: 'general', label: '#general' },
              { value: 'random', label: '#random' }
            ]
          }
        ],
        outputSchema: {
          type: 'object',
          properties: {
            text: { type: 'string' },
            user: { type: 'string' },
            channel: { type: 'string' },
            timestamp: { type: 'string' }
          }
        }
      }
    ],
    actions: [
      {
        id: 'send_message',
        name: 'Send Message',
        description: 'Send a message to a Slack channel',
        icon: '📤',
        fields: [
          {
            id: 'channel',
            type: 'text',
            label: 'Channel',
            description: 'Channel name or ID',
            required: true,
            placeholder: '#general'
          },
          {
            id: 'message',
            type: 'textarea',
            label: 'Message',
            description: 'Message content',
            required: true,
            placeholder: 'Your message here...'
          },
          {
            id: 'username',
            type: 'text',
            label: 'Username (Optional)',
            description: 'Custom username for the bot',
            placeholder: 'Workflow Bot'
          }
        ],
        inputSchema: {
          type: 'object',
          properties: {
            channel: { type: 'string' },
            message: { type: 'string' }
          }
        }
      }
    ]
  },
  {
    id: 'google_sheets',
    name: 'Google Sheets',
    description: 'Read and write data to Google Sheets',
    category: 'productivity',
    icon: { name: '📊', color: 'text-green-600', bgColor: 'bg-green-50' },
    authType: 'oauth',
    isPopular: true,
    triggers: [
      {
        id: 'row_added',
        name: 'New Row Added',
        description: 'Trigger when a new row is added to a sheet',
        icon: '➕',
        fields: [
          {
            id: 'spreadsheet_id',
            type: 'text',
            label: 'Spreadsheet ID',
            description: 'The ID of the Google Spreadsheet',
            required: true,
            placeholder: '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
          },
          {
            id: 'sheet_name',
            type: 'text',
            label: 'Sheet Name',
            description: 'Name of the specific sheet',
            required: true,
            placeholder: 'Sheet1'
          }
        ],
        outputSchema: {
          type: 'object',
          properties: {
            row: { type: 'array' },
            rowNumber: { type: 'number' },
            values: { type: 'object' }
          }
        }
      }
    ],
    actions: [
      {
        id: 'add_row',
        name: 'Add Row',
        description: 'Add a new row to a Google Sheet',
        icon: '➕',
        fields: [
          {
            id: 'spreadsheet_id',
            type: 'text',
            label: 'Spreadsheet ID',
            description: 'The ID of the Google Spreadsheet',
            required: true,
            placeholder: '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
          },
          {
            id: 'sheet_name',
            type: 'text',
            label: 'Sheet Name',
            description: 'Name of the specific sheet',
            required: true,
            placeholder: 'Sheet1'
          },
          {
            id: 'values',
            type: 'textarea',
            label: 'Row Values',
            description: 'Comma-separated values for the new row',
            required: true,
            placeholder: 'Value1,Value2,Value3'
          }
        ],
        inputSchema: {
          type: 'object',
          properties: {
            spreadsheet_id: { type: 'string' },
            sheet_name: { type: 'string' },
            values: { type: 'string' }
          }
        }
      }
    ]
  },
  {
    id: 'webhook',
    name: 'Webhook',
    description: 'Send and receive HTTP requests',
    category: 'development',
    icon: { name: '🔗', color: 'text-blue-600', bgColor: 'bg-blue-50' },
    authType: 'none',
    triggers: [
      {
        id: 'http_request',
        name: 'HTTP Request Received',
        description: 'Trigger when an HTTP request is received',
        icon: '🌐',
        fields: [
          {
            id: 'method',
            type: 'select',
            label: 'HTTP Method',
            description: 'Allowed HTTP methods',
            required: true,
            options: [
              { value: 'GET', label: 'GET' },
              { value: 'POST', label: 'POST' },
              { value: 'PUT', label: 'PUT' },
              { value: 'DELETE', label: 'DELETE' }
            ],
            defaultValue: 'POST'
          },
          {
            id: 'path',
            type: 'text',
            label: 'Path (Optional)',
            description: 'Specific path to match',
            placeholder: '/webhook'
          }
        ],
        outputSchema: {
          type: 'object',
          properties: {
            method: { type: 'string' },
            headers: { type: 'object' },
            body: { type: 'string' },
            query: { type: 'object' },
            path: { type: 'string' }
          }
        }
      }
    ],
    actions: [
      {
        id: 'http_request',
        name: 'HTTP Request',
        description: 'Make an HTTP request to any URL',
        icon: '🌐',
        fields: [
          {
            id: 'url',
            type: 'url',
            label: 'URL',
            description: 'The URL to make the request to',
            required: true,
            placeholder: 'https://api.example.com/endpoint'
          },
          {
            id: 'method',
            type: 'select',
            label: 'HTTP Method',
            description: 'HTTP method to use',
            required: true,
            options: [
              { value: 'GET', label: 'GET' },
              { value: 'POST', label: 'POST' },
              { value: 'PUT', label: 'PUT' },
              { value: 'DELETE', label: 'DELETE' }
            ],
            defaultValue: 'POST'
          },
          {
            id: 'headers',
            type: 'textarea',
            label: 'Headers (Optional)',
            description: 'JSON object of headers',
            placeholder: '{"Content-Type": "application/json"}'
          },
          {
            id: 'body',
            type: 'textarea',
            label: 'Request Body (Optional)',
            description: 'Request body content',
            placeholder: '{"key": "value"}'
          }
        ],
        inputSchema: {
          type: 'object',
          properties: {
            url: { type: 'string' },
            method: { type: 'string' },
            headers: { type: 'object' },
            body: { type: 'string' }
          }
        }
      }
    ]
  },
  {
    id: 'schedule',
    name: 'Schedule',
    description: 'Trigger workflows on a schedule',
    category: 'other',
    icon: { name: '⏰', color: 'text-yellow-600', bgColor: 'bg-yellow-50' },
    authType: 'none',
    triggers: [
      {
        id: 'cron',
        name: 'Scheduled Trigger',
        description: 'Trigger on a cron schedule',
        icon: '⏰',
        fields: [
          {
            id: 'cron_expression',
            type: 'text',
            label: 'Cron Expression',
            description: 'Cron expression for scheduling',
            required: true,
            placeholder: '0 9 * * MON-FRI',
            validation: {
              pattern: '^[0-9\\*\\,\\-\\/\\s]+$',
              message: 'Invalid cron expression'
            }
          },
          {
            id: 'timezone',
            type: 'select',
            label: 'Timezone',
            description: 'Timezone for the schedule',
            required: true,
            options: [
              { value: 'UTC', label: 'UTC' },
              { value: 'America/New_York', label: 'Eastern Time' },
              { value: 'America/Chicago', label: 'Central Time' },
              { value: 'America/Denver', label: 'Mountain Time' },
              { value: 'America/Los_Angeles', label: 'Pacific Time' },
              { value: 'Europe/London', label: 'London' },
              { value: 'Europe/Paris', label: 'Paris' },
              { value: 'Asia/Tokyo', label: 'Tokyo' }
            ],
            defaultValue: 'UTC'
          }
        ],
        outputSchema: {
          type: 'object',
          properties: {
            timestamp: { type: 'string' },
            timezone: { type: 'string' },
            cronExpression: { type: 'string' }
          }
        }
      }
    ],
    actions: []
  }
]

// Helper functions
export function getIntegrationsByCategory(categoryId: string): Integration[] {
  return INTEGRATIONS.filter(integration => integration.category === categoryId)
}

export function getPopularIntegrations(): Integration[] {
  return INTEGRATIONS.filter(integration => integration.isPopular)
}

export function getNewIntegrations(): Integration[] {
  return INTEGRATIONS.filter(integration => integration.isNew)
}

export function searchIntegrations(query: string): Integration[] {
  const lowercaseQuery = query.toLowerCase()
  return INTEGRATIONS.filter(integration => 
    integration.name.toLowerCase().includes(lowercaseQuery) ||
    integration.description.toLowerCase().includes(lowercaseQuery) ||
    integration.triggers.some(trigger => 
      trigger.name.toLowerCase().includes(lowercaseQuery) ||
      trigger.description.toLowerCase().includes(lowercaseQuery)
    ) ||
    integration.actions.some(action => 
      action.name.toLowerCase().includes(lowercaseQuery) ||
      action.description.toLowerCase().includes(lowercaseQuery)
    )
  )
}

export function getIntegrationById(id: string): Integration | undefined {
  return INTEGRATIONS.find(integration => integration.id === id)
}

export function getTriggerById(integrationId: string, triggerId: string): TriggerSchema | undefined {
  const integration = getIntegrationById(integrationId)
  return integration?.triggers.find(trigger => trigger.id === triggerId)
}

export function getActionById(integrationId: string, actionId: string): ActionSchema | undefined {
  const integration = getIntegrationById(integrationId)
  return integration?.actions.find(action => action.id === actionId)
}
