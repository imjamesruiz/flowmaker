-- Row Level Security (RLS) Policies for Supabase
-- This script sets up security policies to ensure users can only access their own data

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.oauth_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_triggers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.execution_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jwt_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.password_reset_tokens ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can view their own profile" ON public.users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update their own profile" ON public.users
    FOR UPDATE USING (auth.uid()::text = id::text);

CREATE POLICY "Users can insert their own profile" ON public.users
    FOR INSERT WITH CHECK (auth.uid()::text = id::text);

-- Workflows table policies
CREATE POLICY "Users can view their own workflows" ON public.workflows
    FOR SELECT USING (auth.uid()::text = owner_id::text);

CREATE POLICY "Users can create workflows" ON public.workflows
    FOR INSERT WITH CHECK (auth.uid()::text = owner_id::text);

CREATE POLICY "Users can update their own workflows" ON public.workflows
    FOR UPDATE USING (auth.uid()::text = owner_id::text);

CREATE POLICY "Users can delete their own workflows" ON public.workflows
    FOR DELETE USING (auth.uid()::text = owner_id::text);

-- Integrations table policies
CREATE POLICY "Users can view their own integrations" ON public.integrations
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can create integrations" ON public.integrations
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own integrations" ON public.integrations
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete their own integrations" ON public.integrations
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- OAuth tokens table policies
CREATE POLICY "Users can view their own oauth tokens" ON public.oauth_tokens
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can create oauth tokens" ON public.oauth_tokens
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own oauth tokens" ON public.oauth_tokens
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete their own oauth tokens" ON public.oauth_tokens
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- Workflow nodes table policies
CREATE POLICY "Users can view nodes of their workflows" ON public.workflow_nodes
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.workflows 
            WHERE workflows.id = workflow_nodes.workflow_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can create nodes in their workflows" ON public.workflow_nodes
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workflows 
            WHERE workflows.id = workflow_nodes.workflow_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can update nodes in their workflows" ON public.workflow_nodes
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.workflows 
            WHERE workflows.id = workflow_nodes.workflow_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can delete nodes from their workflows" ON public.workflow_nodes
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.workflows 
            WHERE workflows.id = workflow_nodes.workflow_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

-- Workflow connections table policies
CREATE POLICY "Users can view connections of their workflows" ON public.workflow_connections
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.workflows 
            WHERE workflows.id = workflow_connections.workflow_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can create connections in their workflows" ON public.workflow_connections
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workflows 
            WHERE workflows.id = workflow_connections.workflow_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can update connections in their workflows" ON public.workflow_connections
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.workflows 
            WHERE workflows.id = workflow_connections.workflow_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can delete connections from their workflows" ON public.workflow_connections
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.workflows 
            WHERE workflows.id = workflow_connections.workflow_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

-- Workflow triggers table policies
CREATE POLICY "Users can view triggers of their workflows" ON public.workflow_triggers
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.workflows 
            WHERE workflows.id = workflow_triggers.workflow_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can create triggers for their workflows" ON public.workflow_triggers
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workflows 
            WHERE workflows.id = workflow_triggers.workflow_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can update triggers of their workflows" ON public.workflow_triggers
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.workflows 
            WHERE workflows.id = workflow_triggers.workflow_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can delete triggers from their workflows" ON public.workflow_triggers
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.workflows 
            WHERE workflows.id = workflow_triggers.workflow_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

-- Workflow executions table policies
CREATE POLICY "Users can view executions of their workflows" ON public.workflow_executions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.workflows 
            WHERE workflows.id = workflow_executions.workflow_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can create executions for their workflows" ON public.workflow_executions
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workflows 
            WHERE workflows.id = workflow_executions.workflow_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can update executions of their workflows" ON public.workflow_executions
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.workflows 
            WHERE workflows.id = workflow_executions.workflow_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can delete executions from their workflows" ON public.workflow_executions
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.workflows 
            WHERE workflows.id = workflow_executions.workflow_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

-- Execution logs table policies
CREATE POLICY "Users can view logs of their workflow executions" ON public.execution_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.workflow_executions 
            JOIN public.workflows ON workflows.id = workflow_executions.workflow_id
            WHERE workflow_executions.id = execution_logs.execution_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can create logs for their workflow executions" ON public.execution_logs
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.workflow_executions 
            JOIN public.workflows ON workflows.id = workflow_executions.workflow_id
            WHERE workflow_executions.id = execution_logs.execution_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can update logs of their workflow executions" ON public.execution_logs
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.workflow_executions 
            JOIN public.workflows ON workflows.id = workflow_executions.workflow_id
            WHERE workflow_executions.id = execution_logs.execution_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can delete logs from their workflow executions" ON public.execution_logs
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.workflow_executions 
            JOIN public.workflows ON workflows.id = workflow_executions.workflow_id
            WHERE workflow_executions.id = execution_logs.execution_id 
            AND workflows.owner_id::text = auth.uid()::text
        )
    );

-- JWT tokens table policies
CREATE POLICY "Users can view their own jwt tokens" ON public.jwt_tokens
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can create jwt tokens" ON public.jwt_tokens
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own jwt tokens" ON public.jwt_tokens
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete their own jwt tokens" ON public.jwt_tokens
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- Password reset tokens table policies (more permissive for password reset functionality)
CREATE POLICY "Anyone can create password reset tokens" ON public.password_reset_tokens
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Anyone can view password reset tokens by email" ON public.password_reset_tokens
    FOR SELECT USING (true);

CREATE POLICY "Anyone can update password reset tokens" ON public.password_reset_tokens
    FOR UPDATE USING (true);

CREATE POLICY "Anyone can delete password reset tokens" ON public.password_reset_tokens
    FOR DELETE USING (true);
