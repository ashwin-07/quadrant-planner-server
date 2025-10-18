-- =====================================================
-- Subtasks Row Level Security (RLS) Policies
-- =====================================================

-- Enable RLS on subtasks table
ALTER TABLE subtasks ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view their own subtasks" ON subtasks;
DROP POLICY IF EXISTS "Users can insert their own subtasks" ON subtasks;
DROP POLICY IF EXISTS "Users can update their own subtasks" ON subtasks;
DROP POLICY IF EXISTS "Users can delete their own subtasks" ON subtasks;

-- =====================================================
-- SELECT Policy: Users can view their own subtasks
-- =====================================================
CREATE POLICY "Users can view their own subtasks"
    ON subtasks
    FOR SELECT
    USING (
        task_id IN (
            SELECT id FROM tasks WHERE user_id = current_setting('app.current_user_id', TRUE)::TEXT
        )
    );

-- =====================================================
-- INSERT Policy: Users can insert subtasks for their tasks
-- =====================================================
CREATE POLICY "Users can insert their own subtasks"
    ON subtasks
    FOR INSERT
    WITH CHECK (
        task_id IN (
            SELECT id FROM tasks WHERE user_id = current_setting('app.current_user_id', TRUE)::TEXT
        )
    );

-- =====================================================
-- UPDATE Policy: Users can update their own subtasks
-- =====================================================
CREATE POLICY "Users can update their own subtasks"
    ON subtasks
    FOR UPDATE
    USING (
        task_id IN (
            SELECT id FROM tasks WHERE user_id = current_setting('app.current_user_id', TRUE)::TEXT
        )
    )
    WITH CHECK (
        task_id IN (
            SELECT id FROM tasks WHERE user_id = current_setting('app.current_user_id', TRUE)::TEXT
        )
    );

-- =====================================================
-- DELETE Policy: Users can delete their own subtasks
-- =====================================================
CREATE POLICY "Users can delete their own subtasks"
    ON subtasks
    FOR DELETE
    USING (
        task_id IN (
            SELECT id FROM tasks WHERE user_id = current_setting('app.current_user_id', TRUE)::TEXT
        )
    );

-- =====================================================
-- Service Role Policies (bypass RLS)
-- =====================================================
-- Service role can do anything (for backend operations)
CREATE POLICY "Service role has full access to subtasks"
    ON subtasks
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

