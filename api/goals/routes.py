"""
Goals API routes
"""

import logging
from typing import Union, Tuple, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from supabase import Client

from api.dependencies import (
    get_db, get_user_id_from_token, get_pagination_params, get_goal_filters
)
from api.goals.service import GoalsService
from api.goals.models import (
    Goal, GoalCreate, GoalUpdate, GoalWithStats, GoalWithTasks,
    GoalsListResponse, GoalsListWithStatsResponse, GoalStats
)
from api.shared.responses import success_response, paginated_response
from api.shared.exceptions import QuadrantPlannerException

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=Union[GoalsListResponse, GoalsListWithStatsResponse])
async def get_goals(
    user_id: str = Depends(get_user_id_from_token),
    filters: dict = Depends(get_goal_filters),
    pagination: Tuple[int, int] = Depends(get_pagination_params),
    include_stats: bool = Query(False, description="Include goal statistics"),
    db: Client = Depends(get_db)
):
    """
    Get user's goals with filtering and pagination
    
    **Authentication**: Requires JWT Bearer token in Authorization header
    
    - **category**: Filter by category (optional)
    - **archived**: Include archived goals (default: false)
    - **timeframe**: Filter by timeframe (optional)
    - **limit**: Number of goals to return (default: 50, max: 100)
    - **offset**: Number of goals to skip (default: 0)
    - **include_stats**: Include goal statistics (default: false)
    """
    try:
        limit, offset = pagination
        service = GoalsService(db)
        
        goals, total, has_more = await service.get_goals(
            user_id=user_id,
            category=filters.get("category"),
            archived=filters.get("archived", False),
            timeframe=filters.get("timeframe"),
            limit=limit,
            offset=offset,
            include_stats=include_stats
        )
        
        if include_stats:
            return GoalsListWithStatsResponse(
                goals=goals,
                total=total,
                has_more=has_more
            )
        else:
            return GoalsListResponse(
                goals=goals,
                total=total,
                has_more=has_more
            )
            
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get goals: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=Goal, status_code=201)
async def create_goal(
    goal_data: GoalCreate,
    user_id: str = Depends(get_user_id_from_token),
    db: Client = Depends(get_db)
):
    """
    Create a new goal
    
    **Authentication**: Requires JWT Bearer token in Authorization header
    
    - **title**: Goal title (max 200 characters)
    - **description**: Goal description (optional, max 1000 characters)
    - **category**: Goal category (career, health, relationships, learning, financial, personal)
    - **timeframe**: Goal timeframe (3_months, 6_months, 1_year, ongoing)
    - **color**: Goal color (optional, hex or color name)
    """
    try:
        service = GoalsService(db)
        goal = await service.create_goal(goal_data, user_id)
        return goal
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to create goal: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{goal_id}", response_model=Union[Goal, GoalWithTasks])
async def get_goal(
    goal_id: str = Path(..., description="Goal ID"),
    user_id: str = Depends(get_user_id_from_token),
    include_tasks: bool = Query(False, description="Include associated tasks"),
    db: Client = Depends(get_db)
):
    """
    Get a specific goal by ID
    
    - **goal_id**: Goal unique identifier
    - **user_id**: User identifier (required)
    - **include_tasks**: Include associated tasks (default: false)
    """
    try:
        service = GoalsService(db)
        goal = await service.get_goal_by_id(
            goal_id=goal_id,
            user_id=user_id,
            include_tasks=include_tasks
        )
        
        return success_response(goal)
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get goal {goal_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{goal_id}", response_model=Goal)
async def update_goal(
    goal_data: GoalUpdate,
    goal_id: str = Path(..., description="Goal ID"),
    user_id: str = Depends(get_user_id_from_token),
    db: Client = Depends(get_db)
):
    """
    Update an existing goal
    
    - **goal_id**: Goal unique identifier
    - **user_id**: User identifier
    - **title**: Goal title (optional, max 200 characters)
    - **description**: Goal description (optional, max 1000 characters)
    - **category**: Goal category (optional)
    - **timeframe**: Goal timeframe (optional)
    - **color**: Goal color (optional)
    - **archived**: Archive status (optional)
    """
    try:
        service = GoalsService(db)
        goal = await service.update_goal(goal_id, goal_data)
        return success_response(goal, "Goal updated successfully")
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to update goal {goal_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{goal_id}", status_code=200)
async def delete_goal(
    goal_id: str = Path(..., description="Goal ID"),
    user_id: str = Depends(get_user_id_from_token),
    db: Client = Depends(get_db)
):
    """
    Delete a goal (soft delete - archives the goal)
    
    - **goal_id**: Goal unique identifier
    - **user_id**: User identifier (required)
    
    Note: This operation archives the goal rather than permanently deleting it.
    Associated tasks will have their goal reference removed.
    """
    try:
        service = GoalsService(db)
        await service.delete_goal(goal_id, user_id)
        
        return success_response(
            data={"deleted": True, "goal_id": goal_id},
            message="Goal deleted successfully"
        )
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete goal {goal_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{goal_id}/stats", response_model=GoalStats)
async def get_goal_stats(
    goal_id: str = Path(..., description="Goal ID"),
    user_id: str = Depends(get_user_id_from_token),
    db: Client = Depends(get_db)
):
    """
    Get statistics for a specific goal
    
    - **goal_id**: Goal unique identifier
    - **user_id**: User identifier (required)
    
    Returns detailed statistics including:
    - Total, completed, and active tasks
    - Completion rate percentage
    - Average age of active tasks
    - Last activity timestamp
    """
    try:
        service = GoalsService(db)
        stats = await service.get_goal_stats(goal_id, user_id)
        
        return success_response(stats)
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get goal stats for {goal_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search", response_model=Union[GoalsListResponse, GoalsListWithStatsResponse])
async def search_goals(
    q: str = Query(..., min_length=2, max_length=100, description="Search query (minimum 2 characters)"),
    user_id: str = Depends(get_user_id_from_token),
    category: Optional[str] = Query(None, description="Filter by goal category"),
    archived: bool = Query(False, description="Include archived goals"),
    include_stats: bool = Query(False, description="Include goal statistics"),
    limit: int = Query(50, ge=1, le=200, description="Number of goals to return"),
    offset: int = Query(0, ge=0, description="Number of goals to skip"),
    db: Client = Depends(get_db)
):
    """
    Search goals by title
    
    **Authentication**: Requires JWT Bearer token in Authorization header
    
    - **q**: Search query (minimum 2 characters, maximum 100 characters)
    - **category**: Filter by goal category (optional)
    - **archived**: Include archived goals (default: false)
    - **include_stats**: Include goal statistics (default: false)
    - **limit**: Number of goals to return (default: 50, max: 200)
    - **offset**: Number of goals to skip (default: 0)
    
    Performs case-insensitive search on goal titles using PostgreSQL ilike.
    """
    try:
        service = GoalsService(db)
        goals, total, has_more = await service.search_goals(
            user_id=user_id,
            query=q,
            category=category,
            archived=archived,
            limit=limit,
            offset=offset,
            include_stats=include_stats
        )
        
        if include_stats:
            return GoalsListWithStatsResponse(
                goals=goals,
                total=total,
                has_more=has_more
            )
        else:
            return GoalsListResponse(
                goals=goals,
                total=total,
                has_more=has_more
            )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to search goals for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
