-- Supabase Database Schema for Flowmaker/Worqly
-- This script sets up all the necessary tables and relationships

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE node_type AS ENUM ('trigger', 'action', 'condition', 'transformer', 'webhook', 'delay', 'loop');
CREATE TYPE connection_type AS ENUM ('data_flow', 'conditional', 'error_handler');
CREATE TYPE execution_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');
CREATE TYPE node_execution_status AS ENUM ('pending', 'running', 'completed', 'failed', 'skipped');

-- Users table (extends Supabase auth.users)
CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255), -- Nullable for OAuth users
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Workflows table
CREATE TABLE public.workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT true,
    is_template BOOLEAN DEFAULT false,
    version INTEGER DEFAULT 1,
    canvas_data JSONB, -- Joint.js canvas data
    settings JSONB, -- Workflow settings
    trigger_config JSONB, -- Trigger configuration
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Integrations table
CREATE TABLE public.integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    provider VARCHAR(100) NOT NULL, -- gmail, slack, sheets, etc.
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    config JSONB, -- Provider-specific configuration
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- OAuth tokens table
CREATE TABLE public.oauth_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    integration_id UUID NOT NULL REFERENCES public.integrations(id) ON DELETE CASCADE,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_type VARCHAR(50) DEFAULT 'Bearer',
    expires_at TIMESTAMPTZ,
    scope TEXT,
    is_valid BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Workflow nodes table
CREATE TABLE public.workflow_nodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID NOT NULL REFERENCES public.workflows(id) ON DELETE CASCADE,
    node_id VARCHAR(255) NOT NULL, -- Joint.js node ID
    node_type node_type NOT NULL,
    name VARCHAR(255) NOT NULL,
    position_x FLOAT NOT NULL,
    position_y FLOAT NOT NULL,
    config JSONB, -- Node configuration
    integration_id UUID REFERENCES public.integrations(id) ON DELETE SET NULL,
    is_enabled BOOLEAN DEFAULT true,
    retry_config JSONB, -- Retry configuration
    timeout_seconds INTEGER DEFAULT 300, -- Node timeout
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Workflow connections table
CREATE TABLE public.workflow_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID NOT NULL REFERENCES public.workflows(id) ON DELETE CASCADE,
    connection_id VARCHAR(255) NOT NULL, -- Joint.js connection ID
    source_node_id VARCHAR(255) NOT NULL,
    target_node_id VARCHAR(255) NOT NULL,
    connection_type connection_type DEFAULT 'data_flow',
    source_port VARCHAR(100),
    target_port VARCHAR(100),
    condition JSONB, -- Conditional logic
    data_mapping JSONB, -- Data transformation mapping
    is_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Workflow triggers table
CREATE TABLE public.workflow_triggers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID NOT NULL REFERENCES public.workflows(id) ON DELETE CASCADE,
    trigger_type VARCHAR(100) NOT NULL, -- webhook, schedule, manual
    config JSONB, -- Trigger-specific configuration
    is_active BOOLEAN DEFAULT true,
    last_triggered TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Workflow executions table
CREATE TABLE public.workflow_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID NOT NULL REFERENCES public.workflows(id) ON DELETE CASCADE,
    execution_id VARCHAR(255) UNIQUE NOT NULL, -- UUID for tracking
    status execution_status DEFAULT 'pending',
    trigger_data JSONB, -- Data that triggered the execution
    result_data JSONB, -- Final result data
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Execution logs table
CREATE TABLE public.execution_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID NOT NULL REFERENCES public.workflow_executions(id) ON DELETE CASCADE,
    node_id VARCHAR(255) NOT NULL, -- Joint.js node ID
    node_name VARCHAR(255) NOT NULL,
    node_type VARCHAR(100) NOT NULL,
    status node_execution_status DEFAULT 'pending',
    input_data JSONB, -- Input data for the node
    output_data JSONB, -- Output data from the node
    error_message TEXT,
    execution_time_ms INTEGER, -- Execution time in milliseconds
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- JWT tokens table (for backend token management)
CREATE TABLE public.jwt_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token VARCHAR(500) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    is_revoked BOOLEAN DEFAULT false,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Password reset tokens table
CREATE TABLE public.password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    verification_code VARCHAR(6) NOT NULL, -- 6-digit code
    is_used BOOLEAN DEFAULT false,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_workflows_owner_id ON public.workflows(owner_id);
CREATE INDEX idx_workflows_is_active ON public.workflows(is_active);
CREATE INDEX idx_integrations_user_id ON public.integrations(user_id);
CREATE INDEX idx_integrations_provider ON public.integrations(provider);
CREATE INDEX idx_oauth_tokens_user_id ON public.oauth_tokens(user_id);
CREATE INDEX idx_oauth_tokens_integration_id ON public.oauth_tokens(integration_id);
CREATE INDEX idx_workflow_nodes_workflow_id ON public.workflow_nodes(workflow_id);
CREATE INDEX idx_workflow_nodes_node_id ON public.workflow_nodes(node_id);
CREATE INDEX idx_workflow_connections_workflow_id ON public.workflow_connections(workflow_id);
CREATE INDEX idx_workflow_triggers_workflow_id ON public.workflow_triggers(workflow_id);
CREATE INDEX idx_workflow_executions_workflow_id ON public.workflow_executions(workflow_id);
CREATE INDEX idx_workflow_executions_execution_id ON public.workflow_executions(execution_id);
CREATE INDEX idx_workflow_executions_status ON public.workflow_executions(status);
CREATE INDEX idx_execution_logs_execution_id ON public.execution_logs(execution_id);
CREATE INDEX idx_jwt_tokens_user_id ON public.jwt_tokens(user_id);
CREATE INDEX idx_jwt_tokens_token ON public.jwt_tokens(token);
CREATE INDEX idx_password_reset_tokens_email ON public.password_reset_tokens(email);
CREATE INDEX idx_password_reset_tokens_token ON public.password_reset_tokens(token);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON public.workflows FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON public.integrations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_oauth_tokens_updated_at BEFORE UPDATE ON public.oauth_tokens FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflow_nodes_updated_at BEFORE UPDATE ON public.workflow_nodes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflow_triggers_updated_at BEFORE UPDATE ON public.workflow_triggers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
