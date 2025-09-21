"""
Database models and schema definitions
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class GoalCategory(str, Enum):
    """Goal category enumeration"""
    CAREER = "career"
    HEALTH = "health"
    RELATIONSHIPS = "relationships"
    LEARNING = "learning"
    FINANCIAL = "financial"
    PERSONAL = "personal"


class GoalTimeframe(str, Enum):
    """Goal timeframe enumeration"""
    THREE_MONTHS = "3_months"
    SIX_MONTHS = "6_months"
    ONE_YEAR = "1_year"
    ONGOING = "ongoing"


class TaskQuadrant(str, Enum):
    """Task quadrant enumeration"""
    Q1 = "Q1"  # Urgent + Important
    Q2 = "Q2"  # Important + Not Urgent
    Q3 = "Q3"  # Urgent + Not Important
    Q4 = "Q4"  # Not Important + Not Urgent
    STAGING = "staging"  # Staging zone


class TaskPriority(str, Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Goal(BaseModel):
    """Goal database model"""
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    category: GoalCategory
    timeframe: GoalTimeframe
    color: Optional[str] = None
    archived: bool = False
    created_at: datetime
    updated_at: datetime


class Task(BaseModel):
    """Task database model"""
    id: str
    user_id: str
    goal_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    quadrant: TaskQuadrant
    due_date: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: List[str] = Field(default_factory=list)
    completed: bool = False
    is_staged: bool = False
    position: int = 0
    staged_at: Optional[datetime] = None
    organized_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class GoalWithStats(Goal):
    """Goal with statistics"""
    total_tasks: int = 0
    completed_tasks: int = 0
    active_tasks: int = 0
    completion_rate: float = 0.0


class TaskWithGoal(Task):
    """Task with associated goal information"""
    goal: Optional[dict] = None  # Will contain goal info: {id, title, category, color}


# Database table schemas for Supabase
GOALS_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    category TEXT CHECK (category IN ('career', 'health', 'relationships', 'learning', 'financial', 'personal')),
    timeframe TEXT CHECK (timeframe IN ('3_months', '6_months', '1_year', 'ongoing')),
    color VARCHAR(50),
    archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
"""

TASKS_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    goal_id UUID REFERENCES goals(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    quadrant TEXT CHECK (quadrant IN ('Q1', 'Q2', 'Q3', 'Q4', 'staging')),
    due_date TIMESTAMPTZ,
    estimated_minutes INTEGER CHECK (estimated_minutes BETWEEN 1 AND 480),
    priority TEXT CHECK (priority IN ('low', 'medium', 'high', 'urgent')) DEFAULT 'medium',
    tags TEXT[],
    completed BOOLEAN DEFAULT FALSE,
    is_staged BOOLEAN DEFAULT FALSE,
    position INTEGER DEFAULT 0,
    staged_at TIMESTAMPTZ,
    organized_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
"""

INDEXES_SCHEMA = """
-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals(user_id);
CREATE INDEX IF NOT EXISTS idx_goals_category ON goals(category);
CREATE INDEX IF NOT EXISTS idx_goals_archived ON goals(archived);

CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_goal_id ON tasks(goal_id);
CREATE INDEX IF NOT EXISTS idx_tasks_quadrant ON tasks(quadrant);
CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);
CREATE INDEX IF NOT EXISTS idx_tasks_is_staged ON tasks(is_staged);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
"""

RLS_POLICIES_SCHEMA = """
-- Enable Row Level Security
ALTER TABLE goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Note: RLS policies will be configured through Supabase dashboard
-- since they require proper authentication context
"""
