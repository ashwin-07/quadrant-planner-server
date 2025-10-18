"""
Tasks API routes
"""

import logging
from typing import Union, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from supabase import Client

from api.dependencies import (
    get_db, get_user_id_from_token, get_pagination_params, get_task_filters
)
from api.tasks.service import TasksService
from api.tasks.models import (
    Task, TaskCreate, TaskUpdate, TaskWithGoal, TaskMove, TaskToggle,
    TaskBulkUpdate, TasksListResponse, TaskStats, StagingZoneResponse,
    Subtask, SubtaskCreate, SubtaskUpdate
)
from api.shared.responses import success_response
from api.shared.exceptions import QuadrantPlannerException

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=TasksListResponse)
async def get_tasks(
    user_id: str = Depends(get_user_id_from_token),
    filters: dict = Depends(get_task_filters),
    pagination: Tuple[int, int] = Depends(get_pagination_params),
    include_goal: bool = Query(False, description="Include associated goal information"),
    db: Client = Depends(get_db)
):
    """
    Get user's tasks with filtering and pagination
    
    **Authentication**: Requires JWT Bearer token in Authorization header
    - **quadrant**: Filter by quadrant (Q1, Q2, Q3, Q4, staging)
    - **goal_id**: Filter by goal ID
    - **completed**: Filter by completion status
    - **is_staged**: Filter by staging status
    - **priority**: Filter by priority (low, medium, high, urgent)
    - **tags**: Filter by tags (comma-separated)
    - **limit**: Number of tasks to return (default: 100, max: 200)
    - **offset**: Number of tasks to skip (default: 0)
    - **include_goal**: Include goal information (default: false)
    """
    try:
        limit, offset = pagination
        service = TasksService(db)
        
        tasks, total, has_more = await service.get_tasks(
            user_id=user_id,
            quadrant=filters.get("quadrant"),
            goal_id=filters.get("goal_id"),
            completed=filters.get("completed"),
            is_staged=filters.get("is_staged"),
            priority=filters.get("priority"),
            tags=filters.get("tags"),
            limit=limit,
            offset=offset,
            include_goal=include_goal
        )
        
        return TasksListResponse(
            tasks=tasks,
            total=total,
            has_more=has_more
        )
            
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=Task, status_code=201)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_user_id_from_token),
    db: Client = Depends(get_db)
):
    """
    Create a new task
    
    **Authentication**: Requires JWT Bearer token in Authorization header
    
    - **title**: Task title (max 200 characters)
    - **description**: Task description (optional, max 1000 characters)
    - **goal_id**: Associated goal ID (optional)
    - **quadrant**: Task quadrant (Q1, Q2, Q3, Q4, staging)
    - **due_date**: Task due date (optional)
    - **estimated_minutes**: Estimated completion time (optional, 1-480 minutes)
    - **priority**: Task priority (low, medium, high, urgent)
    - **tags**: Task tags (optional, max 10 tags)
    """
    try:
        service = TasksService(db)
        task = await service.create_task(task_data, user_id)
        return task
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{task_id}", response_model=Union[Task, TaskWithGoal])
async def get_task(
    task_id: str = Path(..., description="Task ID"),
    user_id: str = Depends(get_user_id_from_token),
    include_goal: bool = Query(False, description="Include associated goal information"),
    db: Client = Depends(get_db)
):
    """
    Get a specific task by ID
    
    - **task_id**: Task unique identifier
    **Authentication**: Requires JWT Bearer token in Authorization header
    - **include_goal**: Include associated goal information (default: false)
    """
    try:
        service = TasksService(db)
        task = await service.get_task_by_id(
            task_id=task_id,
            user_id=user_id,
            include_goal=include_goal
        )
        
        return task
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_data: TaskUpdate,
    task_id: str = Path(..., description="Task ID"),
    user_id: str = Depends(get_user_id_from_token),
    db: Client = Depends(get_db)
):
    """
    Update an existing task
    
    **Authentication**: Requires JWT Bearer token in Authorization header
    
    - **task_id**: Task unique identifier
    - **title**: Task title (optional, max 200 characters)
    - **description**: Task description (optional, max 1000 characters)
    - **goal_id**: Associated goal ID (optional)
    - **quadrant**: Task quadrant (optional)
    - **due_date**: Task due date (optional)
    - **estimated_minutes**: Estimated completion time (optional)
    - **priority**: Task priority (optional)
    - **tags**: Task tags (optional)
    - **completed**: Completion status (optional)
    - **position**: Task position within quadrant (optional)
    """
    try:
        service = TasksService(db)
        task = await service.update_task(task_id, task_data, user_id)
        return task
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to update task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{task_id}", status_code=200)
async def delete_task(
    task_id: str = Path(..., description="Task ID"),
    user_id: str = Depends(get_user_id_from_token),
    db: Client = Depends(get_db)
):
    """
    Delete a task
    
    - **task_id**: Task unique identifier
    **Authentication**: Requires JWT Bearer token in Authorization header
    """
    try:
        service = TasksService(db)
        await service.delete_task(task_id, user_id)
        
        return success_response(
            data={"deleted": True, "task_id": task_id},
            message="Task deleted successfully"
        )
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{task_id}/toggle", response_model=Task)
async def toggle_task_completion(
    toggle_data: TaskToggle,
    task_id: str = Path(..., description="Task ID"),
    user_id: str = Depends(get_user_id_from_token),
    db: Client = Depends(get_db)
):
    """
    Toggle task completion status
    
    **Authentication**: Requires JWT Bearer token in Authorization header
    
    - **task_id**: Task unique identifier
    
    Toggles the completion status of the task and updates completion timestamp.
    """
    try:
        service = TasksService(db)
        task = await service.toggle_task_completion(task_id, user_id)
        
        return task
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle task completion {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{task_id}/move", response_model=Task)
async def move_task(
    move_data: TaskMove,
    task_id: str = Path(..., description="Task ID"),
    user_id: str = Depends(get_user_id_from_token),
    db: Client = Depends(get_db)
):
    """
    Move a task to a different quadrant/position (Drag & Drop)
    
    **Authentication**: Requires JWT Bearer token in Authorization header
    
    - **task_id**: Task unique identifier
    - **quadrant**: Target quadrant (Q1, Q2, Q3, Q4, staging)
    - **position**: Target position within quadrant
    - **is_staged**: Whether task is staged (optional)
    
    Moves a task between quadrants and updates staging-related timestamps.
    """
    try:
        service = TasksService(db)
        task = await service.move_task(task_id, move_data, user_id)
        
        return task
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to move task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/bulk", response_model=dict)
async def bulk_update_tasks(
    bulk_data: TaskBulkUpdate,
    user_id: str = Depends(get_user_id_from_token),
    db: Client = Depends(get_db)
):
    """
    Bulk update tasks (Drag & Drop Multiple)
    
    **Authentication**: Requires JWT Bearer token in Authorization header
    
    - **updates**: Array of task updates (max 50 items)
    
    Each update should contain:
    - **task_id**: Task unique identifier
    - **quadrant**: Target quadrant (optional)
    - **position**: Target position (optional)
    - **is_staged**: Staging status (optional)
    """
    try:
        service = TasksService(db)
        updated_tasks = []
        
        # Process each update
        for update in bulk_data.updates:
            task_id = update.get("task_id")
            if not task_id:
                continue
                
            move_data = TaskMove(
                quadrant=update.get("quadrant", "Q1"),
                position=update.get("position", 0),
                is_staged=update.get("is_staged")
            )
            
            try:
                updated_task = await service.move_task(task_id, move_data, user_id)
                updated_tasks.append({
                    "id": updated_task.id,
                    "quadrant": updated_task.quadrant,
                    "position": updated_task.position,
                    "is_staged": updated_task.is_staged,
                    "organized_at": updated_task.organized_at
                })
            except Exception as e:
                logger.warning(f"Failed to update task {task_id} in bulk operation: {e}")
                continue
        
        return success_response({
            "updated_tasks": updated_tasks,
            "total_updated": len(updated_tasks)
        }, "Tasks updated successfully")
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to bulk update tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/staging/status", response_model=StagingZoneResponse)
async def get_staging_zone(
    user_id: str = Depends(get_user_id_from_token),
    db: Client = Depends(get_db)
):
    """
    Get staging zone status and tasks
    
    **Authentication**: Requires JWT Bearer token in Authorization header
    
    Returns staging zone status including:
    - Current item count and capacity
    - Tasks in staging zone
    - Processing suggestions and reminders
    """
    try:
        service = TasksService(db)
        staging_zone = await service.get_staging_zone(user_id)
        
        return success_response(staging_zone)
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get staging zone: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats/summary", response_model=TaskStats)
async def get_task_stats(
    user_id: str = Depends(get_user_id_from_token),
    db: Client = Depends(get_db)
):
    """
    Get task statistics summary
    
    **Authentication**: Requires JWT Bearer token in Authorization header
    
    Returns comprehensive task statistics including:
    - Total, completed, active, and overdue task counts
    - Staging zone status
    - Quadrant distribution
    """
    try:
        service = TasksService(db)
        stats = await service.get_task_stats(user_id)
        
        return success_response(stats)
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# =====================================================
# SUBTASK ENDPOINTS
# =====================================================

@router.patch("/{task_id}/subtasks/{subtask_id}/toggle", response_model=dict)
async def toggle_subtask(
    task_id: str = Path(..., description="Task ID"),
    subtask_id: str = Path(..., description="Subtask ID"),
    user_id: str = Depends(get_user_id_from_token),
    db: Client = Depends(get_db)
):
    """
    Toggle subtask completion status
    
    **Authentication**: Requires JWT Bearer token in Authorization header
    
    - **task_id**: Parent task unique identifier
    - **subtask_id**: Subtask unique identifier
    
    Toggles the completion status of the subtask.
    """
    try:
        service = TasksService(db)
        subtask = await service.toggle_subtask_completion(task_id, subtask_id, user_id)
        
        return subtask
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to toggle subtask {subtask_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
