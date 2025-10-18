-- =====================================================
-- Subtasks Feature - Database Migration
-- =====================================================

-- Create subtasks table
CREATE TABLE IF NOT EXISTS subtasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    position INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Comments
COMMENT ON TABLE subtasks IS 'Subtasks for breaking down tasks into smaller actionable items';
COMMENT ON COLUMN subtasks.task_id IS 'Parent task reference (cascade delete)';
COMMENT ON COLUMN subtasks.title IS 'Subtask title (1-200 characters)';
COMMENT ON COLUMN subtasks.completed IS 'Completion status of the subtask';
COMMENT ON COLUMN subtasks.position IS 'Position within parent task for ordering';

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_subtasks_task_id ON subtasks(task_id);
CREATE INDEX IF NOT EXISTS idx_subtasks_completed ON subtasks(completed);
CREATE INDEX IF NOT EXISTS idx_subtasks_task_position ON subtasks(task_id, position);

-- Trigger for automatic updated_at
CREATE TRIGGER update_subtasks_updated_at 
    BEFORE UPDATE ON subtasks 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- Constraints and Validation
-- =====================================================

-- Limit subtasks per task (max 20)
CREATE OR REPLACE FUNCTION check_subtasks_limit()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT COUNT(*) FROM subtasks WHERE task_id = NEW.task_id) >= 20 THEN
        RAISE EXCEPTION 'Maximum of 20 subtasks allowed per task';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_subtasks_limit
    BEFORE INSERT ON subtasks
    FOR EACH ROW
    EXECUTE FUNCTION check_subtasks_limit();

