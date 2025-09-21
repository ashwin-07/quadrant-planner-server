-- =====================================================
-- Analytics Views and Functions for Quadrant Planner
-- =====================================================

-- =====================================================
-- GOAL STATISTICS VIEW
-- =====================================================

CREATE OR REPLACE VIEW goal_stats AS
SELECT 
    g.id as goal_id,
    g.user_id,
    g.title as goal_title,
    g.category,
    g.timeframe,
    g.color,
    g.created_at as goal_created_at,
    COUNT(t.id) as total_tasks,
    COUNT(CASE WHEN t.completed = true THEN 1 END) as completed_tasks,
    COUNT(CASE WHEN t.completed = false THEN 1 END) as active_tasks,
    CASE 
        WHEN COUNT(t.id) > 0 THEN 
            ROUND((COUNT(CASE WHEN t.completed = true THEN 1 END) * 100.0 / COUNT(t.id)), 2)
        ELSE 0 
    END as completion_rate,
    CASE 
        WHEN COUNT(CASE WHEN t.completed = false THEN 1 END) > 0 THEN
            ROUND(AVG(CASE WHEN t.completed = false THEN EXTRACT(days FROM NOW() - t.created_at) END), 1)
        ELSE 0
    END as average_task_age,
    MAX(CASE WHEN t.completed = false THEN t.updated_at END) as last_activity_at
FROM goals g
LEFT JOIN tasks t ON g.id = t.goal_id
WHERE g.archived = false
GROUP BY g.id, g.user_id, g.title, g.category, g.timeframe, g.color, g.created_at;

-- =====================================================
-- QUADRANT DISTRIBUTION VIEW
-- =====================================================

CREATE OR REPLACE VIEW quadrant_distribution AS
SELECT 
    user_id,
    COUNT(CASE WHEN quadrant = 'Q1' AND completed = false THEN 1 END) as q1_count,
    COUNT(CASE WHEN quadrant = 'Q2' AND completed = false THEN 1 END) as q2_count,
    COUNT(CASE WHEN quadrant = 'Q3' AND completed = false THEN 1 END) as q3_count,
    COUNT(CASE WHEN quadrant = 'Q4' AND completed = false THEN 1 END) as q4_count,
    COUNT(CASE WHEN quadrant = 'staging' AND completed = false THEN 1 END) as staging_count,
    COUNT(CASE WHEN completed = false THEN 1 END) as total_active_tasks,
    CASE 
        WHEN COUNT(CASE WHEN completed = false THEN 1 END) > 0 THEN
            ROUND((COUNT(CASE WHEN quadrant = 'Q2' AND completed = false THEN 1 END) * 100.0 / 
                   COUNT(CASE WHEN completed = false THEN 1 END)), 2)
        ELSE 0
    END as q2_focus_percentage
FROM tasks
GROUP BY user_id;

-- =====================================================
-- STAGING EFFICIENCY VIEW
-- =====================================================

CREATE OR REPLACE VIEW staging_efficiency AS
SELECT 
    user_id,
    COUNT(CASE WHEN quadrant = 'staging' THEN 1 END) as items_staged,
    COUNT(CASE WHEN organized_at IS NOT NULL THEN 1 END) as items_processed,
    CASE 
        WHEN COUNT(CASE WHEN quadrant = 'staging' THEN 1 END) > 0 THEN
            ROUND((COUNT(CASE WHEN organized_at IS NOT NULL THEN 1 END) * 100.0 / 
                   COUNT(CASE WHEN quadrant = 'staging' THEN 1 END)), 2)
        ELSE 0
    END as processing_rate,
    CASE 
        WHEN COUNT(CASE WHEN organized_at IS NOT NULL THEN 1 END) > 0 THEN
            ROUND(AVG(CASE WHEN organized_at IS NOT NULL THEN 
                EXTRACT(hours FROM organized_at - staged_at) END), 1)
        ELSE 0
    END as average_staging_time_hours,
    (SELECT 
        CASE 
            WHEN COUNT(*) > 0 THEN 
                JSON_BUILD_OBJECT(
                    'taskId', (SELECT id FROM tasks WHERE user_id = t.user_id AND quadrant = 'staging' 
                              AND completed = false ORDER BY staged_at ASC LIMIT 1),
                    'daysSinceStaged', EXTRACT(days FROM NOW() - MIN(staged_at))
                )
            ELSE NULL 
        END
     FROM tasks 
     WHERE user_id = t.user_id AND quadrant = 'staging' AND completed = false
    ) as oldest_staged_item
FROM tasks t
GROUP BY user_id;

-- =====================================================
-- PRODUCTIVITY METRICS VIEW
-- =====================================================

CREATE OR REPLACE VIEW productivity_metrics AS
SELECT 
    user_id,
    -- Current week metrics
    COUNT(CASE WHEN created_at >= date_trunc('week', NOW()) THEN 1 END) as tasks_created_this_week,
    COUNT(CASE WHEN completed_at >= date_trunc('week', NOW()) THEN 1 END) as tasks_completed_this_week,
    -- Overall completion rate
    CASE 
        WHEN COUNT(*) > 0 THEN
            ROUND((COUNT(CASE WHEN completed = true THEN 1 END) * 100.0 / COUNT(*)), 2)
        ELSE 0
    END as overall_completion_rate,
    -- Q2 focus (important, not urgent)
    CASE 
        WHEN COUNT(CASE WHEN completed = false THEN 1 END) > 0 THEN
            ROUND((COUNT(CASE WHEN quadrant = 'Q2' AND completed = false THEN 1 END) * 100.0 / 
                   COUNT(CASE WHEN completed = false THEN 1 END)), 2)
        ELSE 0
    END as q2_focus,
    -- Goal balance (no single goal should dominate)
    CASE 
        WHEN COUNT(CASE WHEN goal_id IS NOT NULL THEN 1 END) > 0 THEN
            100.0 - (
                SELECT MAX(goal_task_count) * 100.0 / COUNT(CASE WHEN goal_id IS NOT NULL THEN 1 END)
                FROM (
                    SELECT COUNT(*) as goal_task_count
                    FROM tasks t2 
                    WHERE t2.user_id = t.user_id AND t2.goal_id IS NOT NULL AND t2.completed = false
                    GROUP BY t2.goal_id
                ) goal_counts
            )
        ELSE 100.0
    END as goal_balance,
    -- Streak calculation (consecutive days with completed tasks)
    (SELECT 
        COALESCE(
            (SELECT COUNT(*)
             FROM generate_series(
                 CURRENT_DATE - INTERVAL '30 days',
                 CURRENT_DATE,
                 INTERVAL '1 day'
             ) AS day_series(day)
             WHERE EXISTS (
                 SELECT 1 FROM tasks 
                 WHERE user_id = t.user_id 
                 AND DATE(completed_at) = day_series.day
             )
             AND day_series.day >= ALL (
                 SELECT COALESCE(MAX(DATE(completed_at)), CURRENT_DATE - INTERVAL '30 days')
                 FROM tasks 
                 WHERE user_id = t.user_id
             )
            ), 0
        )
    ) as streak_days
FROM tasks t
GROUP BY user_id;

-- =====================================================
-- TASK TRENDS FUNCTION
-- =====================================================

CREATE OR REPLACE FUNCTION get_task_trends(
    user_id_param TEXT,
    start_date_param DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    end_date_param DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    date DATE,
    created INTEGER,
    completed INTEGER,
    active INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        day_series::DATE as date,
        COALESCE(created_count, 0) as created,
        COALESCE(completed_count, 0) as completed,
        COALESCE(
            (SELECT COUNT(*)::INTEGER 
             FROM tasks 
             WHERE user_id = user_id_param 
             AND DATE(created_at) <= day_series::DATE 
             AND (completed_at IS NULL OR DATE(completed_at) > day_series::DATE)
            ), 0
        ) as active
    FROM generate_series(
        start_date_param::DATE,
        end_date_param::DATE,
        INTERVAL '1 day'
    ) AS day_series
    LEFT JOIN (
        SELECT 
            DATE(created_at) as created_date,
            COUNT(*)::INTEGER as created_count
        FROM tasks
        WHERE user_id = user_id_param
        AND created_at >= start_date_param
        AND created_at <= end_date_param + INTERVAL '1 day'
        GROUP BY DATE(created_at)
    ) created_tasks ON day_series::DATE = created_tasks.created_date
    LEFT JOIN (
        SELECT 
            DATE(completed_at) as completed_date,
            COUNT(*)::INTEGER as completed_count
        FROM tasks
        WHERE user_id = user_id_param
        AND completed_at >= start_date_param
        AND completed_at <= end_date_param + INTERVAL '1 day'
        GROUP BY DATE(completed_at)
    ) completed_tasks ON day_series::DATE = completed_tasks.completed_date
    ORDER BY day_series;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- INSIGHTS GENERATION FUNCTION
-- =====================================================

CREATE OR REPLACE FUNCTION generate_insights(user_id_param TEXT)
RETURNS JSON AS $$
DECLARE
    insights JSON := '[]'::JSON;
    q2_percentage NUMERIC;
    staging_count INTEGER;
    overdue_count INTEGER;
    longest_staged_days INTEGER;
BEGIN
    -- Get current metrics
    SELECT q2_focus_percentage INTO q2_percentage
    FROM quadrant_distribution 
    WHERE user_id = user_id_param;
    
    SELECT staging_count INTO staging_count
    FROM quadrant_distribution 
    WHERE user_id = user_id_param;
    
    SELECT COUNT(*) INTO overdue_count
    FROM tasks 
    WHERE user_id = user_id_param 
    AND due_date < NOW() 
    AND completed = false;
    
    SELECT COALESCE(MAX(EXTRACT(days FROM NOW() - staged_at)), 0) INTO longest_staged_days
    FROM tasks 
    WHERE user_id = user_id_param 
    AND quadrant = 'staging' 
    AND completed = false;
    
    -- Generate insights based on data
    
    -- Q2 Focus Insight
    IF q2_percentage IS NOT NULL THEN
        IF q2_percentage >= 30 THEN
            insights := insights || jsonb_build_object(
                'id', 'q2-focus-good',
                'type', 'q2_focus',
                'severity', 'success',
                'title', 'Great Q2 Focus!',
                'description', FORMAT('You''re spending %s%% of your time on important, non-urgent tasks. Keep it up!', q2_percentage),
                'actionable', false
            );
        ELSIF q2_percentage < 20 THEN
            insights := insights || jsonb_build_object(
                'id', 'q2-focus-low',
                'type', 'q2_focus',
                'severity', 'warning',
                'title', 'Focus on Important Tasks',
                'description', FORMAT('Only %s%% of your tasks are in Q2. Try to prioritize important, non-urgent activities.', q2_percentage),
                'actionable', true
            );
        END IF;
    END IF;
    
    -- Staging Zone Insight
    IF staging_count IS NOT NULL AND staging_count > 3 THEN
        insights := insights || jsonb_build_object(
            'id', 'staging-overflow',
            'type', 'staging_efficiency',
            'severity', 'info',
            'title', 'Staging Zone Needs Attention',
            'description', FORMAT('You have %s items in your staging zone. Consider organizing them into quadrants.', staging_count),
            'actionable', true
        );
    END IF;
    
    -- Overdue Tasks Insight
    IF overdue_count > 0 THEN
        insights := insights || jsonb_build_object(
            'id', 'overdue-tasks',
            'type', 'task_management',
            'severity', 'warning',
            'title', 'Overdue Tasks',
            'description', FORMAT('You have %s overdue task%s. Consider reviewing your priorities.', 
                                 overdue_count, 
                                 CASE WHEN overdue_count > 1 THEN 's' ELSE '' END),
            'actionable', true
        );
    END IF;
    
    -- Long Staged Items Insight
    IF longest_staged_days > 5 THEN
        insights := insights || jsonb_build_object(
            'id', 'long-staged',
            'type', 'staging_efficiency',
            'severity', 'info',
            'title', 'Old Staged Items',
            'description', FORMAT('You have items staged for %s days. Time to organize them!', longest_staged_days),
            'actionable', true
        );
    END IF;
    
    RETURN insights;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- GRANT PERMISSIONS ON VIEWS AND FUNCTIONS
-- =====================================================

GRANT SELECT ON goal_stats TO authenticated, service_role;
GRANT SELECT ON quadrant_distribution TO authenticated, service_role;
GRANT SELECT ON staging_efficiency TO authenticated, service_role;
GRANT SELECT ON productivity_metrics TO authenticated, service_role;

GRANT EXECUTE ON FUNCTION get_task_trends(TEXT, DATE, DATE) TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION generate_insights(TEXT) TO authenticated, service_role;
