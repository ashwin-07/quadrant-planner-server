-- =====================================================
-- Row Level Security (RLS) Policies for Quadrant Planner
-- =====================================================

-- Note: These policies should be applied in the Supabase dashboard
-- or via the Supabase CLI, as they require proper authentication context

-- =====================================================
-- ENABLE ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- GOALS TABLE POLICIES
-- =====================================================

-- Policy: Users can only see their own goals
CREATE POLICY "Users can view own goals" ON goals
    FOR SELECT USING (
        auth.uid()::text = user_id OR user_id = current_setting('app.current_user_id', true)
    );

-- Policy: Users can insert their own goals
CREATE POLICY "Users can insert own goals" ON goals
    FOR INSERT WITH CHECK (
        auth.uid()::text = user_id OR user_id = current_setting('app.current_user_id', true)
    );

-- Policy: Users can update their own goals
CREATE POLICY "Users can update own goals" ON goals
    FOR UPDATE USING (
        auth.uid()::text = user_id OR user_id = current_setting('app.current_user_id', true)
    ) WITH CHECK (
        auth.uid()::text = user_id OR user_id = current_setting('app.current_user_id', true)
    );

-- Policy: Users can delete their own goals
CREATE POLICY "Users can delete own goals" ON goals
    FOR DELETE USING (
        auth.uid()::text = user_id OR user_id = current_setting('app.current_user_id', true)
    );

-- =====================================================
-- TASKS TABLE POLICIES
-- =====================================================

-- Policy: Users can only see their own tasks
CREATE POLICY "Users can view own tasks" ON tasks
    FOR SELECT USING (
        auth.uid()::text = user_id OR user_id = current_setting('app.current_user_id', true)
    );

-- Policy: Users can insert their own tasks
CREATE POLICY "Users can insert own tasks" ON tasks
    FOR INSERT WITH CHECK (
        auth.uid()::text = user_id OR user_id = current_setting('app.current_user_id', true)
    );

-- Policy: Users can update their own tasks
CREATE POLICY "Users can update own tasks" ON tasks
    FOR UPDATE USING (
        auth.uid()::text = user_id OR user_id = current_setting('app.current_user_id', true)
    ) WITH CHECK (
        auth.uid()::text = user_id OR user_id = current_setting('app.current_user_id', true)
    );

-- Policy: Users can delete their own tasks
CREATE POLICY "Users can delete own tasks" ON tasks
    FOR DELETE USING (
        auth.uid()::text = user_id OR user_id = current_setting('app.current_user_id', true)
    );

-- =====================================================
-- HELPER FUNCTIONS FOR RLS
-- =====================================================

-- Function to set current user context for service role operations
CREATE OR REPLACE FUNCTION set_current_user_id(user_id_param text)
RETURNS void
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
BEGIN
    PERFORM set_config('app.current_user_id', user_id_param, true);
END;
$$;

-- Function to get current user ID
CREATE OR REPLACE FUNCTION get_current_user_id()
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    RETURN COALESCE(
        auth.uid()::text,
        current_setting('app.current_user_id', true)
    );
END;
$$;

-- =====================================================
-- GRANTS AND PERMISSIONS
-- =====================================================

-- Grant necessary permissions to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON goals TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON tasks TO authenticated;

-- Grant permissions to service role for admin operations
GRANT ALL ON goals TO service_role;
GRANT ALL ON tasks TO service_role;

-- Grant usage on sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO service_role;
