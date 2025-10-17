"""
Tasks service layer - Business logic for tasks management
"""

import logging
from typing import List, Optional, Dict, Any, Union, Tuple
from datetime import datetime
from supabase import Client
from api.tasks.models import (
    Task, TaskCreate, TaskUpdate, TaskWithGoal, TaskMove, 
    TaskToggle, TaskBulkUpdate, TaskStats, StagingZoneStatus, StagingZoneResponse
)
from api.shared.exceptions import NotFoundError, ConflictError, DatabaseError, ValidationError
from api.shared.validation import validate_user_id
from database.connection import get_service_client

logger = logging.getLogger(__name__)


class TasksService:
    """Service class for tasks business logic"""

    def __init__(self, db: Client):
        self.db = db

    async def get_tasks(
        self,
        user_id: str,
        quadrant: Optional[str] = None,
        goal_id: Optional[str] = None,
        completed: Optional[bool] = None,
        is_staged: Optional[bool] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
        include_goal: bool = False
    ) -> Tuple[List[Union[Task, TaskWithGoal]], int, bool]:
        """Get tasks for a user with filtering and pagination"""
        try:
            validate_user_id(user_id)
            
            # Use service client for read operations and set user context
            from database.connection import get_service_client
            service_db = get_service_client()
            
            # Set user context for RLS policies
            service_db.rpc('set_current_user_id', {'user_id_param': user_id}).execute()
            
            # Build query
            if include_goal:
                # Join with goals table for goal information
                query = service_db.table("tasks").select("""
                    *,
                    goal:goals(id, title, category, color)
                """)
            else:
                query = service_db.table("tasks").select("*")
            
            # Apply filters
            query = query.eq("user_id", user_id)
            
            if quadrant:
                query = query.eq("quadrant", quadrant)
            
            if goal_id:
                query = query.eq("goal_id", goal_id)
            
            if completed is not None:
                query = query.eq("completed", completed)
            
            if is_staged is not None:
                query = query.eq("is_staged", is_staged)
            
            if priority:
                query = query.eq("priority", priority)
            
            # Tags filtering (PostgreSQL array contains)
            if tags:
                for tag in tags:
                    query = query.contains("tags", [tag])
            
            # Get total count
            count_result = query.execute()
            total = len(count_result.data) if count_result.data else 0
            
            # Apply pagination and ordering
            query = query.order("position", desc=False).order("created_at", desc=True)
            query = query.range(offset, offset + limit - 1)
            
            result = query.execute()
            
            if not result.data:
                return [], total, False
            
            # Convert to Pydantic models
            tasks = []
            for task_data in result.data:
                if include_goal and task_data.get("goal"):
                    task = TaskWithGoal(**task_data)
                else:
                    task = Task(**task_data)
                tasks.append(task)
            
            has_more = len(result.data) == limit and (offset + limit) < total
            
            logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}")
            return tasks, total, has_more
            
        except Exception as e:
            logger.error(f"Failed to get tasks for user {user_id}: {e}")
            raise DatabaseError("Failed to retrieve tasks")

    async def get_task_by_id(
        self,
        task_id: str,
        user_id: str,
        include_goal: bool = False
    ) -> Union[Task, TaskWithGoal]:
        """Get a specific task by ID"""
        try:
            validate_user_id(user_id)
            
            # Use service client for read operations and set user context
            service_db = get_service_client()
            
            # Set user context for RLS policies
            service_db.rpc('set_current_user_id', {'user_id_param': user_id}).execute()
            
            if include_goal:
                query = service_db.table("tasks").select("""
                    *,
                    goal:goals(id, title, category, color)
                """)
            else:
                query = service_db.table("tasks").select("*")
            
            result = query.eq("id", task_id).eq("user_id", user_id).execute()
            
            if not result.data:
                raise NotFoundError("Task", task_id)
            
            task_data = result.data[0]
            
            if include_goal and task_data.get("goal"):
                return TaskWithGoal(**task_data)
            else:
                return Task(**task_data)
                
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            raise DatabaseError("Failed to retrieve task")

    async def create_task(self, task_data: TaskCreate, user_id: str) -> Task:
        """Create a new task"""
        try:
            # Check if user has reached the limit of 1000 tasks
            existing_count = await self._count_user_tasks(user_id)
            if existing_count >= 1000:
                raise ConflictError("Maximum of 1000 tasks allowed per user")
            
            # Check staging zone capacity if creating in staging
            if task_data.quadrant == "staging":
                staging_count = await self._count_staging_tasks(user_id)
                if staging_count >= 5:
                    raise ConflictError("Staging zone is full (maximum 5 items)")
            
            # Validate goal_id if provided
            if task_data.goal_id:
                await self._validate_goal_ownership(task_data.goal_id, user_id)
            
            # Prepare data for insertion
            insert_data = task_data.model_dump()
            insert_data['user_id'] = user_id
            
            # Set position if not provided
            if "position" not in insert_data:
                insert_data["position"] = await self._get_next_position(
                    user_id, task_data.quadrant
                )
            
            # Set staging-related fields
            if task_data.quadrant == "staging":
                insert_data["is_staged"] = True
                insert_data["staged_at"] = datetime.utcnow().isoformat()
            else:
                insert_data["is_staged"] = False
            
            # Use service client for write operations to bypass RLS
            from database.connection import get_service_client
            service_db = get_service_client()
            result = service_db.table("tasks").insert(insert_data).execute()
            
            if not result.data:
                raise DatabaseError("Failed to create task")
            
            created_task = Task(**result.data[0])
            logger.info(f"Created task {created_task.id} for user {user_id}")
            
            return created_task
            
        except (ConflictError, DatabaseError):
            raise
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise DatabaseError("Failed to create task")

    async def update_task(self, task_id: str, task_data: TaskUpdate, user_id: str) -> Task:
        """Update an existing task"""
        try:
            validate_user_id(user_id)
            
            # Verify task exists and belongs to user
            existing_task = await self.get_task_by_id(task_id, user_id)
            
            # Validate goal_id if provided
            if task_data.goal_id:
                await self._validate_goal_ownership(task_data.goal_id, user_id)
            
            # Prepare update data (only include non-None fields)
            update_data = {
                k: v for k, v in task_data.model_dump().items() 
                if v is not None
            }
            
            if not update_data:
                return existing_task
            
            # Handle quadrant changes
            if "quadrant" in update_data:
                new_quadrant = update_data["quadrant"]
                old_quadrant = existing_task.quadrant
                
                # Check staging zone capacity if moving to staging
                if new_quadrant == "staging" and old_quadrant != "staging":
                    staging_count = await self._count_staging_tasks(user_id)
                    if staging_count >= 5:
                        raise ConflictError("Staging zone is full (maximum 5 items)")
                
                # Update staging-related fields
                if new_quadrant == "staging" and old_quadrant != "staging":
                    update_data["is_staged"] = True
                    update_data["staged_at"] = datetime.utcnow().isoformat()
                elif new_quadrant != "staging" and old_quadrant == "staging":
                    update_data["is_staged"] = False
                    update_data["organized_at"] = datetime.utcnow().isoformat()
            
            # Handle completion status changes
            if "completed" in update_data:
                if update_data["completed"] and not existing_task.completed:
                    update_data["completed_at"] = datetime.utcnow().isoformat()
                elif not update_data["completed"] and existing_task.completed:
                    update_data["completed_at"] = None
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Use service client for write operations and set user context
            service_db = get_service_client()
            
            # Set user context for RLS policies
            service_db.rpc('set_current_user_id', {'user_id_param': user_id}).execute()
            
            result = service_db.table("tasks").update(update_data).eq("id", task_id).eq("user_id", user_id).execute()
            
            if not result.data:
                raise DatabaseError("Failed to update task")
            
            updated_task = Task(**result.data[0])
            logger.info(f"Updated task {task_id} for user {user_id}")
            
            return updated_task
            
        except (NotFoundError, ConflictError, DatabaseError):
            raise
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            raise DatabaseError("Failed to update task")

    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete a task"""
        try:
            validate_user_id(user_id)
            
            # Verify task exists and belongs to user
            await self.get_task_by_id(task_id, user_id)
            
            # Use service client for write operations and set user context
            from database.connection import get_service_client
            service_db = get_service_client()
            
            # Set user context for RLS policies
            service_db.rpc('set_current_user_id', {'user_id_param': user_id}).execute()
            
            result = service_db.table("tasks").delete().eq("id", task_id).eq("user_id", user_id).execute()
            
            if not result.data:
                raise DatabaseError("Failed to delete task")
            
            logger.info(f"Deleted task {task_id} for user {user_id}")
            return True
            
        except (NotFoundError, DatabaseError):
            raise
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            raise DatabaseError("Failed to delete task")

    async def toggle_task_completion(self, task_id: str, user_id: str) -> Task:
        """Toggle task completion status"""
        try:
            validate_user_id(user_id)
            
            # Get current task
            task = await self.get_task_by_id(task_id, user_id)
            
            # Toggle completion
            new_completed = not task.completed
            update_data = {
                "completed": new_completed,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if new_completed:
                update_data["completed_at"] = datetime.utcnow().isoformat()
            else:
                update_data["completed_at"] = None
            
            # Use service client for write operations and set user context
            service_db = get_service_client()
            
            # Set user context for RLS policies
            service_db.rpc('set_current_user_id', {'user_id_param': user_id}).execute()
            
            result = service_db.table("tasks").update(update_data).eq("id", task_id).eq("user_id", user_id).execute()
            
            if not result.data:
                raise DatabaseError("Failed to toggle task completion")
            
            updated_task = Task(**result.data[0])
            logger.info(f"Toggled completion for task {task_id} to {new_completed}")
            
            return updated_task
            
        except (NotFoundError, DatabaseError):
            raise
        except Exception as e:
            logger.error(f"Failed to toggle task completion {task_id}: {e}")
            raise DatabaseError("Failed to toggle task completion")

    async def move_task(self, task_id: str, move_data: TaskMove, user_id: str) -> Task:
        """Move a task to a different quadrant/position"""
        try:
            validate_user_id(user_id)
            
            # Get current task
            task = await self.get_task_by_id(task_id, user_id)
            
            # Check staging zone capacity if moving to staging
            if move_data.quadrant == "staging" and task.quadrant != "staging":
                staging_count = await self._count_staging_tasks(user_id)
                if staging_count >= 5:
                    raise ConflictError("Staging zone is full (maximum 5 items)")
            
            # Prepare update data
            update_data = {
                "quadrant": move_data.quadrant,
                "position": move_data.position,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Update staging-related fields
            if move_data.quadrant == "staging" and task.quadrant != "staging":
                update_data["is_staged"] = True
                update_data["staged_at"] = datetime.utcnow().isoformat()
            elif move_data.quadrant != "staging" and task.quadrant == "staging":
                update_data["is_staged"] = False
                update_data["organized_at"] = datetime.utcnow().isoformat()
            
            # Use service client for write operations and set user context
            service_db = get_service_client()
            
            # Set user context for RLS policies
            service_db.rpc('set_current_user_id', {'user_id_param': user_id}).execute()
            
            result = service_db.table("tasks").update(update_data).eq("id", task_id).eq("user_id", user_id).execute()
            
            if not result.data:
                raise DatabaseError("Failed to move task")
            
            # Update positions of other tasks in the target quadrant
            await self._reorder_tasks_in_quadrant(
                user_id, move_data.quadrant, task_id, move_data.position
            )
            
            moved_task = Task(**result.data[0])
            logger.info(f"Moved task {task_id} to {move_data.quadrant} at position {move_data.position}")
            
            return moved_task
            
        except (NotFoundError, ConflictError, DatabaseError):
            raise
        except Exception as e:
            logger.error(f"Failed to move task {task_id}: {e}")
            raise DatabaseError("Failed to move task")

    async def get_staging_zone(self, user_id: str) -> StagingZoneResponse:
        """Get staging zone status and tasks"""
        try:
            validate_user_id(user_id)
            
            # Get staging tasks
            staging_tasks, _, _ = await self.get_tasks(
                user_id=user_id,
                quadrant="staging",
                completed=False,
                limit=5
            )
            
            # Calculate status
            current_count = len(staging_tasks)
            is_full = current_count >= 5
            
            # Find oldest item
            oldest_item = None
            if staging_tasks:
                oldest_task = min(staging_tasks, key=lambda t: t.staged_at or t.created_at)
                days_since_staged = (datetime.utcnow() - (oldest_task.staged_at or oldest_task.created_at)).days
                oldest_item = {
                    "task_id": oldest_task.id,
                    "title": oldest_task.title,
                    "days_since_staged": days_since_staged
                }
            
            # Generate processing reminder
            processing_reminder = None
            if current_count >= 3:
                processing_reminder = f"You have {current_count} items staged. Consider organizing them into quadrants."
            elif oldest_item and oldest_item["days_since_staged"] > 5:
                processing_reminder = f"You have items staged for {oldest_item['days_since_staged']} days. Time to organize them!"
            
            # Generate suggestions
            suggestions = []
            if current_count >= 4:
                suggestions.append("Your staging zone is almost full. Process some items to make room.")
            if oldest_item and oldest_item["days_since_staged"] > 3:
                suggestions.append("Consider organizing older staged items into appropriate quadrants.")
            if current_count == 0:
                suggestions.append("Stage quick thoughts here, then organize into quadrants.")
            
            status = StagingZoneStatus(
                current_count=current_count,
                max_capacity=5,
                is_full=is_full,
                oldest_item=oldest_item,
                processing_reminder=processing_reminder
            )
            
            return StagingZoneResponse(
                status=status,
                tasks=staging_tasks,
                suggestions=suggestions
            )
            
        except Exception as e:
            logger.error(f"Failed to get staging zone for user {user_id}: {e}")
            raise DatabaseError("Failed to retrieve staging zone")

    async def get_task_stats(self, user_id: str) -> TaskStats:
        """Get task statistics for a user"""
        try:
            validate_user_id(user_id)
            
            # Get all tasks
            all_tasks, _, _ = await self.get_tasks(user_id=user_id, limit=1000)
            
            total_tasks = len(all_tasks)
            completed_tasks = len([t for t in all_tasks if t.completed])
            active_tasks = total_tasks - completed_tasks
            
            # Count overdue tasks
            now = datetime.utcnow()
            overdue_tasks = len([
                t for t in all_tasks 
                if not t.completed and t.due_date and t.due_date < now
            ])
            
            # Count staging tasks
            staging_tasks = len([t for t in all_tasks if t.quadrant == "staging" and not t.completed])
            
            # Calculate quadrant distribution
            quadrant_distribution = {
                "Q1": len([t for t in all_tasks if t.quadrant == "Q1" and not t.completed]),
                "Q2": len([t for t in all_tasks if t.quadrant == "Q2" and not t.completed]),
                "Q3": len([t for t in all_tasks if t.quadrant == "Q3" and not t.completed]),
                "Q4": len([t for t in all_tasks if t.quadrant == "Q4" and not t.completed]),
                "staging": staging_tasks
            }
            
            return TaskStats(
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                active_tasks=active_tasks,
                overdue_tasks=overdue_tasks,
                staging_tasks=staging_tasks,
                quadrant_distribution=quadrant_distribution
            )
            
        except Exception as e:
            logger.error(f"Failed to get task stats for user {user_id}: {e}")
            raise DatabaseError("Failed to retrieve task statistics")

    # Private helper methods

    async def _count_user_tasks(self, user_id: str) -> int:
        """Count tasks for a user"""
        result = self.db.table("tasks").select("count", count="exact").eq("user_id", user_id).execute()
        return result.count or 0

    async def _count_staging_tasks(self, user_id: str) -> int:
        """Count tasks in staging zone for a user"""
        result = self.db.table("tasks").select("count", count="exact").eq("user_id", user_id).eq("quadrant", "staging").eq("completed", False).execute()
        return result.count or 0

    async def _get_next_position(self, user_id: str, quadrant: str) -> int:
        """Get the next position for a task in a quadrant"""
        try:
            result = self.db.table("tasks").select("position").eq("user_id", user_id).eq("quadrant", quadrant).order("position", desc=True).limit(1).execute()
            
            if result.data:
                return result.data[0]["position"] + 1
            return 0
        except Exception:
            return 0

    async def _validate_goal_ownership(self, goal_id: str, user_id: str) -> None:
        """Validate that a goal exists and belongs to the user"""
        try:
            service_db = get_service_client()
            service_db.rpc('set_current_user_id', {'user_id_param': user_id}).execute()
            
            result = service_db.table("goals").select("id").eq("id", goal_id).eq("user_id", user_id).execute()
            
            if not result.data:
                raise NotFoundError("Goal", goal_id)
                
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to validate goal ownership for goal {goal_id}: {e}")
            raise DatabaseError("Failed to validate goal ownership")

    async def _reorder_tasks_in_quadrant(self, user_id: str, quadrant: str, moved_task_id: str, new_position: int) -> None:
        """Reorder tasks in a quadrant after a move"""
        try:
            # Get all tasks in the quadrant
            tasks_result = self.db.table("tasks").select("id, position").eq("user_id", user_id).eq("quadrant", quadrant).order("position").execute()
            
            if not tasks_result.data:
                return
            
            # Update positions for tasks that need to shift
            for task in tasks_result.data:
                if task["id"] != moved_task_id and task["position"] >= new_position:
                    new_pos = task["position"] + 1
                    self.db.table("tasks").update({"position": new_pos}).eq("id", task["id"]).execute()
                    
        except Exception as e:
            logger.warning(f"Failed to reorder tasks in quadrant {quadrant}: {e}")
            # Don't raise here as the main operation was successful
