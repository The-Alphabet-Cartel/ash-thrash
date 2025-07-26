-- sql/queries/reporting.sql
-- Reporting and Analytics Database Operations for Ash-Thrash Testing Suite
-- Repository: https://github.com/The-Alphabet-Cartel/ash-thrash

-- =============================================================================
-- COMPREHENSIVE REPORTS
-- =============================================================================

-- Generate executive summary report
-- name: get_executive_summary_report
WITH recent_tests AS (
    SELECT * FROM test_runs 
    WHERE test_status = 'completed' 
      AND started_at >= :start_date 
      AND started_at <= :end_date
      AND (:environment IS NULL OR environment = :environment)
),
summary_stats AS (
    SELECT 
        COUNT(*) as total_tests,
        AVG(overall_pass_rate) as avg_pass_rate,
        AVG(goal_achievement_rate) as avg_goal_achievement,
        AVG(execution_time_seconds) as avg_execution_time,
        COUNT(*) FILTER (WHERE overall_pass_rate >= 85) as excellent_tests,
        COUNT(*) FILTER (WHERE overall_pass_rate < 70) as poor_tests
    FROM recent_tests
),
category_stats AS (
    SELECT 
        COUNT(DISTINCT cp.category_name) as categories_tested,
        COUNT(*) FILTER (WHERE cp.goal_met = TRUE) as goals_achieved,
        COUNT(*) FILTER (WHERE cp.goal_met = FALSE) as goals_missed,
        COUNT(*) FILTER (WHERE cp.is_critical = TRUE AND cp.goal_met = FALSE) as critical_failures
    FROM category_performance cp
    JOIN recent_tests rt ON cp.test_run_id = rt.id
),
failure_stats AS (
    SELECT 
        COUNT(*) as total_failures,
        COUNT(*) FILTER (WHERE tf.is_critical = TRUE) as critical_failures,
        COUNT(DISTINCT tf.test_phrase) as unique_failing_phrases
    FROM test_failures tf
    JOIN recent_tests rt ON tf.test_run_id = rt.id
)
SELECT 
    ss.total_tests,
    ROUND(ss.avg_pass_rate, 2) as avg_pass_rate,
    ROUND(ss.avg_goal_achievement, 2) as avg_goal_achievement,
    ROUND(ss.avg_execution_time, 2) as avg_execution_time_seconds,
    ss.excellent_tests,
    ss.poor_tests,
    cs.categories_tested,
    cs.goals_achieved,
    cs.goals_missed,
    cs.critical_failures as critical_category_failures,
    fs.total_failures,
    fs.critical_failures as critical_test_failures,
    fs.unique_failing_phrases,
    CASE 
        WHEN ss.avg_pass_rate >= 90 THEN 'Excellent'
        WHEN ss.avg_pass_rate >= 80 THEN 'Good'
        WHEN ss.avg_pass_rate >= 70 THEN 'Fair'
        ELSE 'Poor'
    END as overall_health_status
FROM summary_stats ss, category_stats cs, failure_stats fs;

-- Generate detailed test performance report
-- name: get_detailed_performance_report
SELECT 
    tr.id as test_run_id,
    tr.test_type,
    tr.environment,
    tr.started_at,
    tr.completed_at,
    EXTRACT(EPOCH FROM (tr.completed_at - tr.started_at)) as duration_seconds,
    tr.total_tests,
    tr.passed_tests,
    tr.failed_tests,
    tr.error_tests,
    tr.overall_pass_rate,
    tr.goal_achievement_rate,
    tr.avg_response_time_ms,
    tr.avg_processing_time_ms,
    COUNT(cp.id) as categories_tested,
    COUNT(cp.id) FILTER (WHERE cp.goal_met = TRUE) as goals_achieved,
    COUNT(cp.id) FILTER (WHERE cp.goal_met = FALSE) as goals_missed,
    COUNT(cp.id) FILTER (WHERE cp.is_critical = TRUE) as critical_categories,
    COUNT(tf.id) as total_failures,
    COUNT(tf.id) FILTER (WHERE tf.is_critical = TRUE) as critical_failures,
    COUNT(tf.id) FILTER (WHERE tf.failure_type = 'false_positive') as false_positives,
    COUNT(tf.id) FILTER (WHERE tf.failure_type = 'false_negative') as false_negatives,
    COUNT(tf.id) FILTER (WHERE tf.failure_type = 'wrong_priority') as wrong_priorities,
    CASE 
        WHEN tr.overall_pass_rate >= 90 THEN 'Excellent'
        WHEN tr.overall_pass_rate >= 80 THEN 'Good'
        WHEN tr.overall_pass_rate >= 70 THEN 'Fair'
        ELSE 'Poor'
    END as performance_grade
FROM test_runs tr
LEFT JOIN category_performance cp ON tr.id = cp.test_run_id
LEFT JOIN test_failures tf ON tr.id = tf.test_run_id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY tr.id, tr.test_type, tr.environment, tr.started_at, tr.completed_at,
         tr.total_tests, tr.passed_tests, tr.failed_tests, tr.error_tests,
         tr.overall_pass_rate, tr.goal_achievement_rate, tr.avg_response_time_ms, tr.avg_processing_time_ms
ORDER BY tr.started_at DESC;

-- Generate category performance analysis report
-- name: get_category_analysis_report
SELECT 
    cp.category_name,
    cp.category_type,
    cp.priority_level,
    cp.is_critical,
    COUNT(*) as test_runs,
    ROUND(AVG(cp.pass_rate), 2) as avg_pass_rate,
    ROUND(AVG(cp.target_pass_rate), 2) as avg_target_rate,
    COUNT(*) FILTER (WHERE cp.goal_met = TRUE) as goals_achieved,
    COUNT(*) FILTER (WHERE cp.goal_met = FALSE) as goals_missed,
    ROUND((COUNT(*) FILTER (WHERE cp.goal_met = TRUE)::decimal / COUNT(*)) * 100, 2) as goal_success_rate,
    ROUND(AVG(cp.avg_confidence), 3) as avg_confidence,
    ROUND(MIN(cp.pass_rate), 2) as worst_pass_rate,
    ROUND(MAX(cp.pass_rate), 2) as best_pass_rate,
    ROUND(STDDEV(cp.pass_rate), 2) as pass_rate_variability,
    COUNT(tf.id) as total_failures,
    COUNT(tf.id) FILTER (WHERE tf.is_critical = TRUE) as critical_failures,
    ROUND(AVG(cp.avg_response_time_ms), 2) as avg_response_time,
    MAX(tr.started_at) as last_tested,
    CASE 
        WHEN AVG(cp.pass_rate) >= 90 THEN 'Excellent'
        WHEN AVG(cp.pass_rate) >= 80 THEN 'Good'
        WHEN AVG(cp.pass_rate) >= 70 THEN 'Fair'
        ELSE 'Poor'
    END as performance_grade
FROM category_performance cp
JOIN test_runs tr ON cp.test_run_id = tr.id
LEFT JOIN test_failures tf ON cp.id = tf.category_performance_id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY cp.category_name, cp.category_type, cp.priority_level, cp.is_critical
ORDER BY avg_pass_rate ASC, critical_failures DESC, goal_success_rate ASC;

-- =============================================================================
-- TREND ANALYSIS REPORTS
-- =============================================================================

-- Generate weekly trend analysis
-- name: get_weekly_trend_analysis
SELECT 
    DATE_TRUNC('week', tr.started_at) as week_start,
    tr.test_type,
    tr.environment,
    COUNT(*) as test_count,
    ROUND(AVG(tr.overall_pass_rate), 2) as avg_pass_rate,
    ROUND(AVG(tr.goal_achievement_rate), 2) as avg_goal_achievement,
    ROUND(AVG(tr.avg_response_time_ms), 2) as avg_response_time,
    ROUND(AVG(tr.execution_time_seconds), 2) as avg_execution_time,
    COUNT(*) FILTER (WHERE tr.overall_pass_rate >= 85) as excellent_tests,
    COUNT(*) FILTER (WHERE tr.overall_pass_rate < 70) as poor_tests,
    COUNT(DISTINCT cp.category_name) as unique_categories_tested,
    COUNT(cp.id) FILTER (WHERE cp.goal_met = FALSE) as category_goal_failures,
    COUNT(tf.id) as total_failures,
    COUNT(tf.id) FILTER (WHERE tf.is_critical = TRUE) as critical_failures,
    -- Calculate week-over-week changes
    LAG(AVG(tr.overall_pass_rate)) OVER (PARTITION BY tr.test_type, tr.environment ORDER BY DATE_TRUNC('week', tr.started_at)) as prev_week_pass_rate,
    ROUND(AVG(tr.overall_pass_rate) - LAG(AVG(tr.overall_pass_rate)) OVER (PARTITION BY tr.test_type, tr.environment ORDER BY DATE_TRUNC('week', tr.started_at)), 2) as pass_rate_change
FROM test_runs tr
LEFT JOIN category_performance cp ON tr.id = cp.test_run_id
LEFT JOIN test_failures tf ON tr.id = tf.test_run_id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY DATE_TRUNC('week', tr.started_at), tr.test_type, tr.environment
ORDER BY week_start DESC, tr.test_type, tr.environment;

-- Generate failure trend analysis
-- name: get_failure_trend_analysis
SELECT 
    DATE_TRUNC(:period, tr.started_at) as period_start,
    tf.failure_type,
    COUNT(*) as failure_count,
    COUNT(*) FILTER (WHERE tf.is_critical = TRUE) as critical_failures,
    COUNT(DISTINCT tf.test_phrase) as unique_phrases_affected,
    COUNT(DISTINCT tr.id) as test_runs_affected,
    ROUND(AVG(tf.confidence_score), 3) as avg_confidence,
    ROUND(AVG(tf.response_time_ms), 2) as avg_response_time,
    -- Calculate period-over-period changes
    LAG(COUNT(*)) OVER (PARTITION BY tf.failure_type ORDER BY DATE_TRUNC(:period, tr.started_at)) as prev_period_count,
    COUNT(*) - LAG(COUNT(*)) OVER (PARTITION BY tf.failure_type ORDER BY DATE_TRUNC(:period, tr.started_at)) as failure_count_change
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY DATE_TRUNC(:period, tr.started_at), tf.failure_type
ORDER BY period_start DESC, failure_count DESC;

-- =============================================================================
-- QUALITY ASSURANCE REPORTS
-- =============================================================================

-- Generate quality metrics dashboard
-- name: get_quality_metrics_dashboard
WITH quality_metrics AS (
    SELECT 
        tr.test_type,
        tr.environment,
        COUNT(*) as total_test_runs,
        ROUND(AVG(tr.overall_pass_rate), 2) as avg_pass_rate,
        ROUND(STDDEV(tr.overall_pass_rate), 2) as pass_rate_consistency,
        COUNT(*) FILTER (WHERE tr.overall_pass_rate >= 90) as excellent_runs,
        COUNT(*) FILTER (WHERE tr.overall_pass_rate >= 80 AND tr.overall_pass_rate < 90) as good_runs,
        COUNT(*) FILTER (WHERE tr.overall_pass_rate >= 70 AND tr.overall_pass_rate < 80) as fair_runs,
        COUNT(*) FILTER (WHERE tr.overall_pass_rate < 70) as poor_runs,
        ROUND(AVG(tr.goal_achievement_rate), 2) as avg_goal_achievement,
        ROUND(AVG(tr.avg_response_time_ms), 2) as avg_response_time,
        ROUND(AVG(tr.execution_time_seconds), 2) as avg_execution_time
    FROM test_runs tr
    WHERE tr.test_status = 'completed'
      AND tr.started_at >= :start_date
      AND tr.started_at <= :end_date
    GROUP BY tr.test_type, tr.environment
),
failure_metrics AS (
    SELECT 
        tr.test_type,
        tr.environment,
        COUNT(tf.id) as total_failures,
        COUNT(tf.id) FILTER (WHERE tf.is_critical = TRUE) as critical_failures,
        COUNT(tf.id) FILTER (WHERE tf.failure_type = 'false_positive') as false_positives,
        COUNT(tf.id) FILTER (WHERE tf.failure_type = 'false_negative') as false_negatives,
        COUNT(tf.id) FILTER (WHERE tf.failure_type = 'wrong_priority') as wrong_priorities,
        COUNT(DISTINCT tf.test_phrase) as unique_failing_phrases
    FROM test_failures tf
    JOIN test_runs tr ON tf.test_run_id = tr.id
    WHERE tr.test_status = 'completed'
      AND tr.started_at >= :start_date
      AND tr.started_at <= :end_date
    GROUP BY tr.test_type, tr.environment
)
SELECT 
    qm.*,
    COALESCE(fm.total_failures, 0) as total_failures,
    COALESCE(fm.critical_failures, 0) as critical_failures,
    COALESCE(fm.false_positives, 0) as false_positives,
    COALESCE(fm.false_negatives, 0) as false_negatives,
    COALESCE(fm.wrong_priorities, 0) as wrong_priorities,
    COALESCE(fm.unique_failing_phrases, 0) as unique_failing_phrases,
    CASE 
        WHEN qm.avg_pass_rate >= 90 AND qm.pass_rate_consistency <= 5 THEN 'Excellent'
        WHEN qm.avg_pass_rate >= 80 AND qm.pass_rate_consistency <= 10 THEN 'Good'
        WHEN qm.avg_pass_rate >= 70 AND qm.pass_rate_consistency <= 15 THEN 'Fair'
        ELSE 'Poor'
    END as quality_grade
FROM quality_metrics qm
LEFT JOIN failure_metrics fm ON qm.test_type = fm.test_type AND qm.environment = fm.environment
ORDER BY qm.avg_pass_rate DESC, qm.pass_rate_consistency ASC;

-- Generate regression analysis report
-- name: get_regression_analysis_report
WITH current_period AS (
    SELECT 
        cp.category_name,
        AVG(cp.pass_rate) as current_pass_rate,
        COUNT(*) FILTER (WHERE cp.goal_met = TRUE) as current_goals_met,
        COUNT(*) as current_test_count
    FROM category_performance cp
    JOIN test_runs tr ON cp.test_run_id = tr.id
    WHERE tr.test_status = 'completed'
      AND tr.started_at >= :current_start_date
      AND tr.started_at <= :current_end_date
      AND (:test_type IS NULL OR tr.test_type = :test_type)
      AND (:environment IS NULL OR tr.environment = :environment)
    GROUP BY cp.category_name
),
previous_period AS (
    SELECT 
        cp.category_name,
        AVG(cp.pass_rate) as previous_pass_rate,
        COUNT(*) FILTER (WHERE cp.goal_met = TRUE) as previous_goals_met,
        COUNT(*) as previous_test_count
    FROM category_performance cp
    JOIN test_runs tr ON cp.test_run_id = tr.id
    WHERE tr.test_status = 'completed'
      AND tr.started_at >= :previous_start_date
      AND tr.started_at <= :previous_end_date
      AND (:test_type IS NULL OR tr.test_type = :test_type)
      AND (:environment IS NULL OR tr.environment = :environment)
    GROUP BY cp.category_name
)
SELECT 
    COALESCE(cp.category_name, pp.category_name) as category_name,
    ROUND(cp.current_pass_rate, 2) as current_pass_rate,
    ROUND(pp.previous_pass_rate, 2) as previous_pass_rate,
    ROUND(cp.current_pass_rate - pp.previous_pass_rate, 2) as pass_rate_change,
    cp.current_goals_met,
    cp.current_test_count,
    pp.previous_goals_met,
    pp.previous_test_count,
    CASE 
        WHEN cp.current_pass_rate IS NULL THEN 'New Category'
        WHEN pp.previous_pass_rate IS NULL THEN 'Missing Previous Data'
        WHEN cp.current_pass_rate - pp.previous_pass_rate > 5 THEN 'Improved'
        WHEN cp.current_pass_rate - pp.previous_pass_rate < -5 THEN 'Regressed'
        ELSE 'Stable'
    END as trend_status,
    CASE 
        WHEN cp.current_pass_rate - pp.previous_pass_rate < -10 THEN 'Critical Regression'
        WHEN cp.current_pass_rate - pp.previous_pass_rate < -5 THEN 'Moderate Regression'
        WHEN cp.current_pass_rate - pp.previous_pass_rate < -2 THEN 'Minor Regression'
        WHEN cp.current_pass_rate - pp.previous_pass_rate <= 2 THEN 'Stable'
        WHEN cp.current_pass_rate - pp.previous_pass_rate <= 5 THEN 'Minor Improvement'
        WHEN cp.current_pass_rate - pp.previous_pass_rate <= 10 THEN 'Moderate Improvement'
        ELSE 'Significant Improvement'
    END as regression_severity
FROM current_period cp
FULL OUTER JOIN previous_period pp ON cp.category_name = pp.category_name
ORDER BY 
    CASE 
        WHEN cp.current_pass_rate - pp.previous_pass_rate < -10 THEN 1
        WHEN cp.current_pass_rate - pp.previous_pass_rate < -5 THEN 2
        WHEN cp.current_pass_rate - pp.previous_pass_rate < -2 THEN 3
        ELSE 4
    END,
    ABS(COALESCE(cp.current_pass_rate - pp.previous_pass_rate, 0)) DESC;

-- =============================================================================
-- PERFORMANCE OPTIMIZATION REPORTS
-- =============================================================================

-- Generate optimization recommendations report
-- name: get_optimization_recommendations_report
WITH slow_categories AS (
    SELECT 
        cp.category_name,
        AVG(cp.avg_response_time_ms) as avg_response_time,
        COUNT(*) as test_count
    FROM category_performance cp
    JOIN test_runs tr ON cp.test_run_id = tr.id
    WHERE tr.test_status = 'completed'
      AND tr.started_at >= :start_date
      AND tr.started_at <= :end_date
    GROUP BY cp.category_name
    HAVING AVG(cp.avg_response_time_ms) > :response_time_threshold
),
underperforming_categories AS (
    SELECT 
        cp.category_name,
        AVG(cp.pass_rate) as avg_pass_rate,
        COUNT(*) FILTER (WHERE cp.goal_met = FALSE) as goal_failures
    FROM category_performance cp
    JOIN test_runs tr ON cp.test_run_id = tr.id
    WHERE tr.test_status = 'completed'
      AND tr.started_at >= :start_date
      AND tr.started_at <= :end_date
    GROUP BY cp.category_name
    HAVING AVG(cp.pass_rate) < :pass_rate_threshold
),
frequent_failures AS (
    SELECT 
        tf.test_phrase,
        tf.expected_priority,
        tf.failure_type,
        COUNT(*) as failure_count
    FROM test_failures tf
    JOIN test_runs tr ON tf.test_run_id = tr.id
    WHERE tr.test_status = 'completed'
      AND tr.started_at >= :start_date
      AND tr.started_at <= :end_date
    GROUP BY tf.test_phrase, tf.expected_priority, tf.failure_type
    HAVING COUNT(*) >= :failure_threshold
)
SELECT 
    'Performance' as recommendation_type,
    'Optimize slow categories' as recommendation,
    sc.category_name as affected_item,
    ROUND(sc.avg_response_time, 2)::text || 'ms average response time' as details,
    'High' as priority
FROM slow_categories sc

UNION ALL

SELECT 
    'Accuracy' as recommendation_type,
    'Improve underperforming categories' as recommendation,
    uc.category_name as affected_item,
    ROUND(uc.avg_pass_rate, 2)::text || '% pass rate, ' || uc.goal_failures::text || ' goal failures' as details,
    CASE 
        WHEN uc.avg_pass_rate < 60 THEN 'Critical'
        WHEN uc.avg_pass_rate < 70 THEN 'High'
        ELSE 'Medium'
    END as priority
FROM underperforming_categories uc

UNION ALL

SELECT 
    'Reliability' as recommendation_type,
    'Review frequently failing phrases' as recommendation,
    ff.test_phrase as affected_item,
    ff.expected_priority || ' priority, ' || ff.failure_type || ' (' || ff.failure_count::text || ' failures)' as details,
    CASE 
        WHEN ff.failure_count >= 10 THEN 'Critical'
        WHEN ff.failure_count >= 5 THEN 'High'
        ELSE 'Medium'
    END as priority
FROM frequent_failures ff

ORDER BY 
    CASE priority
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        ELSE 4
    END,
    recommendation_type,
    affected_item;

-- =============================================================================
-- EXPORT QUERIES FOR EXTERNAL REPORTING
-- =============================================================================

-- Generate CSV export data for test results
-- name: get_csv_export_test_results
SELECT 
    tr.id as test_run_id,
    tr.test_type,
    tr.environment,
    tr.started_at::date as test_date,
    tr.started_at::time as test_time,
    EXTRACT(EPOCH FROM (tr.completed_at - tr.started_at)) as duration_seconds,
    tr.total_tests,
    tr.passed_tests,
    tr.failed_tests,
    tr.error_tests,
    tr.overall_pass_rate,
    tr.goal_achievement_rate,
    tr.avg_response_time_ms,
    tr.avg_processing_time_ms,
    tr.test_trigger,
    tr.git_commit_hash
FROM test_runs tr
WHERE tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
ORDER BY tr.started_at DESC;

-- Generate CSV export data for category performance
-- name: get_csv_export_category_performance
SELECT 
    tr.started_at::date as test_date,
    tr.test_type,
    tr.environment,
    cp.category_name,
    cp.category_type,
    cp.priority_level,
    cp.total_tests,
    cp.passed_tests,
    cp.failed_tests,
    cp.pass_rate,
    cp.target_pass_rate,
    cp.goal_met,
    cp.avg_confidence,
    cp.avg_response_time_ms,
    cp.is_critical,
    cp.allow_escalation
FROM category_performance cp
JOIN test_runs tr ON cp.test_run_id = tr.id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
ORDER BY tr.started_at DESC, cp.category_name;