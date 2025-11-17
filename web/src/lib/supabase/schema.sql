-- ============================================================================
-- Open Agent Studio - Supabase Database Schema
-- ============================================================================
-- This schema includes Row Level Security (RLS) policies for data protection
-- Run this in your Supabase SQL editor to set up the database

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- PROFILES TABLE
-- ============================================================================
-- Stores user profile data synchronized with Clerk

CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_user_id TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'developer', 'user')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles
CREATE POLICY "Users can view their own profile"
    ON profiles FOR SELECT
    USING (clerk_user_id = current_setting('request.jwt.claims')::json->>'sub');

CREATE POLICY "Users can update their own profile"
    ON profiles FOR UPDATE
    USING (clerk_user_id = current_setting('request.jwt.claims')::json->>'sub');

-- Admins can view all profiles
CREATE POLICY "Admins can view all profiles"
    ON profiles FOR SELECT
    USING (
        (SELECT role FROM profiles WHERE clerk_user_id = current_setting('request.jwt.claims')::json->>'sub') = 'admin'
    );

-- ============================================================================
-- ML INFERENCES TABLE
-- ============================================================================
-- Stores ML inference requests and results for audit and analytics

CREATE TABLE IF NOT EXISTS ml_inferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL REFERENCES profiles(clerk_user_id) ON DELETE CASCADE,
    model_name TEXT NOT NULL,
    input_data JSONB NOT NULL,
    output_data JSONB,
    confidence_score DECIMAL(5,4),
    processing_time_ms INTEGER DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('success', 'failed', 'pending')),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Index for performance
    INDEX idx_ml_inferences_user_id ON ml_inferences(user_id),
    INDEX idx_ml_inferences_created_at ON ml_inferences(created_at DESC)
);

-- Enable RLS
ALTER TABLE ml_inferences ENABLE ROW LEVEL SECURITY;

-- RLS Policies for ml_inferences
CREATE POLICY "Users can view their own inferences"
    ON ml_inferences FOR SELECT
    USING (user_id = current_setting('request.jwt.claims')::json->>'sub');

CREATE POLICY "Users can insert their own inferences"
    ON ml_inferences FOR INSERT
    WITH CHECK (user_id = current_setting('request.jwt.claims')::json->>'sub');

-- Admins can view all inferences
CREATE POLICY "Admins can view all inferences"
    ON ml_inferences FOR SELECT
    USING (
        (SELECT role FROM profiles WHERE clerk_user_id = current_setting('request.jwt.claims')::json->>'sub') = 'admin'
    );

-- ============================================================================
-- AUTOMATION WORKFLOWS TABLE
-- ============================================================================
-- Stores user-created automation workflows

CREATE TABLE IF NOT EXISTS automation_workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL REFERENCES profiles(clerk_user_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    workflow_data JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    last_run_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Index for performance
    INDEX idx_workflows_user_id ON automation_workflows(user_id),
    INDEX idx_workflows_active ON automation_workflows(is_active)
);

-- Enable RLS
ALTER TABLE automation_workflows ENABLE ROW LEVEL SECURITY;

-- RLS Policies for automation_workflows
CREATE POLICY "Users can manage their own workflows"
    ON automation_workflows FOR ALL
    USING (user_id = current_setting('request.jwt.claims')::json->>'sub');

-- ============================================================================
-- API KEYS TABLE
-- ============================================================================
-- Stores hashed API keys for programmatic access
-- SECURITY: Never store plain-text keys, only hashes

CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL REFERENCES profiles(clerk_user_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    key_hash TEXT NOT NULL,
    key_preview TEXT NOT NULL, -- Last 4 characters for identification
    permissions TEXT[] DEFAULT ARRAY['api:read']::TEXT[],
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Index for performance
    INDEX idx_api_keys_user_id ON api_keys(user_id),
    INDEX idx_api_keys_hash ON api_keys(key_hash)
);

-- Enable RLS
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- RLS Policies for api_keys
CREATE POLICY "Users can manage their own API keys"
    ON api_keys FOR ALL
    USING (user_id = current_setting('request.jwt.claims')::json->>'sub');

-- ============================================================================
-- AUDIT LOGS TABLE
-- ============================================================================
-- Security audit trail for compliance and monitoring

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT REFERENCES profiles(clerk_user_id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    metadata JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Index for performance
    INDEX idx_audit_logs_user_id ON audit_logs(user_id),
    INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC),
    INDEX idx_audit_logs_action ON audit_logs(action)
);

-- Enable RLS
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for audit_logs
CREATE POLICY "Users can view their own audit logs"
    ON audit_logs FOR SELECT
    USING (user_id = current_setting('request.jwt.claims')::json->>'sub');

-- Admins can view all audit logs
CREATE POLICY "Admins can view all audit logs"
    ON audit_logs FOR SELECT
    USING (
        (SELECT role FROM profiles WHERE clerk_user_id = current_setting('request.jwt.claims')::json->>'sub') = 'admin'
    );

-- System can always insert audit logs
CREATE POLICY "System can insert audit logs"
    ON audit_logs FOR INSERT
    WITH CHECK (true);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for profiles
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for automation_workflows
CREATE TRIGGER update_workflows_updated_at
    BEFORE UPDATE ON automation_workflows
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- STORAGE BUCKETS
-- ============================================================================
-- Run these commands in the Supabase dashboard Storage section

-- Create storage buckets (run in Supabase dashboard):
-- 1. ml-uploads (for ML inference inputs)
-- 2. user-files (for general user uploads)
-- 3. automation-outputs (for automation results)

-- Storage RLS Policies (apply in Supabase dashboard):
/*
Bucket: ml-uploads
- Users can upload to their own folder: user_id/{filename}
- Users can read only their own files
- Files auto-delete after 7 days (set in bucket settings)

Bucket: user-files
- Users can upload to their own folder
- Users can read only their own files
- Max file size: 10MB (set in bucket settings)

Bucket: automation-outputs
- System can write
- Users can read their own outputs
- Files auto-delete after 30 days
*/

-- ============================================================================
-- DATA RETENTION POLICIES
-- ============================================================================

-- Function to clean up old audit logs
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs()
RETURNS void AS $$
BEGIN
    DELETE FROM audit_logs
    WHERE created_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old ML inferences
CREATE OR REPLACE FUNCTION cleanup_old_ml_inferences()
RETURNS void AS $$
BEGIN
    DELETE FROM ml_inferences
    WHERE created_at < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- Schedule cleanup (configure in Supabase Dashboard > Database > Cron Jobs):
-- Run daily at 2 AM:
-- SELECT cron.schedule('cleanup-audit-logs', '0 2 * * *', 'SELECT cleanup_old_audit_logs()');
-- SELECT cron.schedule('cleanup-ml-inferences', '0 2 * * *', 'SELECT cleanup_old_ml_inferences()');

-- ============================================================================
-- INITIAL SETUP COMPLETE
-- ============================================================================
-- Next steps:
-- 1. Create storage buckets in Supabase Dashboard
-- 2. Configure storage RLS policies
-- 3. Set up cron jobs for data retention
-- 4. Create initial admin user profile
-- 5. Test RLS policies with different user roles
