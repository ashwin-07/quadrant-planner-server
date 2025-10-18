"""
Pydantic models for Tasks API
"""

from typing import Optional, List, Union
from datetime import datetime, date
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


# =====================================================
# SUBTASK MODELS (defined first to avoid circular imports)
# =====================================================

class SubtaskBase(BaseModel):
    """Base subtask model"""
    title: str = Field(..., min_length=1, max_length=200, description="Subtask title")

    @validator('title')
    def validate_title(cls, v: str) -> str:
        return validate_task_title(v)


class SubtaskCreate(SubtaskBase):
    """Subtask creation model (no ID - for new subtasks)"""
    pass


class SubtaskUpdate(SubtaskBase):
    """Subtask update model (with ID - for existing subtasks)"""
    id: str = Field(..., description="Subtask ID for updates")
    completed: Optional[bool] = Field(None, description="Completion status")


class Subtask(SubtaskBase):
    """Subtask response model"""
    id: str = Field(..., description="Subtask unique identifier")
    task_id: str = Field(..., alias="taskId", description="Parent task identifier")
    completed: bool = Field(default=False, description="Completion status")
    position: int = Field(default=0, description="Subtask position within task")
    created_at: datetime = Field(..., alias="createdAt", description="Creation timestamp")
    updated_at: datetime = Field(..., alias="updatedAt", description="Last update timestamp")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_serialization_defaults_required = True
        ser_json_by_alias = True
        json_schema_extra = {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "taskId": "f1e2d3c4-b5a6-9876-5432-10fedcba9876",
                "title": "Research requirements",
                "completed": False,
                "position": 0,
                "createdAt": "2025-10-18T10:00:00Z",
                "updatedAt": "2025-10-18T10:00:00Z"
            }
        }


class TaskBase(BaseModel):
    """Base task model with common fields"""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    quadrant: TaskQuadrant = Field(..., description="Task quadrant")
    due_date: Optional[datetime] = Field(None, alias="dueDate", description="Task due date")
    estimated_minutes: Optional[int] = Field(None, alias="estimatedMinutes", ge=1, le=480, description="Estimated completion time in minutes")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority")
    tags: List[str] = Field(default_factory=list, max_items=10, description="Task tags")

    class Config:
        populate_by_name = True  # Accept both snake_case and camelCase
        json_schema_serialization_defaults_required = True
        ser_json_by_alias = True  # Serialize using aliases (camelCase) in responses

    @validator('title')
    def validate_title(cls, v: str) -> str:
        return validate_task_title(v)

    @validator('description')
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        return validate_task_description(v)

    @validator('due_date', pre=True)
    def validate_due_date(cls, v: Optional[Union[str, datetime, date]]) -> Optional[datetime]:
        """Convert date-only strings to datetime objects"""
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, date):
            return datetime.combine(v, datetime.min.time())
        if isinstance(v, str):
            # Try parsing as date-only string (YYYY-MM-DD)
            if len(v) == 10 and v.count('-') == 2:
                try:
                    parsed_date = datetime.strptime(v, '%Y-%m-%d')
                    return parsed_date
                except ValueError:
                    pass
            # Let Pydantic handle full datetime strings
            return v
        return v

    @validator('estimated_minutes')
    def validate_estimated_minutes(cls, v: Optional[int]) -> Optional[int]:
        return validate_estimated_minutes(v)

    @validator('tags')
    def validate_tags_field(cls, v: List[str]) -> List[str]:
        return validate_tags(v)


class TaskCreate(TaskBase):
    """Task creation model - user_id is extracted from JWT token"""
    goal_id: Optional[str] = Field(None, alias="goalId", description="Associated goal ID")
    subtasks: Optional[List[Union[SubtaskCreate, SubtaskUpdate]]] = Field(default_factory=list, max_items=20, description="Subtasks for the task")


class TaskUpdate(BaseModel):
    """Task update model - all fields optional, user_id is extracted from JWT token"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    goal_id: Optional[str] = Field(None, alias="goalId", description="Associated goal ID")
    quadrant: Optional[TaskQuadrant] = Field(None, description="Task quadrant")
    due_date: Optional[datetime] = Field(None, alias="dueDate", description="Task due date")
    estimated_minutes: Optional[int] = Field(None, alias="estimatedMinutes", ge=1, le=480, description="Estimated completion time")
    priority: Optional[TaskPriority] = Field(None, description="Task priority")
    tags: Optional[List[str]] = Field(None, max_items=10, description="Task tags")
    completed: Optional[bool] = Field(None, description="Completion status")
    position: Optional[int] = Field(None, ge=0, description="Task position within quadrant")
    subtasks: Optional[List[Union[SubtaskCreate, SubtaskUpdate]]] = Field(None, max_items=20, description="Subtasks for the task")

    class Config:
        populate_by_name = True  # Accept both snake_case and camelCase
        json_schema_serialization_defaults_required = True
        ser_json_by_alias = True  # Serialize using aliases (camelCase) in responses

    @validator('title')
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_task_title(v)
        return v

    @validator('description')
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        return validate_task_description(v)

    @validator('due_date', pre=True)
    def validate_due_date(cls, v: Optional[Union[str, datetime, date]]) -> Optional[datetime]:
        """Convert date-only strings to datetime objects"""
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, date):
            return datetime.combine(v, datetime.min.time())
        if isinstance(v, str):
            # Try parsing as date-only string (YYYY-MM-DD)
            if len(v) == 10 and v.count('-') == 2:
                try:
                    parsed_date = datetime.strptime(v, '%Y-%m-%d')
                    return parsed_date
                except ValueError:
                    pass
            # Let Pydantic handle full datetime strings
            return v
        return v

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
    user_id: str = Field(..., alias="userId", description="User identifier")
    goal_id: Optional[str] = Field(None, alias="goalId", description="Associated goal ID")
    completed: bool = Field(default=False, description="Completion status")
    is_staged: bool = Field(default=False, alias="isStaged", description="Whether task is in staging zone")
    position: int = Field(default=0, description="Task position within quadrant")
    staged_at: Optional[datetime] = Field(None, alias="stagedAt", description="When task was moved to staging")
    organized_at: Optional[datetime] = Field(None, alias="organizedAt", description="When task was organized from staging")
    completed_at: Optional[datetime] = Field(None, alias="completedAt", description="When task was completed")
    created_at: datetime = Field(..., alias="createdAt", description="Creation timestamp")
    updated_at: datetime = Field(..., alias="updatedAt", description="Last update timestamp")
    subtasks: List[Subtask] = Field(default_factory=list, description="Subtasks for the task")

    class Config:
        from_attributes = True
        populate_by_name = True  # Accept both snake_case and camelCase
        json_schema_serialization_defaults_required = True
        ser_json_by_alias = True  # Serialize using aliases (camelCase) in responses
        json_schema_extra = {
            "example": {
                "id": "f1e2d3c4-b5a6-9876-5432-10fedcba9876",
                "title": "Complete project proposal",
                "description": "Write and submit the Q4 proposal",
                "quadrant": "Q1",
                "priority": "high",
                "dueDate": "2025-10-25T00:00:00Z",
                "completed": False,
                "subtasks": [
                    {
                        "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                        "taskId": "f1e2d3c4-b5a6-9876-5432-10fedcba9876",
                        "title": "Research requirements",
                        "completed": True,
                        "position": 0,
                        "createdAt": "2025-10-18T10:00:00Z",
                        "updatedAt": "2025-10-18T10:00:00Z"
                    },
                    {
                        "id": "b2c3d4e5-f6g7-8901-2345-678901bcdefg",
                        "taskId": "f1e2d3c4-b5a6-9876-5432-10fedcba9876",
                        "title": "Draft outline",
                        "completed": False,
                        "position": 1,
                        "createdAt": "2025-10-18T10:05:00Z",
                        "updatedAt": "2025-10-18T10:05:00Z"
                    }
                ]
            }
        }


class TaskWithGoal(Task):
    """Task with associated goal information"""
    goal: Optional[dict] = Field(None, description="Associated goal information")


class TaskMove(BaseModel):
    """Task move model for drag & drop - user_id is extracted from JWT token"""
    quadrant: TaskQuadrant = Field(..., description="Target quadrant")
    position: int = Field(0, ge=0, description="Target position")
    is_staged: Optional[bool] = Field(None, alias="isStaged", description="Whether task is staged")

    class Config:
        populate_by_name = True  # Accept both snake_case and camelCase
        json_schema_serialization_defaults_required = True
        ser_json_by_alias = True  # Serialize using aliases (camelCase) in responses

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
    has_more: bool = Field(..., alias="hasMore", description="Whether there are more tasks")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "tasks": [
                    {
                        "id": "f1e2d3c4-b5a6-9876-5432-10fedcba9876",
                        "title": "Complete project proposal",
                        "description": "Write and submit the Q4 proposal",
                        "quadrant": "Q1",
                        "priority": "high",
                        "dueDate": "2025-10-25T00:00:00Z",
                        "completed": False,
                        "subtasks": [
                            {
                                "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                                "taskId": "f1e2d3c4-b5a6-9876-5432-10fedcba9876",
                                "title": "Research requirements",
                                "completed": True,
                                "position": 0,
                                "createdAt": "2025-10-18T10:00:00Z",
                                "updatedAt": "2025-10-18T10:00:00Z"
                            }
                        ]
                    }
                ],
                "total": 1,
                "hasMore": False
            }
        }


class TaskStats(BaseModel):
    """Task statistics model"""
    total_tasks: int = Field(default=0, alias="totalTasks", ge=0, description="Total number of tasks")
    completed_tasks: int = Field(default=0, alias="completedTasks", ge=0, description="Number of completed tasks")
    active_tasks: int = Field(default=0, alias="activeTasks", ge=0, description="Number of active tasks")
    overdue_tasks: int = Field(default=0, alias="overdueTasks", ge=0, description="Number of overdue tasks")
    staging_tasks: int = Field(default=0, alias="stagingTasks", ge=0, description="Number of tasks in staging")
    quadrant_distribution: dict = Field(default_factory=dict, alias="quadrantDistribution", description="Task distribution by quadrant")

    class Config:
        populate_by_name = True


# Staging zone specific models
class StagingZoneStatus(BaseModel):
    """Staging zone status model"""
    current_count: int = Field(..., alias="currentCount", ge=0, le=5, description="Current number of items in staging")
    max_capacity: int = Field(5, alias="maxCapacity", description="Maximum staging zone capacity")
    is_full: bool = Field(..., alias="isFull", description="Whether staging zone is at capacity")
    oldest_item: Optional[dict] = Field(None, alias="oldestItem", description="Information about oldest staged item")
    processing_reminder: Optional[str] = Field(None, alias="processingReminder", description="Processing reminder message")

    class Config:
        populate_by_name = True


class StagingZoneResponse(BaseModel):
    """Staging zone response model"""
    status: StagingZoneStatus = Field(..., description="Staging zone status")
    tasks: List[Task] = Field(..., description="Tasks in staging zone")
    suggestions: List[str] = Field(default_factory=list, description="Organization suggestions")
