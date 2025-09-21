"""
Pydantic models for Analytics API
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, validator


class DateRange(BaseModel):
    """Date range for analytics queries"""
    start_date: Optional[date] = Field(None, description="Start date for analysis")
    end_date: Optional[date] = Field(None, description="End date for analysis")

    @validator('end_date')
    def validate_date_range(cls, v: Optional[date], values: Dict[str, Any]) -> Optional[date]:
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError("End date must be after start date")
        return v


class GoalProgressSummary(BaseModel):
    """Goal progress summary model"""
    goal_id: str = Field(..., description="Goal unique identifier")
    goal_title: str = Field(..., description="Goal title")
    category: str = Field(..., description="Goal category")
    timeframe: str = Field(..., description="Goal timeframe")
    color: str = Field(..., description="Goal color")
    total_tasks: int = Field(default=0, ge=0, description="Total number of tasks")
    completed_tasks: int = Field(default=0, ge=0, description="Number of completed tasks")
    active_tasks: int = Field(default=0, ge=0, description="Number of active tasks")
    completion_rate: float = Field(default=0.0, ge=0, le=100, description="Completion percentage")
    average_task_age: float = Field(default=0.0, ge=0, description="Average age of active tasks in days")
    last_activity_at: Optional[datetime] = Field(None, description="Last activity timestamp")
    goal_created_at: datetime = Field(..., description="Goal creation timestamp")

    class Config:
        from_attributes = True


class QuadrantDistribution(BaseModel):
    """Quadrant distribution model"""
    user_id: str = Field(..., description="User identifier")
    q1_count: int = Field(default=0, ge=0, description="Q1 (Urgent + Important) task count")
    q2_count: int = Field(default=0, ge=0, description="Q2 (Important) task count")
    q3_count: int = Field(default=0, ge=0, description="Q3 (Urgent) task count")
    q4_count: int = Field(default=0, ge=0, description="Q4 (Neither) task count")
    staging_count: int = Field(default=0, ge=0, description="Staging zone task count")
    total_active_tasks: int = Field(default=0, ge=0, description="Total active tasks")
    q1_percentage: float = Field(default=0.0, ge=0, le=100, description="Q1 percentage")
    q2_percentage: float = Field(default=0.0, ge=0, le=100, description="Q2 percentage")
    q3_percentage: float = Field(default=0.0, ge=0, le=100, description="Q3 percentage")
    q4_percentage: float = Field(default=0.0, ge=0, le=100, description="Q4 percentage")
    staging_percentage: float = Field(default=0.0, ge=0, le=100, description="Staging percentage")

    class Config:
        from_attributes = True


class ProductivityTrend(BaseModel):
    """Productivity trend model"""
    date: date = Field(..., description="Date")
    tasks_completed: int = Field(default=0, ge=0, description="Tasks completed on this date")
    tasks_created: int = Field(default=0, ge=0, description="Tasks created on this date")
    goals_created: int = Field(default=0, ge=0, description="Goals created on this date")
    total_active_tasks: int = Field(default=0, ge=0, description="Total active tasks at end of day")


class TimeframeSummary(BaseModel):
    """Timeframe summary model"""
    timeframe: str = Field(..., description="Goal timeframe")
    total_goals: int = Field(default=0, ge=0, description="Total goals in timeframe")
    active_goals: int = Field(default=0, ge=0, description="Active goals in timeframe")
    completed_goals: int = Field(default=0, ge=0, description="Completed goals in timeframe")
    total_tasks: int = Field(default=0, ge=0, description="Total tasks in timeframe")
    completed_tasks: int = Field(default=0, ge=0, description="Completed tasks in timeframe")
    average_completion_rate: float = Field(default=0.0, ge=0, le=100, description="Average completion rate")


class CategorySummary(BaseModel):
    """Category summary model"""
    category: str = Field(..., description="Goal category")
    total_goals: int = Field(default=0, ge=0, description="Total goals in category")
    active_goals: int = Field(default=0, ge=0, description="Active goals in category")
    completed_goals: int = Field(default=0, ge=0, description="Completed goals in category")
    total_tasks: int = Field(default=0, ge=0, description="Total tasks in category")
    completed_tasks: int = Field(default=0, ge=0, description="Completed tasks in category")
    average_completion_rate: float = Field(default=0.0, ge=0, le=100, description="Average completion rate")


class PriorityAnalysis(BaseModel):
    """Priority analysis model"""
    priority: str = Field(..., description="Task priority")
    total_tasks: int = Field(default=0, ge=0, description="Total tasks with this priority")
    completed_tasks: int = Field(default=0, ge=0, description="Completed tasks with this priority")
    overdue_tasks: int = Field(default=0, ge=0, description="Overdue tasks with this priority")
    completion_rate: float = Field(default=0.0, ge=0, le=100, description="Completion rate for this priority")
    average_completion_time: Optional[float] = Field(None, ge=0, description="Average completion time in days")


class OverdueAnalysis(BaseModel):
    """Overdue tasks analysis model"""
    total_overdue: int = Field(default=0, ge=0, description="Total overdue tasks")
    overdue_by_quadrant: Dict[str, int] = Field(default_factory=dict, description="Overdue tasks by quadrant")
    overdue_by_priority: Dict[str, int] = Field(default_factory=dict, description="Overdue tasks by priority")
    overdue_by_days: Dict[str, int] = Field(default_factory=dict, description="Overdue tasks by age ranges")
    oldest_overdue_task: Optional[Dict[str, Any]] = Field(None, description="Information about oldest overdue task")


class CompletionVelocity(BaseModel):
    """Task completion velocity model"""
    period: str = Field(..., description="Period (week, month, quarter)")
    tasks_completed: int = Field(default=0, ge=0, description="Tasks completed in period")
    goals_completed: int = Field(default=0, ge=0, description="Goals completed in period")
    average_tasks_per_day: float = Field(default=0.0, ge=0, description="Average tasks completed per day")
    velocity_trend: str = Field(..., description="Velocity trend (increasing, stable, decreasing)")


class StagingZoneAnalytics(BaseModel):
    """Staging zone analytics model"""
    average_staging_time: float = Field(default=0.0, ge=0, description="Average time items spend in staging (days)")
    total_staged_items: int = Field(default=0, ge=0, description="Total items ever staged")
    items_organized_from_staging: int = Field(default=0, ge=0, description="Items successfully organized")
    staging_efficiency: float = Field(default=0.0, ge=0, le=100, description="Percentage of staged items organized")
    current_staging_utilization: float = Field(default=0.0, ge=0, le=100, description="Current staging zone usage")


class UserProductivityScore(BaseModel):
    """User productivity score model"""
    overall_score: float = Field(..., ge=0, le=100, description="Overall productivity score")
    goal_completion_score: float = Field(..., ge=0, le=100, description="Goal completion score")
    task_completion_score: float = Field(..., ge=0, le=100, description="Task completion score")
    quadrant_balance_score: float = Field(..., ge=0, le=100, description="Quadrant balance score")
    consistency_score: float = Field(..., ge=0, le=100, description="Activity consistency score")
    staging_efficiency_score: float = Field(..., ge=0, le=100, description="Staging efficiency score")
    score_trend: str = Field(..., description="Score trend (improving, stable, declining)")
    recommendations: List[str] = Field(default_factory=list, description="Productivity recommendations")


class AnalyticsDashboard(BaseModel):
    """Complete analytics dashboard model"""
    period: str = Field(..., description="Analytics period")
    generated_at: datetime = Field(..., description="Report generation timestamp")
    
    # Core metrics
    total_goals: int = Field(default=0, ge=0, description="Total active goals")
    total_tasks: int = Field(default=0, ge=0, description="Total active tasks")
    completed_tasks: int = Field(default=0, ge=0, description="Total completed tasks")
    overdue_tasks: int = Field(default=0, ge=0, description="Total overdue tasks")
    
    # Simplified analytics (using basic types to avoid circular dependencies)
    goal_progress: List[Dict[str, Any]] = Field(default_factory=list, description="Goal progress summaries")
    quadrant_distribution: Dict[str, Any] = Field(default_factory=dict, description="Task quadrant distribution")
    productivity_trends: List[Dict[str, Any]] = Field(default_factory=list, description="Daily productivity trends")
    timeframe_analysis: List[Dict[str, Any]] = Field(default_factory=list, description="Analysis by timeframe")
    category_analysis: List[Dict[str, Any]] = Field(default_factory=list, description="Analysis by category")
    priority_analysis: List[Dict[str, Any]] = Field(default_factory=list, description="Analysis by priority")
    overdue_analysis: Dict[str, Any] = Field(default_factory=dict, description="Overdue tasks analysis")
    completion_velocity: Dict[str, Any] = Field(default_factory=dict, description="Task completion velocity")
    staging_analytics: Dict[str, Any] = Field(default_factory=dict, description="Staging zone analytics")
    productivity_score: Dict[str, Any] = Field(default_factory=dict, description="User productivity score")


class AnalyticsFilters(BaseModel):
    """Analytics filtering parameters"""
    user_id: str = Field(..., min_length=1, max_length=255, description="User identifier")
    date_range: Optional[DateRange] = Field(None, description="Date range for analysis")
    goal_ids: Optional[List[str]] = Field(None, max_items=50, description="Specific goal IDs to analyze")
    categories: Optional[List[str]] = Field(None, description="Goal categories to include")
    timeframes: Optional[List[str]] = Field(None, description="Goal timeframes to include")
    include_completed: bool = Field(True, description="Include completed items in analysis")
    include_archived: bool = Field(False, description="Include archived goals in analysis")


# Response models for specific endpoints
class GoalProgressResponse(BaseModel):
    """Goal progress endpoint response"""
    goals: List[GoalProgressSummary] = Field(..., description="Goal progress summaries")
    total_goals: int = Field(..., ge=0, description="Total number of goals")
    average_completion_rate: float = Field(..., ge=0, le=100, description="Average completion rate across all goals")


class QuadrantAnalysisResponse(BaseModel):
    """Quadrant analysis endpoint response"""
    distribution: QuadrantDistribution = Field(..., description="Current quadrant distribution")
    recommendations: List[str] = Field(default_factory=list, description="Quadrant balance recommendations")
    ideal_distribution: Dict[str, float] = Field(default_factory=dict, description="Recommended quadrant percentages")


class ProductivityInsightsResponse(BaseModel):
    """Productivity insights endpoint response"""
    productivity_score: UserProductivityScore = Field(..., description="Overall productivity score")
    trends: List[ProductivityTrend] = Field(..., description="Recent productivity trends")
    velocity: CompletionVelocity = Field(..., description="Task completion velocity")
    insights: List[str] = Field(default_factory=list, description="Key productivity insights")
    action_items: List[str] = Field(default_factory=list, description="Recommended action items")
