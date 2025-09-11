# Supabase Setup Guide for Flowmaker

This guide will help you set up your Supabase database with all the necessary tables, relationships, and security policies for your Flowmaker application.

## Prerequisites

1. A Supabase account and project
2. Your Supabase project URL and anon key
3. Access to your Supabase SQL editor

## Step 1: Create Your Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `flowmaker` (or your preferred name)
   - **Database Password**: Choose a strong password
   - **Region**: Choose the closest region to your users
5. Click "Create new project"
6. Wait for the project to be created (usually takes 1-2 minutes)

## Step 2: Get Your Project Credentials

1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (looks like `https://xyzabc123.supabase.co`)
   - **anon public key** (long string starting with `eyJ...`)

## Step 3: Update Your Frontend Configuration

Update `flowmaker/frontend/src/config/supabase.ts` with your credentials:

```typescript
export const SUPABASE_CONFIG = {
  url: 'https://YOUR-PROJECT-ID.supabase.co',  // Replace with your Project URL
  anonKey: 'YOUR-ANON-KEY-HERE'                // Replace with your anon key
}
```

## Step 4: Set Up Database Schema

1. In your Supabase dashboard, go to **SQL Editor**
2. Create a new query
3. Copy and paste the contents of `supabase-schema.sql`
4. Click "Run" to execute the schema creation

This will create:
- All necessary tables with proper relationships
- Custom data types (enums)
- Indexes for better performance
- Triggers for automatic `updated_at` timestamps

## Step 5: Set Up Row Level Security

1. In the SQL Editor, create another new query
2. Copy and paste the contents of `supabase-rls-policies.sql`
3. Click "Run" to execute the RLS policies

This will:
- Enable Row Level Security on all tables
- Create policies ensuring users can only access their own data
- Set up proper security for workflow-related data

## Step 6: Configure Authentication (Optional)

If you want to use Supabase's built-in authentication:

1. Go to **Authentication** → **Settings**
2. Configure your site URL (e.g., `http://localhost:5173` for development)
3. Set up email templates if needed
4. Configure OAuth providers if you plan to use them

## Step 7: Test Your Setup

1. Start your frontend application:
   ```bash
   cd flowmaker/frontend
   npm install
   npm run dev
   ```

2. Try to register a new user
3. Check your Supabase dashboard to see if the user was created in the `users` table

## Database Schema Overview

### Core Tables

- **users**: User profiles and authentication data
- **workflows**: Workflow definitions and metadata
- **workflow_nodes**: Individual nodes within workflows
- **workflow_connections**: Connections between nodes
- **workflow_triggers**: Trigger configurations for workflows
- **workflow_executions**: Execution history and status
- **execution_logs**: Detailed logs for each node execution

### Integration Tables

- **integrations**: Third-party service integrations
- **oauth_tokens**: OAuth tokens for integrations

### Utility Tables

- **jwt_tokens**: Backend JWT token management
- **password_reset_tokens**: Password reset functionality

## Security Features

- **Row Level Security (RLS)**: Ensures users can only access their own data
- **UUID Primary Keys**: More secure than sequential integers
- **Proper Foreign Key Constraints**: Maintains data integrity
- **Indexes**: Optimized for common query patterns

## Troubleshooting

### Common Issues

1. **"VITE_SUPABASE_URL is not set" error**
   - Make sure you've updated `supabase.ts` with your actual credentials
   - Check that the URL format is correct (should start with `https://`)

2. **Authentication not working**
   - Verify your site URL is configured in Supabase Auth settings
   - Check that RLS policies are properly set up

3. **Database connection issues**
   - Ensure your Supabase project is active
   - Check that the database password is correct
   - Verify network connectivity

### Getting Help

- Check the [Supabase Documentation](https://supabase.com/docs)
- Visit the [Supabase Community](https://github.com/supabase/supabase/discussions)
- Review the error logs in your Supabase dashboard

## Next Steps

Once your database is set up:

1. Test user registration and login
2. Create some sample workflows
3. Test workflow execution
4. Set up integrations with third-party services
5. Configure production environment variables

Your Flowmaker application is now ready to use with Supabase!
