"""
Analytics API routes
"""

import logging
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from api.dependencies import get_db, get_user_id_from_query
from api.analytics.service import AnalyticsService
from api.analytics.models import (
    AnalyticsDashboard, DateRange, GoalProgressResponse, QuadrantAnalysisResponse,
    ProductivityInsightsResponse, QuadrantDistribution, UserProductivityScore
)
from api.shared.responses import success_response
from api.shared.exceptions import QuadrantPlannerException

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/dashboard", response_model=AnalyticsDashboard)
async def get_analytics_dashboard(
    user_id: str = Depends(get_user_id_from_query),
    period: str = Query("30_days", description="Analysis period (7_days, 30_days, 90_days, 1_year)"),
    start_date: Optional[date] = Query(None, description="Custom start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Custom end date (YYYY-MM-DD)"),
    db: Client = Depends(get_db)
):
    """
    Get comprehensive analytics dashboard
    
    - **user_id**: User identifier (required)
    - **period**: Predefined analysis period (default: 30_days)
    - **start_date**: Custom start date (optional, overrides period)
    - **end_date**: Custom end date (optional, overrides period)
    
    Returns complete analytics including:
    - Goal progress summaries
    - Task quadrant distribution
    - Productivity trends
    - Category and timeframe analysis
    - Overdue task analysis
    - Completion velocity
    - Staging zone analytics
    - Productivity score with recommendations
    """
    try:
        service = AnalyticsService(db)
        
        # Create date range if custom dates provided
        date_range = None
        if start_date or end_date:
            date_range = DateRange(start_date=start_date, end_date=end_date)
        
        dashboard = await service.get_dashboard(
            user_id=user_id,
            period=period,
            date_range=date_range
        )
        
        return success_response(dashboard)
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analytics dashboard: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/goals/progress", response_model=GoalProgressResponse)
async def get_goal_progress(
    user_id: str = Depends(get_user_id_from_query),
    start_date: Optional[date] = Query(None, description="Filter goals created after this date"),
    end_date: Optional[date] = Query(None, description="Filter goals created before this date"),
    db: Client = Depends(get_db)
):
    """
    Get goal progress analytics
    
    - **user_id**: User identifier (required)
    - **start_date**: Filter goals created after this date (optional)
    - **end_date**: Filter goals created before this date (optional)
    
    Returns detailed progress information for all goals including:
    - Task completion rates
    - Average task age
    - Last activity timestamps
    - Overall completion statistics
    """
    try:
        service = AnalyticsService(db)
        
        date_range = None
        if start_date or end_date:
            date_range = DateRange(start_date=start_date, end_date=end_date)
        
        progress = await service.get_goal_progress(user_id, date_range)
        
        return success_response(progress)
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get goal progress: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/quadrants/analysis", response_model=QuadrantAnalysisResponse)
async def get_quadrant_analysis(
    user_id: str = Depends(get_user_id_from_query),
    db: Client = Depends(get_db)
):
    """
    Get quadrant distribution analysis with recommendations
    
    - **user_id**: User identifier (required)
    
    Returns:
    - Current task distribution across quadrants
    - Percentage breakdown
    - Optimization recommendations
    - Ideal distribution targets
    """
    try:
        service = AnalyticsService(db)
        analysis = await service.get_quadrant_analysis(user_id)
        
        return success_response(analysis)
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get quadrant analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/quadrants/distribution", response_model=QuadrantDistribution)
async def get_quadrant_distribution(
    user_id: str = Depends(get_user_id_from_query),
    db: Client = Depends(get_db)
):
    """
    Get current quadrant distribution
    
    - **user_id**: User identifier (required)
    
    Returns task counts and percentages for each quadrant (Q1-Q4, staging)
    """
    try:
        service = AnalyticsService(db)
        distribution = await service.get_quadrant_distribution(user_id)
        
        return success_response(distribution)
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get quadrant distribution: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/productivity/insights", response_model=ProductivityInsightsResponse)
async def get_productivity_insights(
    user_id: str = Depends(get_user_id_from_query),
    db: Client = Depends(get_db)
):
    """
    Get comprehensive productivity insights and recommendations
    
    - **user_id**: User identifier (required)
    
    Returns:
    - Overall productivity score breakdown
    - Recent productivity trends
    - Task completion velocity
    - Actionable insights and recommendations
    """
    try:
        service = AnalyticsService(db)
        insights = await service.get_productivity_insights(user_id)
        
        return success_response(insights)
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get productivity insights: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/productivity/score", response_model=UserProductivityScore)
async def get_productivity_score(
    user_id: str = Depends(get_user_id_from_query),
    db: Client = Depends(get_db)
):
    """
    Get user productivity score
    
    - **user_id**: User identifier (required)
    
    Returns detailed productivity scoring including:
    - Overall productivity score (0-100)
    - Individual component scores
    - Score trend analysis
    - Personalized recommendations
    """
    try:
        service = AnalyticsService(db)
        score = await service.calculate_productivity_score(user_id)
        
        return success_response(score)
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get productivity score: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/trends/productivity")
async def get_productivity_trends(
    user_id: str = Depends(get_user_id_from_query),
    start_date: date = Query(..., description="Start date for trend analysis"),
    end_date: date = Query(..., description="End date for trend analysis"),
    db: Client = Depends(get_db)
):
    """
    Get daily productivity trends over a date range
    
    - **user_id**: User identifier (required)
    - **start_date**: Start date for analysis (required)
    - **end_date**: End date for analysis (required)
    
    Returns daily metrics including:
    - Tasks completed per day
    - Tasks created per day
    - Goals created per day
    - Total active tasks at end of day
    """
    try:
        service = AnalyticsService(db)
        
        date_range = DateRange(start_date=start_date, end_date=end_date)
        trends = await service.get_productivity_trends(user_id, date_range)
        
        return success_response({
            "trends": trends,
            "start_date": start_date,
            "end_date": end_date,
            "total_days": len(trends)
        })
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get productivity trends: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analysis/timeframes")
async def get_timeframe_analysis(
    user_id: str = Depends(get_user_id_from_query),
    db: Client = Depends(get_db)
):
    """
    Get analysis by goal timeframes
    
    - **user_id**: User identifier (required)
    
    Returns goal and task statistics grouped by timeframe:
    - 1_week, 1_month, 3_months, 6_months, 1_year, ongoing
    """
    try:
        service = AnalyticsService(db)
        analysis = await service.get_timeframe_analysis(user_id)
        
        return success_response({
            "timeframe_analysis": analysis,
            "total_timeframes": len(analysis)
        })
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get timeframe analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analysis/categories")
async def get_category_analysis(
    user_id: str = Depends(get_user_id_from_query),
    db: Client = Depends(get_db)
):
    """
    Get analysis by goal categories
    
    - **user_id**: User identifier (required)
    
    Returns goal and task statistics grouped by category:
    - health, career, learning, personal, relationships, financial, creative, other
    """
    try:
        service = AnalyticsService(db)
        analysis = await service.get_category_analysis(user_id)
        
        return success_response({
            "category_analysis": analysis,
            "total_categories": len(analysis)
        })
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get category analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analysis/priorities")
async def get_priority_analysis(
    user_id: str = Depends(get_user_id_from_query),
    db: Client = Depends(get_db)
):
    """
    Get analysis by task priorities
    
    - **user_id**: User identifier (required)
    
    Returns task statistics grouped by priority:
    - low, medium, high, urgent
    - Includes completion rates and average completion times
    """
    try:
        service = AnalyticsService(db)
        analysis = await service.get_priority_analysis(user_id)
        
        return success_response({
            "priority_analysis": analysis,
            "total_priorities": len(analysis)
        })
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get priority analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analysis/overdue")
async def get_overdue_analysis(
    user_id: str = Depends(get_user_id_from_query),
    db: Client = Depends(get_db)
):
    """
    Get overdue tasks analysis
    
    - **user_id**: User identifier (required)
    
    Returns comprehensive overdue task breakdown:
    - Total overdue count
    - Distribution by quadrant and priority
    - Age-based groupings
    - Oldest overdue task details
    """
    try:
        service = AnalyticsService(db)
        analysis = await service.get_overdue_analysis(user_id)
        
        return success_response(analysis)
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get overdue analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/velocity/completion")
async def get_completion_velocity(
    user_id: str = Depends(get_user_id_from_query),
    period: str = Query("30_days", description="Analysis period (7_days, 30_days, 90_days)"),
    db: Client = Depends(get_db)
):
    """
    Get task completion velocity
    
    - **user_id**: User identifier (required)
    - **period**: Analysis period (default: 30_days)
    
    Returns completion velocity metrics:
    - Tasks completed in period
    - Goals completed in period
    - Average tasks per day
    - Velocity trend direction
    """
    try:
        service = AnalyticsService(db)
        velocity = await service.get_completion_velocity(user_id, period)
        
        return success_response(velocity)
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get completion velocity: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/staging/analytics")
async def get_staging_analytics(
    user_id: str = Depends(get_user_id_from_query),
    db: Client = Depends(get_db)
):
    """
    Get staging zone analytics
    
    - **user_id**: User identifier (required)
    
    Returns staging zone performance metrics:
    - Average time items spend in staging
    - Total items ever staged
    - Staging efficiency (% organized)
    - Current utilization
    """
    try:
        service = AnalyticsService(db)
        analytics = await service.get_staging_analytics(user_id)
        
        return success_response(analytics)
        
    except QuadrantPlannerException:
        raise
    except Exception as e:
        logger.error(f"Failed to get staging analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
