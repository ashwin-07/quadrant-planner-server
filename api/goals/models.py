"""
Pydantic models for Goals API
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from database.models import GoalCategory, GoalTimeframe
from api.shared.validation import (
    validate_goal_title,
    validate_goal_description,
    validate_color,
    BaseValidator
)


class GoalBase(BaseModel):
    """Base goal model with common fields"""
    title: str = Field(..., min_length=1, max_length=200, description="Goal title")
    description: Optional[str] = Field(None, max_length=1000, description="Goal description")
    category: GoalCategory = Field(..., description="Goal category")
    timeframe: GoalTimeframe = Field(..., description="Goal timeframe")
    color: Optional[str] = Field(None, max_length=50, description="Goal color (hex or name)")

    class Config:
        populate_by_name = True  # Accept both snake_case and camelCase
        json_schema_serialization_defaults_required = True
        ser_json_by_alias = True  # Serialize using aliases (camelCase) in responses

    @validator('title')
    def validate_title(cls, v: str) -> str:
        return validate_goal_title(v)

    @validator('description')
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        return validate_goal_description(v)

    @validator('color')
    def validate_color_format(cls, v: Optional[str]) -> Optional[str]:
        return validate_color(v)


class GoalCreate(GoalBase):
    """Goal creation model - user_id is extracted from JWT token"""
    pass


class GoalUpdate(BaseModel):
    """Goal update model - all fields optional"""
    user_id: str = Field(..., alias="userId", min_length=1, max_length=255, description="User identifier")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Goal title")
    description: Optional[str] = Field(None, max_length=1000, description="Goal description")
    category: Optional[GoalCategory] = Field(None, description="Goal category")
    timeframe: Optional[GoalTimeframe] = Field(None, description="Goal timeframe")
    color: Optional[str] = Field(None, max_length=50, description="Goal color")
    archived: Optional[bool] = Field(None, description="Archive status")

    class Config:
        populate_by_name = True  # Accept both snake_case and camelCase
        json_schema_serialization_defaults_required = True
        ser_json_by_alias = True  # Serialize using aliases (camelCase) in responses

    @validator('user_id')
    def validate_user_id(cls, v: str) -> str:
        return BaseValidator.validate_required_string(v, "User ID", 255)

    @validator('title')
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_goal_title(v)
        return v

    @validator('description')
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        return validate_goal_description(v)

    @validator('color')
    def validate_color_format(cls, v: Optional[str]) -> Optional[str]:
        return validate_color(v)


class Goal(GoalBase):
    """Goal response model"""
    id: str = Field(..., description="Goal unique identifier")
    user_id: str = Field(..., alias="userId", description="User identifier")
    archived: bool = Field(default=False, description="Archive status")
    created_at: datetime = Field(..., alias="createdAt", description="Creation timestamp")
    updated_at: datetime = Field(..., alias="updatedAt", description="Last update timestamp")

    class Config:
        from_attributes = True
        populate_by_name = True  # Accept both snake_case and camelCase
        json_schema_serialization_defaults_required = True
        ser_json_by_alias = True  # Serialize using aliases (camelCase) in responses


class GoalWithStats(Goal):
    """Goal with statistics"""
    total_tasks: int = Field(default=0, alias="totalTasks", description="Total number of tasks")
    completed_tasks: int = Field(default=0, alias="completedTasks", description="Number of completed tasks")
    active_tasks: int = Field(default=0, alias="activeTasks", description="Number of active tasks")
    completion_rate: float = Field(default=0.0, alias="completionRate", ge=0, le=100, description="Completion rate percentage")
    average_task_age: Optional[float] = Field(default=None, alias="averageTaskAge", description="Average age of active tasks in days")
    last_activity_at: Optional[datetime] = Field(default=None, alias="lastActivityAt", description="Last activity timestamp")


class GoalStats(BaseModel):
    """Goal statistics model"""
    total_tasks: int = Field(default=0, alias="totalTasks", ge=0, description="Total number of tasks")
    completed_tasks: int = Field(default=0, alias="completedTasks", ge=0, description="Number of completed tasks")
    active_tasks: int = Field(default=0, alias="activeTasks", ge=0, description="Number of active tasks")
    completion_rate: float = Field(default=0.0, alias="completionRate", ge=0, le=100, description="Completion rate percentage")
    average_task_age: Optional[float] = Field(default=None, alias="averageTaskAge", ge=0, description="Average age of active tasks in days")
    last_activity_at: Optional[datetime] = Field(default=None, alias="lastActivityAt", description="Last activity timestamp")

    class Config:
        populate_by_name = True
        json_schema_serialization_defaults_required = True
        ser_json_by_alias = True


class TaskSummary(BaseModel):
    """Summary of a task for goal details"""
    id: str = Field(..., description="Task ID")
    title: str = Field(..., description="Task title")
    completed: bool = Field(..., description="Completion status")
    quadrant: str = Field(..., description="Task quadrant")


class GoalWithTasks(Goal):
    """Goal with associated tasks"""
    tasks: List[TaskSummary] = Field(default_factory=list, description="Associated tasks")
    stats: GoalStats = Field(..., description="Goal statistics")


class GoalsListResponse(BaseModel):
    """Response model for goals list"""
    goals: List[Goal] = Field(..., description="List of goals")
    total: int = Field(..., ge=0, description="Total number of goals")
    has_more: bool = Field(..., alias="hasMore", description="Whether there are more goals")

    class Config:
        populate_by_name = True
        json_schema_serialization_defaults_required = True
        ser_json_by_alias = True


class GoalsListWithStatsResponse(BaseModel):
    """Response model for goals list with statistics"""
    goals: List[GoalWithStats] = Field(..., description="List of goals with statistics")
    total: int = Field(..., ge=0, description="Total number of goals")
    has_more: bool = Field(..., alias="hasMore", description="Whether there are more goals")

    class Config:
        populate_by_name = True
        json_schema_serialization_defaults_required = True
        ser_json_by_alias = True
