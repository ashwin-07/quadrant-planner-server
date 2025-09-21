"""
Goals service layer - Business logic for goals management
"""

import logging
from typing import List, Optional, Dict, Any, Union, Tuple
from datetime import datetime
from supabase import Client
from api.goals.models import (
    Goal, GoalCreate, GoalUpdate, GoalWithStats, GoalWithTasks,
    GoalStats, TaskSummary
)
from api.shared.exceptions import NotFoundError, ConflictError, DatabaseError
from api.shared.validation import validate_user_id

logger = logging.getLogger(__name__)


class GoalsService:
    """Service class for goals business logic"""

    def __init__(self, db: Client):
        self.db = db

    async def get_goals(
        self,
        user_id: str,
        category: Optional[str] = None,
        archived: bool = False,
        timeframe: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        include_stats: bool = False
    ) -> Tuple[List[Union[Goal, GoalWithStats]], int, bool]:
        """Get goals for a user with filtering and pagination"""
        try:
            validate_user_id(user_id)
            
            # Use service client for read operations and set user context
            from database.connection import get_service_client
            service_db = get_service_client()
            
            # Set user context for RLS policies
            service_db.rpc('set_current_user_id', {'user_id_param': user_id}).execute()
            
            # Build query
            query = service_db.table("goals").select("*")
            
            # Apply filters
            query = query.eq("user_id", user_id)
            query = query.eq("archived", archived)
            
            if category:
                query = query.eq("category", category)
            
            if timeframe:
                query = query.eq("timeframe", timeframe)
            
            # Get total count
            count_result = query.execute()
            total = len(count_result.data) if count_result.data else 0
            
            # Apply pagination and ordering
            query = query.order("created_at", desc=True)
            query = query.range(offset, offset + limit - 1)
            
            result = query.execute()
            
            if not result.data:
                return [], total, False
            
            # Convert to Pydantic models
            goals = []
            if include_stats:
                # Get goals with statistics
                for goal_data in result.data:
                    goal_with_stats = await self._get_goal_with_stats(goal_data)
                    goals.append(goal_with_stats)
            else:
                goals = [Goal(**goal_data) for goal_data in result.data]
            
            has_more = len(result.data) == limit and (offset + limit) < total
            
            logger.info(f"Retrieved {len(goals)} goals for user {user_id}")
            return goals, total, has_more
            
        except Exception as e:
            logger.error(f"Failed to get goals for user {user_id}: {e}")
            raise DatabaseError("Failed to retrieve goals")

    async def search_goals(
        self,
        user_id: str,
        query: str,
        category: Optional[str] = None,
        archived: bool = False,
        limit: int = 50,
        offset: int = 0,
        include_stats: bool = False
    ) -> Tuple[List[Union[Goal, GoalWithStats]], int, bool]:
        """Search goals by title for a user with filtering and pagination"""
        try:
            validate_user_id(user_id)
            
            if not query or len(query.strip()) < 2:
                raise ValueError("Search query must be at least 2 characters long")
            
            # Use service client for read operations and set user context
            from database.connection import get_service_client
            service_db = get_service_client()
            
            # Set user context for RLS policies
            service_db.rpc('set_current_user_id', {'user_id_param': user_id}).execute()
            
            # Build query with text search
            if include_stats:
                # Join with tasks for stats
                db_query = service_db.table("goals").select("""
                    *,
                    tasks:tasks(id, completed, created_at, completed_at)
                """)
            else:
                db_query = service_db.table("goals").select("*")
            
            # Apply filters
            db_query = db_query.eq("user_id", user_id)
            
            # Text search using PostgreSQL ilike (case-insensitive)
            db_query = db_query.ilike("title", f"%{query.strip()}%")
            
            if category:
                db_query = db_query.eq("category", category)
            
            if archived is not None:
                db_query = db_query.eq("archived", archived)
            
            # Get total count for pagination
            count_result = db_query.execute()
            total = len(count_result.data) if count_result.data else 0
            
            # Apply pagination and ordering
            db_query = db_query.order("created_at", desc=True)
            db_query = db_query.range(offset, offset + limit - 1)
            
            result = db_query.execute()
            
            if not result.data:
                return [], 0, False
            
            goals_data = result.data
            
            if include_stats:
                goals = [self._get_goal_with_stats(goal_data) for goal_data in goals_data]
            else:
                goals = [Goal(**goal_data) for goal_data in goals_data]
            
            has_more = (offset + limit) < total
            
            logger.info(f"Found {len(goals)} goals matching '{query}' for user {user_id}")
            return goals, total, has_more
            
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            logger.error(f"Failed to search goals for user {user_id}: {e}")
            raise DatabaseError("Failed to search goals")

    async def get_goal_by_id(
        self,
        goal_id: str,
        user_id: str,
        include_tasks: bool = False
    ) -> Union[Goal, GoalWithTasks]:
        """Get a specific goal by ID"""
        try:
            validate_user_id(user_id)
            
            # Use service client for read operations and set user context
            from database.connection import get_service_client
            service_db = get_service_client()
            
            # Set user context for RLS policies
            service_db.rpc('set_current_user_id', {'user_id_param': user_id}).execute()
            
            result = service_db.table("goals").select("*").eq("id", goal_id).eq("user_id", user_id).execute()
            
            if not result.data:
                raise NotFoundError("Goal", goal_id)
            
            goal_data = result.data[0]
            
            if include_tasks:
                return await self._get_goal_with_tasks(goal_data)
            else:
                return Goal(**goal_data)
                
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get goal {goal_id}: {e}")
            raise DatabaseError("Failed to retrieve goal")

    async def create_goal(self, goal_data: GoalCreate, user_id: str) -> Goal:
        """Create a new goal"""
        try:
            # Check if user has reached the limit of 100 goals
            existing_count = await self._count_user_goals(user_id, archived=False)
            if existing_count >= 100:
                raise ConflictError("Maximum of 100 active goals allowed per user")
            
            # Prepare data for insertion
            insert_data = goal_data.model_dump()
            insert_data['user_id'] = user_id
            
            # Use service client for write operations to bypass RLS
            from database.connection import get_service_client
            service_db = get_service_client()
            result = service_db.table("goals").insert(insert_data).execute()
            
            if not result.data:
                raise DatabaseError("Failed to create goal")
            
            created_goal = Goal(**result.data[0])
            logger.info(f"Created goal {created_goal.id} for user {user_id}")
            
            return created_goal
            
        except (ConflictError, DatabaseError):
            raise
        except Exception as e:
            logger.error(f"Failed to create goal: {e}")
            raise DatabaseError("Failed to create goal")

    async def update_goal(self, goal_id: str, goal_data: GoalUpdate) -> Goal:
        """Update an existing goal"""
        try:
            # Verify goal exists and belongs to user
            existing_goal = await self.get_goal_by_id(goal_id, goal_data.user_id)
            
            # Prepare update data (only include non-None fields)
            update_data = {
                k: v for k, v in goal_data.model_dump().items() 
                if v is not None and k != "user_id"
            }
            
            if not update_data:
                return existing_goal
            
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Use service client for write operations and set user context
            from database.connection import get_service_client
            service_db = get_service_client()
            
            # Set user context for RLS policies
            service_db.rpc('set_current_user_id', {'user_id_param': goal_data.user_id}).execute()
            
            result = service_db.table("goals").update(update_data).eq("id", goal_id).eq("user_id", goal_data.user_id).execute()
            
            if not result.data:
                raise DatabaseError("Failed to update goal")
            
            updated_goal = Goal(**result.data[0])
            logger.info(f"Updated goal {goal_id} for user {goal_data.user_id}")
            
            return updated_goal
            
        except (NotFoundError, DatabaseError):
            raise
        except Exception as e:
            logger.error(f"Failed to update goal {goal_id}: {e}")
            raise DatabaseError("Failed to update goal")

    async def delete_goal(self, goal_id: str, user_id: str) -> bool:
        """Delete a goal (soft delete by archiving)"""
        try:
            validate_user_id(user_id)
            
            # Verify goal exists and belongs to user
            await self.get_goal_by_id(goal_id, user_id)
            
            # Use service client for write operations and set user context
            from database.connection import get_service_client
            service_db = get_service_client()
            
            # Set user context for RLS policies
            service_db.rpc('set_current_user_id', {'user_id_param': user_id}).execute()
            
            # Soft delete by archiving
            update_data = {
                "archived": True,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = service_db.table("goals").update(update_data).eq("id", goal_id).eq("user_id", user_id).execute()
            
            if not result.data:
                raise DatabaseError("Failed to delete goal")
            
            # Update associated tasks to remove goal reference
            await self._handle_goal_deletion(goal_id, user_id)
            
            logger.info(f"Deleted goal {goal_id} for user {user_id}")
            return True
            
        except (NotFoundError, DatabaseError):
            raise
        except Exception as e:
            logger.error(f"Failed to delete goal {goal_id}: {e}")
            raise DatabaseError("Failed to delete goal")

    async def get_goal_stats(self, goal_id: str, user_id: str) -> GoalStats:
        """Get statistics for a specific goal"""
        try:
            validate_user_id(user_id)
            
            # Verify goal exists and belongs to user
            await self.get_goal_by_id(goal_id, user_id)
            
            # Get task statistics
            tasks_result = self.db.table("tasks").select("*").eq("goal_id", goal_id).eq("user_id", user_id).execute()
            
            tasks = tasks_result.data or []
            
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.get("completed", False)])
            active_tasks = total_tasks - completed_tasks
            
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
            
            # Calculate average task age for active tasks
            average_task_age = None
            last_activity_at = None
            
            if active_tasks > 0:
                now = datetime.utcnow()
                active_task_ages = []
                activity_dates = []
                
                for task in tasks:
                    if not task.get("completed", False):
                        created_at = datetime.fromisoformat(task["created_at"].replace("Z", "+00:00"))
                        age_days = (now - created_at).days
                        active_task_ages.append(age_days)
                    
                    if task.get("updated_at"):
                        updated_at = datetime.fromisoformat(task["updated_at"].replace("Z", "+00:00"))
                        activity_dates.append(updated_at)
                
                if active_task_ages:
                    average_task_age = sum(active_task_ages) / len(active_task_ages)
                
                if activity_dates:
                    last_activity_at = max(activity_dates)
            
            return GoalStats(
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                active_tasks=active_tasks,
                completion_rate=round(completion_rate, 2),
                average_task_age=round(average_task_age, 1) if average_task_age else None,
                last_activity_at=last_activity_at
            )
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get goal stats for {goal_id}: {e}")
            raise DatabaseError("Failed to retrieve goal statistics")

    # Private helper methods

    async def _count_user_goals(self, user_id: str, archived: bool = False) -> int:
        """Count goals for a user"""
        result = self.db.table("goals").select("count", count="exact").eq("user_id", user_id).eq("archived", archived).execute()
        return result.count or 0

    async def _get_goal_with_stats(self, goal_data: Dict[str, Any]) -> GoalWithStats:
        """Convert goal data to GoalWithStats model"""
        goal = Goal(**goal_data)
        stats = await self.get_goal_stats(goal.id, goal.user_id)
        
        return GoalWithStats(
            **goal.model_dump(),
            total_tasks=stats.total_tasks,
            completed_tasks=stats.completed_tasks,
            active_tasks=stats.active_tasks,
            completion_rate=stats.completion_rate,
            average_task_age=stats.average_task_age,
            last_activity_at=stats.last_activity_at
        )

    async def _get_goal_with_tasks(self, goal_data: Dict[str, Any]) -> GoalWithTasks:
        """Convert goal data to GoalWithTasks model"""
        goal = Goal(**goal_data)
        
        # Get associated tasks
        tasks_result = self.db.table("tasks").select("id, title, completed, quadrant").eq("goal_id", goal.id).eq("user_id", goal.user_id).execute()
        
        tasks = [TaskSummary(**task_data) for task_data in (tasks_result.data or [])]
        stats = await self.get_goal_stats(goal.id, goal.user_id)
        
        return GoalWithTasks(
            **goal.model_dump(),
            tasks=tasks,
            stats=stats
        )

    async def _handle_goal_deletion(self, goal_id: str, user_id: str) -> None:
        """Handle cleanup when a goal is deleted"""
        try:
            # Set goal_id to null for associated tasks instead of deleting them
            update_data = {
                "goal_id": None,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            self.db.table("tasks").update(update_data).eq("goal_id", goal_id).eq("user_id", user_id).execute()
            
            logger.info(f"Updated tasks for deleted goal {goal_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle goal deletion cleanup: {e}")
            # Don't raise here as the goal deletion was successful
