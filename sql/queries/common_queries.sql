-- sql/queries/common_queries.sql
-- Common and Frequently Used Database Operations for Ash-Thrash Testing Suite
-- Repository: https://github.com/The-Alphabet-Cartel/ash-thrash

-- =============================================================================
-- DASHBOARD QUICK ACCESS QUERIES
-- =============================================================================

-- Get latest test status (most commonly requested)
-- name: get_latest_test_status
SELECT * FROM latest_test_summary LIMIT 1;

-- Get system health at a glance
-- name: get_system_health_snapshot
SELECT 
    (SELECT COUNT(*) FROM test_runs WHERE test_status = 'running') as active_tests,
    (SELECT AVG(overall_pass_rate) FROM test_runs WHERE started_at >= NOW() - INTERVAL '24 hours' AND test_status = 'completed') as pass_rate_24h,
    (SELECT COUNT(*) FROM test_failures WHERE created_at >= NOW() - INTERVAL '24 hours') as failures_24h,
    (SELECT COUNT(*) FROM test_failures WHERE is_critical = TRUE AND created_at >= NOW() - INTERVAL '24 hours') as critical_failures_24h,
    (SELECT server_status FROM system_performance ORDER BY recorded_at DESC LIMIT 1) as last_server_status,
    NOW() as checked_at;

-- Get recent test summary (last 7 days)
-- name: get_recent_test_summary
SELECT 
    test_type,
    environment,
    COUNT(*) as test_count,
    ROUND(AVG(overall_pass_rate), 2) as avg_pass_rate,
    ROUND(AVG(goal_achievement_rate), 2) as avg_goal_achievement,
    COUNT(*) FILTER (WHERE overall_pass_rate >= 85) as excellent_tests,
    COUNT(*) FILTER (WHERE overall_pass_rate < 70) as poor_tests,
    MAX(started_at) as last_test_date
FROM test_runs 
WHERE test_status = 'completed' 
  AND started_at >= NOW() - INTERVAL '7 days'
GROUP BY test_type, environment
ORDER BY last_test_date DESC;

-- =============================================================================
-- QUICK LOOKUP QUERIES
-- =============================================================================

-- Find test run by any identifier
-- name: find_test_run
SELECT 
    tr.*,
    COUNT(cp.id) as categories_tested,
    COUNT(tf.id) as total_failures,
    COUNT(tf.id) FILTER (WHERE tf.is_critical = TRUE) as critical_failures
FROM test_runs tr
LEFT JOIN category_performance cp ON tr.id = cp.test_run_id
LEFT JOIN test_failures tf ON tr.id = tf.test_run_id
WHERE tr.id = COALESCE(:test_run_id, tr.id)
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
  AND tr.started_at >= COALESCE(:start_date, tr.started_at)
  AND tr.started_at <= COALESCE(:end_date, tr.started_at)
GROUP BY tr.id
ORDER BY tr.started_at DESC
LIMIT COALESCE(:limit, 10);

-- Quick category lookup
-- name: quick_category_lookup
SELECT 
    cp.category_name,
    cp.category_type,
    cp.priority_level,
    cp.is_critical,
    COUNT(*) as test_count,
    AVG(cp.pass_rate) as avg_pass_rate,
    COUNT(*) FILTER (WHERE cp.goal_met = TRUE) as goals_achieved,
    MAX(tr.started_at) as last_tested
FROM category_performance cp
JOIN test_runs tr ON cp.test_run_id = tr.id
WHERE (:category_name IS NULL OR cp.category_name ILIKE '%' || :category_name || '%')
  AND tr.test_status = 'completed'
  AND tr.started_at >= COALESCE(:start_date, NOW() - INTERVAL '30 days')
GROUP BY cp.category_name, cp.category_type, cp.priority_level, cp.is_critical
ORDER BY last_tested DESC
LIMIT COALESCE(:limit, 20);

-- Quick phrase failure lookup
-- name: quick_phrase_lookup
SELECT 
    tf.test_phrase,
    tf.expected_priority,
    tf.failure_type,
    COUNT(*) as failure_count,
    COUNT(DISTINCT tf.test_run_id) as test_runs_affected,
    AVG(tf.confidence_score) as avg_confidence,
    MAX(tr.started_at) as last_failure
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
WHERE (:phrase_search IS NULL OR tf.test_phrase ILIKE '%' || :phrase_search || '%')
  AND tr.test_status = 'completed'
  AND tr.started_at >= COALESCE(:start_date, NOW() - INTERVAL '30 days')
GROUP BY tf.test_phrase, tf.expected_priority, tf.failure_type
ORDER BY failure_count DESC, last_failure DESC
LIMIT COALESCE(:limit, 20);

-- =============================================================================
-- COMMON AGGREGATIONS
-- =============================================================================

-- Get pass rate by category (frequently requested)
-- name: get_pass_rates_by_category
SELECT 
    cp.category_name,
    cp.category_type,
    cp.priority_level,
    COUNT(*) as test_count,
    ROUND(AVG(cp.pass_rate), 2) as avg_pass_rate,
    ROUND(MIN(cp.pass_rate), 2) as min_pass_rate,
    ROUND(MAX(cp.pass_rate), 2) as max_pass_rate,
    COUNT(*) FILTER (WHERE cp.goal_met = TRUE) as goals_achieved,
    ROUND((COUNT(*) FILTER (WHERE cp.goal_met = TRUE)::decimal / COUNT(*)) * 100, 2) as goal_success_rate
FROM category_performance cp
JOIN test_runs tr ON cp.test_run_id = tr.id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= COALESCE(:start_date, NOW() - INTERVAL '30 days')
  AND tr.started_at <= COALESCE(:end_date, NOW())
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY cp.category_name, cp.category_type, cp.priority_level
ORDER BY avg_pass_rate DESC;

-- Get failure statistics (commonly needed for alerts)
-- name: get_failure_statistics
SELECT 
    tf.failure_type,
    COUNT(*) as total_count,
    COUNT(*) FILTER (WHERE tf.is_critical = TRUE) as critical_count,
    COUNT(DISTINCT tf.test_phrase) as unique_phrases,
    COUNT(DISTINCT tf.test_run_id) as test_runs_affected,
    ROUND(AVG(tf.confidence_score), 3) as avg_confidence,
    MIN(tr.started_at) as first_occurrence,
    MAX(tr.started_at) as last_occurrence
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= COALESCE(:start_date, NOW() - INTERVAL '7 days')
  AND tr.started_at <= COALESCE(:end_date, NOW())
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY tf.failure_type
ORDER BY total_count DESC;

-- Get response time statistics
-- name: get_response_time_statistics
SELECT 
    'Overall' as metric_category,
    COUNT(*) as measurement_count,
    ROUND(AVG(tr.avg_response_time_ms), 2) as avg_response_time,
    ROUND(MIN(tr.avg_response_time_ms), 2) as min_response_time,
    ROUND(MAX(tr.avg_response_time_ms), 2) as max_response_time,
    ROUND(STDDEV(tr.avg_response_time_ms), 2) as std_dev_response_time
FROM test_runs tr
WHERE tr.test_status = 'completed'
  AND tr.started_at >= COALESCE(:start_date, NOW() - INTERVAL '7 days')
  AND tr.avg_response_time_ms IS NOT NULL

UNION ALL

SELECT 
    cp.category_name as metric_category,
    COUNT(*) as measurement_count,
    ROUND(AVG(cp.avg_response_time_ms), 2) as avg_response_time,
    ROUND(MIN(cp.avg_response_time_ms), 2) as min_response_time,
    ROUND(MAX(cp.avg_response_time_ms), 2) as max_response_time,
    ROUND(STDDEV(cp.avg_response_time_ms), 2) as std_dev_response_time
FROM category_performance cp
JOIN test_runs tr ON cp.test_run_id = tr.id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= COALESCE(:start_date, NOW() - INTERVAL '7 days')
  AND cp.avg_response_time_ms IS NOT NULL
GROUP BY cp.category_name
ORDER BY avg_response_time DESC
LIMIT 10;

-- =============================================================================
-- COMMON COMPARISONS
-- =============================================================================

-- Compare current vs previous performance
-- name: compare_current_vs_previous_performance
WITH current_period AS (
    SELECT 
        test_type,
        environment,
        COUNT(*) as test_count,
        AVG(overall_pass_rate) as avg_pass_rate,
        AVG(goal_achievement_rate) as avg_goal_achievement,
        AVG(avg_response_time_ms) as avg_response_time
    FROM test_runs
    WHERE test_status = 'completed'
      AND started_at >= :current_start_date
      AND started_at <= :current_end_date
    GROUP BY test_type, environment
),
previous_period AS (
    SELECT 
        test_type,
        environment,
        COUNT(*) as test_count,
        AVG(overall_pass_rate) as avg_pass_rate,
        AVG(goal_achievement_rate) as avg_goal_achievement,
        AVG(avg_response_time_ms) as avg_response_time
    FROM test_runs
    WHERE test_status = 'completed'
      AND started_at >= :previous_start_date
      AND started_at <= :previous_end_date
    GROUP BY test_type, environment
)
SELECT 
    COALESCE(c.test_type, p.test_type) as test_type,
    COALESCE(c.environment, p.environment) as environment,
    c.test_count as current_tests,
    p.test_count as previous_tests,
    ROUND(c.avg_pass_rate, 2) as current_pass_rate,
    ROUND(p.avg_pass_rate, 2) as previous_pass_rate,
    ROUND(c.avg_pass_rate - p.avg_pass_rate, 2) as pass_rate_change,
    ROUND(c.avg_goal_achievement, 2) as current_goal_achievement,
    ROUND(p.avg_goal_achievement, 2) as previous_goal_achievement,
    ROUND(c.avg_goal_achievement - p.avg_goal_achievement, 2) as goal_achievement_change,
    ROUND(c.avg_response_time, 2) as current_response_time,
    ROUND(p.avg_response_time, 2) as previous_response_time,
    ROUND(c.avg_response_time - p.avg_response_time, 2) as response_time_change
FROM current_period c
FULL OUTER JOIN previous_period p ON c.test_type = p.test_type AND c.environment = p.environment
ORDER BY test_type, environment;

-- =============================================================================
-- FREQUENTLY USED FILTERS AND SEARCHES
-- =============================================================================

-- Search across all test data
-- name: global_search
SELECT 
    'test_run' as result_type,
    tr.id::text as result_id,
    tr.test_type || ' - ' || tr.environment || ' (' || tr.started_at::date || ')' as result_title,
    'Pass Rate: ' || tr.overall_pass_rate || '%, Tests: ' || tr.total_tests as result_summary,
    tr.started_at as result_date
FROM test_runs tr
WHERE (:search_term IS NULL OR 
       tr.test_type ILIKE '%' || :search_term || '%' OR
       tr.environment ILIKE '%' || :search_term || '%' OR
       tr.metadata::text ILIKE '%' || :search_term || '%')
  AND tr.started_at >= COALESCE(:start_date, NOW() - INTERVAL '30 days')

UNION ALL

SELECT 
    'category' as result_type,
    cp.id::text as result_id,
    cp.category_name || ' (' || cp.category_type || ')' as result_title,
    'Pass Rate: ' || cp.pass_rate || '%, Goal Met: ' || cp.goal_met as result_summary,
    cp.created_at as result_date
FROM category_performance cp
JOIN test_runs tr ON cp.test_run_id = tr.id
WHERE (:search_term IS NULL OR 
       cp.category_name ILIKE '%' || :search_term || '%' OR
       cp.category_type ILIKE '%' || :search_term || '%')
  AND tr.started_at >= COALESCE(:start_date, NOW() - INTERVAL '30 days')

UNION ALL

SELECT 
    'failure' as result_type,
    tf.id::text as result_id,
    'Phrase: ' || LEFT(tf.test_phrase, 50) || '...' as result_title,
    tf.failure_type || ' - Expected: ' || tf.expected_priority || ', Got: ' || tf.detected_priority as result_summary,
    tf.created_at as result_date
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
WHERE (:search_term IS NULL OR 
       tf.test_phrase ILIKE '%' || :search_term || '%' OR
       tf.failure_type ILIKE '%' || :search_term || '%')
  AND tr.started_at >= COALESCE(:start_date, NOW() - INTERVAL '30 days')

ORDER BY result_date DESC
LIMIT COALESCE(:limit, 50);

-- =============================================================================
-- COMMON HEALTH CHECKS
-- =============================================================================

-- Quick health check (used by monitoring systems)
-- name: quick_health_check
SELECT 
    'database_connection' as check_name,
    'ok' as status,
    'Database connection successful' as message,
    NOW() as checked_at

UNION ALL

SELECT 
    'recent_test_activity' as check_name,
    CASE 
        WHEN EXISTS (SELECT 1 FROM test_runs WHERE started_at >= NOW() - INTERVAL '24 hours') 
        THEN 'ok' 
        ELSE 'warning' 
    END as status,
    CASE 
        WHEN EXISTS (SELECT 1 FROM test_runs WHERE started_at >= NOW() - INTERVAL '24 hours') 
        THEN 'Recent test activity detected' 
        ELSE 'No test activity in last 24 hours' 
    END as message,
    NOW() as checked_at

UNION ALL

SELECT 
    'critical_failures' as check_name,
    CASE 
        WHEN COUNT(*) = 0 THEN 'ok'
        WHEN COUNT(*) < 5 THEN 'warning'
        ELSE 'critical'
    END as status,
    COUNT(*)::text || ' critical failures in last 24 hours' as message,
    NOW() as checked_at
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
WHERE tf.is_critical = TRUE 
  AND tr.started_at >= NOW() - INTERVAL '24 hours'

UNION ALL

SELECT 
    'data_integrity' as check_name,
    CASE 
        WHEN COUNT(*) = 0 THEN 'ok'
        ELSE 'error'
    END as status,
    'Found ' || COUNT(*)::text || ' orphaned records' as message,
    NOW() as checked_at
FROM (
    SELECT id FROM category_performance cp 
    WHERE NOT EXISTS (SELECT 1 FROM test_runs tr WHERE tr.id = cp.test_run_id)
    UNION ALL
    SELECT id FROM test_failures tf 
    WHERE NOT EXISTS (SELECT 1 FROM test_runs tr WHERE tr.id = tf.test_run_id)
) orphaned;

-- =============================================================================
-- COMMON COUNTS AND METRICS
-- =============================================================================

-- Get record counts for all tables
-- name: get_record_counts
SELECT 
    'test_runs' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE started_at >= NOW() - INTERVAL '24 hours') as recent_24h,
    COUNT(*) FILTER (WHERE started_at >= NOW() - INTERVAL '7 days') as recent_7d,
    COUNT(*) FILTER (WHERE started_at >= NOW() - INTERVAL '30 days') as recent_30d
FROM test_runs

UNION ALL

SELECT 
    'category_performance' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '24 hours') as recent_24h,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as recent_7d,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as recent_30d
FROM category_performance

UNION ALL

SELECT 
    'test_failures' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '24 hours') as recent_24h,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as recent_7d,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as recent_30d
FROM test_failures

UNION ALL

SELECT 
    'system_performance' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE recorded_at >= NOW() - INTERVAL '24 hours') as recent_24h,
    COUNT(*) FILTER (WHERE recorded_at >= NOW() - INTERVAL '7 days') as recent_7d,
    COUNT(*) FILTER (WHERE recorded_at >= NOW() - INTERVAL '30 days') as recent_30d
FROM system_performance

ORDER BY table_name;

-- =============================================================================
-- COMMON VIEW ACCESSORS
-- =============================================================================

-- Access predefined views with common filters
-- name: get_testing_trends
SELECT * FROM testing_trends 
WHERE (:test_type IS NULL OR test_type = :test_type)
  AND test_date >= COALESCE(:start_date, NOW() - INTERVAL '30 days')
ORDER BY test_date DESC, test_type
LIMIT COALESCE(:limit, 30);

-- name: get_category_trends
SELECT * FROM category_trends 
WHERE (:category_name IS NULL OR category_name ILIKE '%' || :category_name || '%')
  AND week_start >= COALESCE(:start_date, NOW() - INTERVAL '90 days')
ORDER BY week_start DESC, category_name
LIMIT COALESCE(:limit, 50);

-- name: get_critical_failures_summary
SELECT * FROM critical_failures_summary
WHERE (:failure_type IS NULL OR failure_type = :failure_type)
  AND last_occurrence >= COALESCE(:start_date, NOW() - INTERVAL '30 days')
ORDER BY failure_count DESC, last_occurrence DESC
LIMIT COALESCE(:limit, 25);

-- name: get_system_health_summary
SELECT * FROM system_health_summary
WHERE hour_start >= COALESCE(:start_date, NOW() - INTERVAL '7 days')
ORDER BY hour_start DESC
LIMIT COALESCE(:limit, 168); -- Default to one week of hourly data