"""
Pydantic models for Tasks API
"""

from typing import Optional, List, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from database.models import TaskQuadrant, TaskPriority
from api.shared.validation import (
    validate_task_title,
    validate_task_description,
    validate_estimated_minutes,
    validate_tags,
    validate_position,
    BaseValidator
)


class TaskBase(BaseModel):
    """Base task model with common fields"""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    quadrant: TaskQuadrant = Field(..., description="Task quadrant")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    estimated_minutes: Optional[int] = Field(None, ge=1, le=480, description="Estimated completion time in minutes")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority")
    tags: List[str] = Field(default_factory=list, max_items=10, description="Task tags")

    @validator('title')
    def validate_title(cls, v: str) -> str:
        return validate_task_title(v)

    @validator('description')
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        return validate_task_description(v)

    @validator('estimated_minutes')
    def validate_estimated_minutes(cls, v: Optional[int]) -> Optional[int]:
        return validate_estimated_minutes(v)

    @validator('tags')
    def validate_tags_field(cls, v: List[str]) -> List[str]:
        return validate_tags(v)


class TaskCreate(TaskBase):
    """Task creation model - user_id is extracted from JWT token"""
    goal_id: Optional[str] = Field(None, description="Associated goal ID")


class TaskUpdate(BaseModel):
    """Task update model - all fields optional, user_id is extracted from JWT token"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    goal_id: Optional[str] = Field(None, description="Associated goal ID")
    quadrant: Optional[TaskQuadrant] = Field(None, description="Task quadrant")
    due_date: Optional[datetime] = Field(None, description="Task due date")
    estimated_minutes: Optional[int] = Field(None, ge=1, le=480, description="Estimated completion time")
    priority: Optional[TaskPriority] = Field(None, description="Task priority")
    tags: Optional[List[str]] = Field(None, max_items=10, description="Task tags")
    completed: Optional[bool] = Field(None, description="Completion status")
    position: Optional[int] = Field(None, ge=0, description="Task position within quadrant")

    @validator('title')
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_task_title(v)
        return v

    @validator('description')
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        return validate_task_description(v)

    @validator('estimated_minutes')
    def validate_estimated_minutes(cls, v: Optional[int]) -> Optional[int]:
        return validate_estimated_minutes(v)

    @validator('tags')
    def validate_tags_field(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            return validate_tags(v)
        return v

    @validator('position')
    def validate_position_field(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            return validate_position(v)
        return v


class Task(TaskBase):
    """Task response model"""
    id: str = Field(..., description="Task unique identifier")
    user_id: str = Field(..., description="User identifier")
    goal_id: Optional[str] = Field(None, description="Associated goal ID")
    completed: bool = Field(default=False, description="Completion status")
    is_staged: bool = Field(default=False, description="Whether task is in staging zone")
    position: int = Field(default=0, description="Task position within quadrant")
    staged_at: Optional[datetime] = Field(None, description="When task was moved to staging")
    organized_at: Optional[datetime] = Field(None, description="When task was organized from staging")
    completed_at: Optional[datetime] = Field(None, description="When task was completed")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class TaskWithGoal(Task):
    """Task with associated goal information"""
    goal: Optional[dict] = Field(None, description="Associated goal information")


class TaskMove(BaseModel):
    """Task move model for drag & drop - user_id is extracted from JWT token"""
    quadrant: TaskQuadrant = Field(..., description="Target quadrant")
    position: int = Field(0, ge=0, description="Target position")
    is_staged: Optional[bool] = Field(None, description="Whether task is staged")

    @validator('position')
    def validate_position_field(cls, v: int) -> int:
        return validate_position(v)


class TaskToggle(BaseModel):
    """Task completion toggle model - user_id is extracted from JWT token"""
    pass  # No fields needed, just toggles completion status


class TaskBulkUpdate(BaseModel):
    """Bulk task update model - user_id is extracted from JWT token"""
    updates: List[dict] = Field(..., min_items=1, max_items=50, description="Task updates")


class TasksListResponse(BaseModel):
    """Response model for tasks list"""
    tasks: List[Union[Task, TaskWithGoal]] = Field(..., description="List of tasks")
    total: int = Field(..., ge=0, description="Total number of tasks")
    has_more: bool = Field(..., description="Whether there are more tasks")


class TaskStats(BaseModel):
    """Task statistics model"""
    total_tasks: int = Field(default=0, ge=0, description="Total number of tasks")
    completed_tasks: int = Field(default=0, ge=0, description="Number of completed tasks")
    active_tasks: int = Field(default=0, ge=0, description="Number of active tasks")
    overdue_tasks: int = Field(default=0, ge=0, description="Number of overdue tasks")
    staging_tasks: int = Field(default=0, ge=0, description="Number of tasks in staging")
    quadrant_distribution: dict = Field(default_factory=dict, description="Task distribution by quadrant")


# Staging zone specific models
class StagingZoneStatus(BaseModel):
    """Staging zone status model"""
    current_count: int = Field(..., ge=0, le=5, description="Current number of items in staging")
    max_capacity: int = Field(5, description="Maximum staging zone capacity")
    is_full: bool = Field(..., description="Whether staging zone is at capacity")
    oldest_item: Optional[dict] = Field(None, description="Information about oldest staged item")
    processing_reminder: Optional[str] = Field(None, description="Processing reminder message")


class StagingZoneResponse(BaseModel):
    """Staging zone response model"""
    status: StagingZoneStatus = Field(..., description="Staging zone status")
    tasks: List[Task] = Field(..., description="Tasks in staging zone")
    suggestions: List[str] = Field(default_factory=list, description="Organization suggestions")
