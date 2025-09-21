"""
Analytics service layer - Business logic for analytics and insights
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from supabase import Client
from api.analytics.models import (
    AnalyticsDashboard, GoalProgressSummary, QuadrantDistribution, ProductivityTrend,
    TimeframeSummary, CategorySummary, PriorityAnalysis, OverdueAnalysis,
    CompletionVelocity, StagingZoneAnalytics, UserProductivityScore,
    AnalyticsFilters, DateRange, GoalProgressResponse, QuadrantAnalysisResponse,
    ProductivityInsightsResponse
)
# Database models import removed to avoid circular dependencies
from api.shared.exceptions import DatabaseError, ValidationError
from api.shared.validation import validate_user_id

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service class for analytics and insights business logic"""

    def __init__(self, db: Client):
        self.db = db

    async def get_dashboard(
        self,
        user_id: str,
        period: str = "30_days",
        date_range: Optional[DateRange] = None
    ) -> AnalyticsDashboard:
        """Get complete analytics dashboard"""
        try:
            validate_user_id(user_id)
            
            # Calculate date range if not provided
            if not date_range:
                end_date = date.today()
                if period == "7_days":
                    start_date = end_date - timedelta(days=7)
                elif period == "30_days":
                    start_date = end_date - timedelta(days=30)
                elif period == "90_days":
                    start_date = end_date - timedelta(days=90)
                elif period == "1_year":
                    start_date = end_date - timedelta(days=365)
                else:
                    start_date = end_date - timedelta(days=30)
                
                date_range = DateRange(start_date=start_date, end_date=end_date)

            # Get all analytics components
            goal_progress = await self.get_goal_progress(user_id, date_range)
            quadrant_dist = await self.get_quadrant_distribution(user_id)
            productivity_trends = await self.get_productivity_trends(user_id, date_range)
            timeframe_analysis = await self.get_timeframe_analysis(user_id)
            category_analysis = await self.get_category_analysis(user_id)
            priority_analysis = await self.get_priority_analysis(user_id)
            overdue_analysis = await self.get_overdue_analysis(user_id)
            completion_velocity = await self.get_completion_velocity(user_id, period)
            staging_analytics = await self.get_staging_analytics(user_id)
            productivity_score = await self.calculate_productivity_score(user_id)

            # Calculate summary metrics
            total_goals = len([g for g in goal_progress.goals if g.active_tasks > 0 or g.completed_tasks > 0])
            total_tasks = sum(g.total_tasks for g in goal_progress.goals)
            completed_tasks = sum(g.completed_tasks for g in goal_progress.goals)
            overdue_tasks = overdue_analysis.total_overdue

            dashboard = AnalyticsDashboard(
                period=period,
                generated_at=datetime.utcnow(),
                total_goals=total_goals,
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                overdue_tasks=overdue_tasks,
                goal_progress=goal_progress.goals,
                quadrant_distribution=quadrant_dist,
                productivity_trends=productivity_trends,
                timeframe_analysis=timeframe_analysis,
                category_analysis=category_analysis,
                priority_analysis=priority_analysis,
                overdue_analysis=overdue_analysis,
                completion_velocity=completion_velocity,
                staging_analytics=staging_analytics,
                productivity_score=productivity_score
            )

            logger.info(f"Generated analytics dashboard for user {user_id}")
            return dashboard

        except Exception as e:
            logger.error(f"Failed to generate analytics dashboard for user {user_id}: {e}")
            raise DatabaseError("Failed to generate analytics dashboard")

    async def get_goal_progress(
        self,
        user_id: str,
        date_range: Optional[DateRange] = None
    ) -> GoalProgressResponse:
        """Get goal progress analytics"""
        try:
            validate_user_id(user_id)

            # Query goal_stats view
            query = self.db.table("goal_stats").select("*").eq("user_id", user_id)
            
            if date_range and date_range.start_date:
                query = query.gte("goal_created_at", date_range.start_date.isoformat())
            if date_range and date_range.end_date:
                query = query.lte("goal_created_at", date_range.end_date.isoformat())

            result = query.execute()

            goals = []
            if result.data:
                for row in result.data:
                    goal = GoalProgressSummary(
                        goal_id=row["goal_id"],
                        goal_title=row["goal_title"],
                        category=row["category"],
                        timeframe=row["timeframe"],
                        color=row["color"],
                        total_tasks=row["total_tasks"] or 0,
                        completed_tasks=row["completed_tasks"] or 0,
                        active_tasks=row["active_tasks"] or 0,
                        completion_rate=row["completion_rate"] or 0.0,
                        average_task_age=row["average_task_age"] or 0.0,
                        last_activity_at=row["last_activity_at"],
                        goal_created_at=row["goal_created_at"]
                    )
                    goals.append(goal)

            total_goals = len(goals)
            avg_completion_rate = sum(g.completion_rate for g in goals) / total_goals if total_goals > 0 else 0.0

            return GoalProgressResponse(
                goals=goals,
                total_goals=total_goals,
                average_completion_rate=round(avg_completion_rate, 2)
            )

        except Exception as e:
            logger.error(f"Failed to get goal progress for user {user_id}: {e}")
            raise DatabaseError("Failed to retrieve goal progress analytics")

    async def get_quadrant_distribution(self, user_id: str) -> QuadrantDistribution:
        """Get task quadrant distribution"""
        try:
            validate_user_id(user_id)

            # Query quadrant_distribution view
            result = self.db.table("quadrant_distribution").select("*").eq("user_id", user_id).execute()

            if result.data:
                row = result.data[0]
                return QuadrantDistribution(
                    user_id=row["user_id"],
                    q1_count=row["q1_count"] or 0,
                    q2_count=row["q2_count"] or 0,
                    q3_count=row["q3_count"] or 0,
                    q4_count=row["q4_count"] or 0,
                    staging_count=row["staging_count"] or 0,
                    total_active_tasks=row["total_active_tasks"] or 0,
                    q1_percentage=row["q1_percentage"] or 0.0,
                    q2_percentage=row["q2_percentage"] or 0.0,
                    q3_percentage=row["q3_percentage"] or 0.0,
                    q4_percentage=row["q4_percentage"] or 0.0,
                    staging_percentage=row["staging_percentage"] or 0.0
                )
            else:
                # Return empty distribution if no data
                return QuadrantDistribution(
                    user_id=user_id,
                    q1_count=0, q2_count=0, q3_count=0, q4_count=0, staging_count=0,
                    total_active_tasks=0,
                    q1_percentage=0.0, q2_percentage=0.0, q3_percentage=0.0,
                    q4_percentage=0.0, staging_percentage=0.0
                )

        except Exception as e:
            logger.error(f"Failed to get quadrant distribution for user {user_id}: {e}")
            raise DatabaseError("Failed to retrieve quadrant distribution")

    async def get_productivity_trends(
        self,
        user_id: str,
        date_range: DateRange
    ) -> List[ProductivityTrend]:
        """Get daily productivity trends"""
        try:
            validate_user_id(user_id)

            # Query productivity_trends view
            query = self.db.table("productivity_trends").select("*").eq("user_id", user_id)
            
            if date_range.start_date:
                query = query.gte("trend_date", date_range.start_date.isoformat())
            if date_range.end_date:
                query = query.lte("trend_date", date_range.end_date.isoformat())

            query = query.order("trend_date", desc=False)
            result = query.execute()

            trends = []
            if result.data:
                for row in result.data:
                    trend = ProductivityTrend(
                        date=row["trend_date"],
                        tasks_completed=row["tasks_completed"] or 0,
                        tasks_created=row["tasks_created"] or 0,
                        goals_created=row["goals_created"] or 0,
                        total_active_tasks=row["total_active_tasks"] or 0
                    )
                    trends.append(trend)

            return trends

        except Exception as e:
            logger.error(f"Failed to get productivity trends for user {user_id}: {e}")
            raise DatabaseError("Failed to retrieve productivity trends")

    async def get_timeframe_analysis(self, user_id: str) -> List[TimeframeSummary]:
        """Get analysis by goal timeframe"""
        try:
            validate_user_id(user_id)

            # Query timeframe_analysis view
            result = self.db.table("timeframe_analysis").select("*").eq("user_id", user_id).execute()

            summaries = []
            if result.data:
                for row in result.data:
                    summary = TimeframeSummary(
                        timeframe=row["timeframe"],
                        total_goals=row["total_goals"] or 0,
                        active_goals=row["active_goals"] or 0,
                        completed_goals=row["completed_goals"] or 0,
                        total_tasks=row["total_tasks"] or 0,
                        completed_tasks=row["completed_tasks"] or 0,
                        average_completion_rate=row["average_completion_rate"] or 0.0
                    )
                    summaries.append(summary)

            return summaries

        except Exception as e:
            logger.error(f"Failed to get timeframe analysis for user {user_id}: {e}")
            raise DatabaseError("Failed to retrieve timeframe analysis")

    async def get_category_analysis(self, user_id: str) -> List[CategorySummary]:
        """Get analysis by goal category"""
        try:
            validate_user_id(user_id)

            # Query category_analysis view
            result = self.db.table("category_analysis").select("*").eq("user_id", user_id).execute()

            summaries = []
            if result.data:
                for row in result.data:
                    summary = CategorySummary(
                        category=row["category"],
                        total_goals=row["total_goals"] or 0,
                        active_goals=row["active_goals"] or 0,
                        completed_goals=row["completed_goals"] or 0,
                        total_tasks=row["total_tasks"] or 0,
                        completed_tasks=row["completed_tasks"] or 0,
                        average_completion_rate=row["average_completion_rate"] or 0.0
                    )
                    summaries.append(summary)

            return summaries

        except Exception as e:
            logger.error(f"Failed to get category analysis for user {user_id}: {e}")
            raise DatabaseError("Failed to retrieve category analysis")

    async def get_priority_analysis(self, user_id: str) -> List[PriorityAnalysis]:
        """Get analysis by task priority"""
        try:
            validate_user_id(user_id)

            # Query priority_analysis view
            result = self.db.table("priority_analysis").select("*").eq("user_id", user_id).execute()

            analyses = []
            if result.data:
                for row in result.data:
                    analysis = PriorityAnalysis(
                        priority=row["priority"],
                        total_tasks=row["total_tasks"] or 0,
                        completed_tasks=row["completed_tasks"] or 0,
                        overdue_tasks=row["overdue_tasks"] or 0,
                        completion_rate=row["completion_rate"] or 0.0,
                        average_completion_time=row["average_completion_time"]
                    )
                    analyses.append(analysis)

            return analyses

        except Exception as e:
            logger.error(f"Failed to get priority analysis for user {user_id}: {e}")
            raise DatabaseError("Failed to retrieve priority analysis")

    async def get_overdue_analysis(self, user_id: str) -> OverdueAnalysis:
        """Get overdue tasks analysis"""
        try:
            validate_user_id(user_id)

            # Get overdue tasks by calling the database function
            result = self.db.rpc("get_overdue_analysis", {"p_user_id": user_id}).execute()

            if result.data:
                data = result.data[0]
                return OverdueAnalysis(
                    total_overdue=data["total_overdue"] or 0,
                    overdue_by_quadrant=data["overdue_by_quadrant"] or {},
                    overdue_by_priority=data["overdue_by_priority"] or {},
                    overdue_by_days=data["overdue_by_days"] or {},
                    oldest_overdue_task=data["oldest_overdue_task"]
                )
            else:
                return OverdueAnalysis(
                    total_overdue=0,
                    overdue_by_quadrant={},
                    overdue_by_priority={},
                    overdue_by_days={},
                    oldest_overdue_task=None
                )

        except Exception as e:
            logger.error(f"Failed to get overdue analysis for user {user_id}: {e}")
            raise DatabaseError("Failed to retrieve overdue analysis")

    async def get_completion_velocity(self, user_id: str, period: str) -> CompletionVelocity:
        """Get task completion velocity"""
        try:
            validate_user_id(user_id)

            # Call database function to get completion velocity
            result = self.db.rpc("get_completion_velocity", {
                "p_user_id": user_id,
                "p_period": period
            }).execute()

            if result.data:
                data = result.data[0]
                return CompletionVelocity(
                    period=period,
                    tasks_completed=data["tasks_completed"] or 0,
                    goals_completed=data["goals_completed"] or 0,
                    average_tasks_per_day=data["average_tasks_per_day"] or 0.0,
                    velocity_trend=data["velocity_trend"] or "stable"
                )
            else:
                return CompletionVelocity(
                    period=period,
                    tasks_completed=0,
                    goals_completed=0,
                    average_tasks_per_day=0.0,
                    velocity_trend="stable"
                )

        except Exception as e:
            logger.error(f"Failed to get completion velocity for user {user_id}: {e}")
            raise DatabaseError("Failed to retrieve completion velocity")

    async def get_staging_analytics(self, user_id: str) -> StagingZoneAnalytics:
        """Get staging zone analytics"""
        try:
            validate_user_id(user_id)

            # Call database function to get staging analytics
            result = self.db.rpc("get_staging_analytics", {"p_user_id": user_id}).execute()

            if result.data:
                data = result.data[0]
                return StagingZoneAnalytics(
                    average_staging_time=data["average_staging_time"] or 0.0,
                    total_staged_items=data["total_staged_items"] or 0,
                    items_organized_from_staging=data["items_organized_from_staging"] or 0,
                    staging_efficiency=data["staging_efficiency"] or 0.0,
                    current_staging_utilization=data["current_staging_utilization"] or 0.0
                )
            else:
                return StagingZoneAnalytics(
                    average_staging_time=0.0,
                    total_staged_items=0,
                    items_organized_from_staging=0,
                    staging_efficiency=0.0,
                    current_staging_utilization=0.0
                )

        except Exception as e:
            logger.error(f"Failed to get staging analytics for user {user_id}: {e}")
            raise DatabaseError("Failed to retrieve staging analytics")

    async def calculate_productivity_score(self, user_id: str) -> UserProductivityScore:
        """Calculate user productivity score"""
        try:
            validate_user_id(user_id)

            # Call database function to calculate productivity score
            result = self.db.rpc("calculate_productivity_score", {"p_user_id": user_id}).execute()

            if result.data:
                data = result.data[0]
                return UserProductivityScore(
                    overall_score=data["overall_score"] or 0.0,
                    goal_completion_score=data["goal_completion_score"] or 0.0,
                    task_completion_score=data["task_completion_score"] or 0.0,
                    quadrant_balance_score=data["quadrant_balance_score"] or 0.0,
                    consistency_score=data["consistency_score"] or 0.0,
                    staging_efficiency_score=data["staging_efficiency_score"] or 0.0,
                    score_trend=data["score_trend"] or "stable",
                    recommendations=data["recommendations"] or []
                )
            else:
                return UserProductivityScore(
                    overall_score=0.0,
                    goal_completion_score=0.0,
                    task_completion_score=0.0,
                    quadrant_balance_score=0.0,
                    consistency_score=0.0,
                    staging_efficiency_score=0.0,
                    score_trend="stable",
                    recommendations=["Create your first goal to start tracking productivity"]
                )

        except Exception as e:
            logger.error(f"Failed to calculate productivity score for user {user_id}: {e}")
            raise DatabaseError("Failed to calculate productivity score")

    async def get_quadrant_analysis(self, user_id: str) -> QuadrantAnalysisResponse:
        """Get detailed quadrant analysis with recommendations"""
        try:
            validate_user_id(user_id)

            # Get current distribution
            distribution = await self.get_quadrant_distribution(user_id)

            # Generate recommendations based on distribution
            recommendations = []
            ideal_distribution = {
                "Q1": 20.0,  # Urgent + Important should be minimal
                "Q2": 60.0,  # Important but not urgent should be majority
                "Q3": 15.0,  # Urgent but not important should be limited
                "Q4": 5.0,   # Neither should be minimal
                "staging": 0.0  # Staging should be temporary
            }

            # Analyze current vs ideal distribution
            if distribution.q1_percentage > 30:
                recommendations.append("You have too many urgent+important tasks. Focus on prevention and planning.")
            
            if distribution.q2_percentage < 40:
                recommendations.append("Increase focus on important but not urgent tasks (Q2) for better long-term results.")
            
            if distribution.q3_percentage > 25:
                recommendations.append("Too many urgent but unimportant tasks. Consider delegation or elimination.")
            
            if distribution.q4_percentage > 10:
                recommendations.append("Reduce time-wasting activities in Q4. Focus energy elsewhere.")
            
            if distribution.staging_percentage > 20:
                recommendations.append("High staging utilization. Process staged items into appropriate quadrants.")

            if not recommendations:
                recommendations.append("Great quadrant balance! Maintain this distribution for optimal productivity.")

            return QuadrantAnalysisResponse(
                distribution=distribution,
                recommendations=recommendations,
                ideal_distribution=ideal_distribution
            )

        except Exception as e:
            logger.error(f"Failed to get quadrant analysis for user {user_id}: {e}")
            raise DatabaseError("Failed to retrieve quadrant analysis")

    async def get_productivity_insights(self, user_id: str) -> ProductivityInsightsResponse:
        """Get comprehensive productivity insights"""
        try:
            validate_user_id(user_id)

            # Get components
            productivity_score = await self.calculate_productivity_score(user_id)
            trends = await self.get_productivity_trends(
                user_id, 
                DateRange(start_date=date.today() - timedelta(days=30), end_date=date.today())
            )
            velocity = await self.get_completion_velocity(user_id, "30_days")

            # Generate insights
            insights = []
            action_items = []

            # Analyze productivity score
            if productivity_score.overall_score >= 80:
                insights.append("Excellent productivity! You're maintaining high performance.")
            elif productivity_score.overall_score >= 60:
                insights.append("Good productivity with room for improvement.")
            else:
                insights.append("Productivity below optimal. Focus on key improvement areas.")
                action_items.append("Review and optimize your goal-setting process")

            # Analyze trends
            if len(trends) >= 7:
                recent_avg = sum(t.tasks_completed for t in trends[-7:]) / 7
                earlier_avg = sum(t.tasks_completed for t in trends[:7]) / 7 if len(trends) >= 14 else recent_avg
                
                if recent_avg > earlier_avg * 1.1:
                    insights.append("Your task completion rate is trending upward!")
                elif recent_avg < earlier_avg * 0.9:
                    insights.append("Task completion has slowed recently. Consider reviewing priorities.")
                    action_items.append("Identify and address productivity bottlenecks")

            # Analyze velocity
            if velocity.average_tasks_per_day < 1:
                action_items.append("Increase daily task completion rate")
            elif velocity.average_tasks_per_day > 5:
                insights.append("High task completion rate - great momentum!")

            # Analyze specific scores
            if productivity_score.quadrant_balance_score < 50:
                action_items.append("Improve task organization across quadrants")
            
            if productivity_score.staging_efficiency_score < 60:
                action_items.append("Process staging zone items more efficiently")

            return ProductivityInsightsResponse(
                productivity_score=productivity_score,
                trends=trends,
                velocity=velocity,
                insights=insights,
                action_items=action_items
            )

        except Exception as e:
            logger.error(f"Failed to get productivity insights for user {user_id}: {e}")
            raise DatabaseError("Failed to retrieve productivity insights")
