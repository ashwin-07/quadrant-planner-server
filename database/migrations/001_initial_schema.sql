-- =====================================================
-- Quadrant Planner Database Schema - Initial Migration
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- GOALS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category TEXT NOT NULL CHECK (category IN ('career', 'health', 'relationships', 'learning', 'financial', 'personal')),
    timeframe TEXT NOT NULL CHECK (timeframe IN ('3_months', '6_months', '1_year', 'ongoing')),
    color VARCHAR(50),
    archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Goals table comments
COMMENT ON TABLE goals IS 'User goals organized by category and timeframe';
COMMENT ON COLUMN goals.user_id IS 'User identifier from Google OAuth';
COMMENT ON COLUMN goals.category IS 'Goal category: career, health, relationships, learning, financial, personal';
COMMENT ON COLUMN goals.timeframe IS 'Target timeframe: 3_months, 6_months, 1_year, ongoing';
COMMENT ON COLUMN goals.archived IS 'Soft delete flag - archived goals are hidden but preserved for analytics';

-- =====================================================
-- TASKS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    goal_id UUID REFERENCES goals(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    quadrant TEXT NOT NULL CHECK (quadrant IN ('Q1', 'Q2', 'Q3', 'Q4', 'staging')),
    due_date TIMESTAMPTZ,
    estimated_minutes INTEGER CHECK (estimated_minutes BETWEEN 1 AND 480),
    priority TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    tags TEXT[] DEFAULT '{}',
    completed BOOLEAN DEFAULT FALSE,
    is_staged BOOLEAN DEFAULT FALSE,
    position INTEGER DEFAULT 0,
    staged_at TIMESTAMPTZ,
    organized_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tasks table comments
COMMENT ON TABLE tasks IS 'User tasks organized in Covey quadrants with staging zone';
COMMENT ON COLUMN tasks.user_id IS 'User identifier from Google OAuth';
COMMENT ON COLUMN tasks.goal_id IS 'Associated goal (nullable for flexibility)';
COMMENT ON COLUMN tasks.quadrant IS 'Covey quadrant: Q1 (urgent+important), Q2 (important), Q3 (urgent), Q4 (neither), staging';
COMMENT ON COLUMN tasks.estimated_minutes IS 'Estimated completion time in minutes (1-480 = 8 hours max)';
COMMENT ON COLUMN tasks.is_staged IS 'True if task is in staging zone (quadrant = staging)';
COMMENT ON COLUMN tasks.position IS 'Task position within quadrant for ordering';
COMMENT ON COLUMN tasks.staged_at IS 'Timestamp when task was moved to staging';
COMMENT ON COLUMN tasks.organized_at IS 'Timestamp when task was moved from staging to a quadrant';

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Goals indexes
CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals(user_id);
CREATE INDEX IF NOT EXISTS idx_goals_category ON goals(category);
CREATE INDEX IF NOT EXISTS idx_goals_archived ON goals(archived);
CREATE INDEX IF NOT EXISTS idx_goals_created_at ON goals(created_at);

-- Tasks indexes
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_goal_id ON tasks(goal_id);
CREATE INDEX IF NOT EXISTS idx_tasks_quadrant ON tasks(quadrant);
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);
CREATE INDEX IF NOT EXISTS idx_tasks_is_staged ON tasks(is_staged);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_user_quadrant ON tasks(user_id, quadrant);
CREATE INDEX IF NOT EXISTS idx_tasks_user_completed ON tasks(user_id, completed);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_goals_user_category_archived ON goals(user_id, category, archived);
CREATE INDEX IF NOT EXISTS idx_tasks_user_goal_completed ON tasks(user_id, goal_id, completed);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for automatic updated_at
CREATE TRIGGER update_goals_updated_at 
    BEFORE UPDATE ON goals 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at 
    BEFORE UPDATE ON tasks 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically set staging-related fields
CREATE OR REPLACE FUNCTION update_task_staging_fields()
RETURNS TRIGGER AS $$
BEGIN
    -- Set is_staged based on quadrant
    NEW.is_staged := (NEW.quadrant = 'staging');
    
    -- Set staged_at when moving to staging
    IF NEW.quadrant = 'staging' AND (OLD IS NULL OR OLD.quadrant != 'staging') THEN
        NEW.staged_at := NOW();
    END IF;
    
    -- Set organized_at when moving from staging to a quadrant
    IF OLD IS NOT NULL AND OLD.quadrant = 'staging' AND NEW.quadrant != 'staging' THEN
        NEW.organized_at := NOW();
    END IF;
    
    -- Set completed_at when marking as completed
    IF NEW.completed = TRUE AND (OLD IS NULL OR OLD.completed = FALSE) THEN
        NEW.completed_at := NOW();
    END IF;
    
    -- Clear completed_at when marking as incomplete
    IF NEW.completed = FALSE AND OLD IS NOT NULL AND OLD.completed = TRUE THEN
        NEW.completed_at := NULL;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for automatic staging field management
CREATE TRIGGER update_task_staging_fields_trigger
    BEFORE INSERT OR UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_task_staging_fields();

-- =====================================================
-- CONSTRAINTS AND VALIDATION
-- =====================================================

-- Add constraint to limit goals per user (max 100)
CREATE OR REPLACE FUNCTION check_goals_limit()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT COUNT(*) FROM goals WHERE user_id = NEW.user_id AND archived = FALSE) >= 100 THEN
        RAISE EXCEPTION 'Maximum of 100 active goals allowed per user';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_goals_limit
    BEFORE INSERT ON goals
    FOR EACH ROW
    EXECUTE FUNCTION check_goals_limit();

-- Add constraint to limit tasks per user (max 1000)
CREATE OR REPLACE FUNCTION check_tasks_limit()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT COUNT(*) FROM tasks WHERE user_id = NEW.user_id) >= 1000 THEN
        RAISE EXCEPTION 'Maximum of 1000 tasks allowed per user';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_tasks_limit
    BEFORE INSERT ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION check_tasks_limit();

-- Add constraint to limit staging zone (max 5 items)
CREATE OR REPLACE FUNCTION check_staging_limit()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.quadrant = 'staging' AND 
       (SELECT COUNT(*) FROM tasks WHERE user_id = NEW.user_id AND quadrant = 'staging' AND completed = FALSE) >= 5 THEN
        RAISE EXCEPTION 'Maximum of 5 items allowed in staging zone';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_staging_limit
    BEFORE INSERT OR UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION check_staging_limit();
