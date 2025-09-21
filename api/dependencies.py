"""
FastAPI dependencies for the Quadrant Planner API
"""

from typing import Optional, Tuple
from fastapi import Depends, Query, Header, HTTPException
from supabase import Client
from database.connection import get_supabase_client, db_manager
from api.shared.exceptions import ValidationError, UnauthorizedError
from api.shared.validation import validate_user_id, validate_pagination
from api.auth.jwt_handler import get_current_user_from_token, get_current_user_info


def get_db() -> Client:
    """Dependency to get database client"""
    return get_supabase_client()


def get_user_id_from_query(user_id: str = Query(..., description="User identifier")) -> str:
    """Extract and validate user ID from query parameters (DEPRECATED - use JWT auth)"""
    return validate_user_id(user_id)


async def get_user_id_from_token(authorization: str = Header(..., description="Authorization header with Bearer token")) -> str:
    """Extract and validate user ID from JWT Bearer token"""
    return await get_current_user_from_token(authorization)


async def get_user_info_from_token(authorization: str = Header(..., description="Authorization header with Bearer token")) -> dict:
    """Extract full user info from JWT Bearer token"""
    return await get_current_user_info(authorization)


def get_user_id_from_header(user_id: Optional[str] = Header(None, alias="X-User-ID")) -> str:
    """Extract and validate user ID from header"""
    if not user_id:
        raise UnauthorizedError("User ID header is required")
    return validate_user_id(user_id)


def get_pagination_params(
    limit: Optional[int] = Query(None, ge=1, le=200, description="Number of items to return"),
    offset: Optional[int] = Query(None, ge=0, description="Number of items to skip")
) -> Tuple[int, int]:
    """Get and validate pagination parameters"""
    return validate_pagination(limit, offset)


def get_goal_filters(
    category: Optional[str] = Query(None, description="Filter by goal category"),
    archived: Optional[bool] = Query(False, description="Include archived goals"),
    timeframe: Optional[str] = Query(None, description="Filter by goal timeframe")
) -> dict:
    """Get goal filtering parameters"""
    filters = {}
    
    if category:
        allowed_categories = ['career', 'health', 'relationships', 'learning', 'financial', 'personal']
        if category not in allowed_categories:
            raise ValidationError(f"Invalid category. Must be one of: {', '.join(allowed_categories)}")
        filters['category'] = category
    
    if timeframe:
        allowed_timeframes = ['3_months', '6_months', '1_year', 'ongoing']
        if timeframe not in allowed_timeframes:
            raise ValidationError(f"Invalid timeframe. Must be one of: {', '.join(allowed_timeframes)}")
        filters['timeframe'] = timeframe
    
    filters['archived'] = archived
    return filters


def get_task_filters(
    quadrant: Optional[str] = Query(None, description="Filter by task quadrant"),
    goal_id: Optional[str] = Query(None, description="Filter by goal ID"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    is_staged: Optional[bool] = Query(None, description="Filter by staging status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)")
) -> dict:
    """Get task filtering parameters"""
    filters = {}
    
    if quadrant:
        allowed_quadrants = ['Q1', 'Q2', 'Q3', 'Q4', 'staging']
        if quadrant not in allowed_quadrants:
            raise ValidationError(f"Invalid quadrant. Must be one of: {', '.join(allowed_quadrants)}")
        filters['quadrant'] = quadrant
    
    if goal_id:
        filters['goal_id'] = goal_id
    
    if completed is not None:
        filters['completed'] = completed
    
    if is_staged is not None:
        filters['is_staged'] = is_staged
    
    if priority:
        allowed_priorities = ['low', 'medium', 'high', 'urgent']
        if priority not in allowed_priorities:
            raise ValidationError(f"Invalid priority. Must be one of: {', '.join(allowed_priorities)}")
        filters['priority'] = priority
    
    if tags:
        # Convert comma-separated tags to list
        filters['tags'] = [tag.strip() for tag in tags.split(',') if tag.strip()]
    
    return filters


def get_analytics_params(
    period: Optional[str] = Query("week", description="Analytics period"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> dict:
    """Get analytics filtering parameters"""
    allowed_periods = ['week', 'month', 'quarter', 'year']
    if period not in allowed_periods:
        raise ValidationError(f"Invalid period. Must be one of: {', '.join(allowed_periods)}")
    
    params = {'period': period}
    
    if start_date:
        params['start_date'] = start_date
    
    if end_date:
        params['end_date'] = end_date
    
    return params


def get_task_filters(
    quadrant: Optional[str] = Query(None, description="Filter by task quadrant"),
    goal_id: Optional[str] = Query(None, description="Filter by goal ID"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    is_staged: Optional[bool] = Query(None, description="Filter by staging status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)")
) -> dict:
    """Get task filtering parameters"""
    filters = {}
    
    if quadrant:
        allowed_quadrants = ['Q1', 'Q2', 'Q3', 'Q4', 'staging']
        if quadrant not in allowed_quadrants:
            raise ValidationError(f"Invalid quadrant. Must be one of: {', '.join(allowed_quadrants)}")
        filters['quadrant'] = quadrant
    
    if goal_id:
        filters['goal_id'] = goal_id
    
    if completed is not None:
        filters['completed'] = completed
    
    if is_staged is not None:
        filters['is_staged'] = is_staged
    
    if priority:
        allowed_priorities = ['low', 'medium', 'high', 'urgent']
        if priority not in allowed_priorities:
            raise ValidationError(f"Invalid priority. Must be one of: {', '.join(allowed_priorities)}")
        filters['priority'] = priority
    
    if tags:
        # Convert comma-separated tags to list
        filters['tags'] = [tag.strip() for tag in tags.split(',') if tag.strip()]
    
    return filters


async def verify_goal_ownership(goal_id: str, user_id: str, db: Client = Depends(get_db)) -> bool:
    """Verify that a goal belongs to the user"""
    try:
        result = db.table("goals").select("id").eq("id", goal_id).eq("user_id", user_id).execute()
        return len(result.data) > 0
    except Exception:
        return False


async def verify_task_ownership(task_id: str, user_id: str, db: Client = Depends(get_db)) -> bool:
    """Verify that a task belongs to the user"""
    try:
        result = db.table("tasks").select("id").eq("id", task_id).eq("user_id", user_id).execute()
        return len(result.data) > 0
    except Exception:
        return False


class CommonDependencies:
    """Common dependencies for API endpoints"""
    
    def __init__(
        self,
        user_id: str = Depends(get_user_id_from_token),  # Use JWT auth by default
        db: Client = Depends(get_db),
        pagination: Tuple[int, int] = Depends(get_pagination_params)
    ):
        self.user_id = user_id
        self.db = db
        self.limit, self.offset = pagination


class CommonDependenciesLegacy:
    """Legacy dependencies using query parameters (DEPRECATED)"""
    
    def __init__(
        self,
        user_id: str = Depends(get_user_id_from_query),
        db: Client = Depends(get_db),
        pagination: Tuple[int, int] = Depends(get_pagination_params)
    ):
        self.user_id = user_id
        self.db = db
        self.limit, self.offset = pagination
