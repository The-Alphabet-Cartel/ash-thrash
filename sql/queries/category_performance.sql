-- sql/queries/category_performance.sql
-- Category Performance Database Operations for Ash-Thrash Testing Suite
-- Repository: https://github.com/The-Alphabet-Cartel/ash-thrash

-- =============================================================================
-- INSERT OPERATIONS
-- =============================================================================

-- Insert category performance record
-- name: insert_category_performance
INSERT INTO category_performance (
    test_run_id,
    category_name,
    category_type,
    priority_level,
    total_tests,
    passed_tests,
    failed_tests,
    pass_rate,
    target_pass_rate,
    goal_met,
    avg_confidence,
    min_confidence,
    max_confidence,
    confidence_std_dev,
    avg_response_time_ms,
    is_critical,
    allow_escalation
) VALUES (
    :test_run_id,
    :category_name,
    :category_type,
    :priority_level,
    :total_tests,
    :passed_tests,
    :failed_tests,
    :pass_rate,
    :target_pass_rate,
    :goal_met,
    :avg_confidence,
    :min_confidence,
    :max_confidence,
    :confidence_std_dev,
    :avg_response_time_ms,
    :is_critical,
    :allow_escalation
) RETURNING id, created_at;

-- Batch insert category performance records
-- name: batch_insert_category_performance
INSERT INTO category_performance (
    test_run_id, category_name, category_type, priority_level, 
    total_tests, passed_tests, failed_tests, pass_rate, 
    target_pass_rate, goal_met, avg_confidence, avg_response_time_ms,
    is_critical, allow_escalation
) 
SELECT * FROM unnest(
    :test_run_ids::uuid[],
    :category_names::text[],
    :category_types::text[],
    :priority_levels::text[],
    :total_tests::integer[],
    :passed_tests::integer[],
    :failed_tests::integer[],
    :pass_rates::decimal[],
    :target_pass_rates::decimal[],
    :goals_met::boolean[],
    :avg_confidences::decimal[],
    :avg_response_times::decimal[],
    :is_criticals::boolean[],
    :allow_escalations::boolean[]
) RETURNING id;

-- =============================================================================
-- SELECT OPERATIONS
-- =============================================================================

-- Get category performance by test run
-- name: get_category_performance_by_test_run
SELECT 
    cp.*,
    tr.test_type,
    tr.started_at as test_started_at,
    tr.environment
FROM category_performance cp
JOIN test_runs tr ON cp.test_run_id = tr.id
WHERE cp.test_run_id = :test_run_id
ORDER BY cp.category_name, cp.priority_level;

-- Get category performance by category name
-- name: get_category_performance_by_name
SELECT 
    cp.*,
    tr.test_type,
    tr.started_at as test_started_at,
    tr.environment,
    tr.overall_pass_rate as test_overall_pass_rate
FROM category_performance cp
JOIN test_runs tr ON cp.test_run_id = tr.id
WHERE cp.category_name = :category_name
  AND tr.test_status = 'completed'
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
  AND tr.started_at >= COALESCE(:start_date, tr.started_at)
  AND tr.started_at <= COALESCE(:end_date, tr.started_at)
ORDER BY tr.started_at DESC
LIMIT :limit OFFSET :offset;

-- Get latest category performance summary
-- name: get_latest_category_performance_summary
SELECT 
    cp.category_name,
    cp.category_type,
    cp.priority_level,
    cp.pass_rate,
    cp.target_pass_rate,
    cp.goal_met,
    cp.avg_confidence,
    cp.total_tests,
    cp.passed_tests,
    cp.failed_tests,
    cp.is_critical,
    tr.started_at as test_date,
    tr.test_type,
    tr.environment
FROM category_performance cp
JOIN test_runs tr ON cp.test_run_id = tr.id
WHERE tr.id = (
    SELECT id FROM test_runs 
    WHERE test_status = 'completed' 
    ORDER BY started_at DESC 
    LIMIT 1
)
ORDER BY 
    cp.is_critical DESC,
    cp.category_type,
    cp.priority_level,
    cp.category_name;

-- Get category performance trends
-- name: get_category_performance_trends
SELECT 
    cp.category_name,
    DATE_TRUNC(:period, tr.started_at) as period_start,
    COUNT(*) as test_count,
    AVG(cp.pass_rate) as avg_pass_rate,
    AVG(cp.target_pass_rate) as avg_target_pass_rate,
    COUNT(*) FILTER (WHERE cp.goal_met = TRUE) as goals_met,
    COUNT(*) FILTER (WHERE cp.goal_met = FALSE) as goals_missed,
    AVG(cp.avg_confidence) as avg_confidence,
    AVG(cp.avg_response_time_ms) as avg_response_time,
    MIN(cp.pass_rate) as min_pass_rate,
    MAX(cp.pass_rate) as max_pass_rate,
    STDDEV(cp.pass_rate) as pass_rate_std_dev
FROM category_performance cp
JOIN test_runs tr ON cp.test_run_id = tr.id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date
  AND (:category_name IS NULL OR cp.category_name = :category_name)
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY cp.category_name, DATE_TRUNC(:period, tr.started_at)
ORDER BY period_start DESC, cp.category_name;

-- Get critical category failures
-- name: get_critical_category_failures
SELECT 
    cp.category_name,
    cp.priority_level,
    cp.pass_rate,
    cp.target_pass_rate,
    cp.goal_met,
    cp.avg_confidence,
    tr.started_at as test_date,
    tr.test_type,
    tr.environment,
    tr.id as test_run_id,
    COUNT(tf.id) as failure_count
FROM category_performance cp
JOIN test_runs tr ON cp.test_run_id = tr.id
LEFT JOIN test_failures tf ON cp.id = tf.category_performance_id
WHERE cp.is_critical = TRUE
  AND (cp.goal_met = FALSE OR cp.pass_rate < :min_pass_rate)
  AND tr.test_status = 'completed'
  AND tr.started_at >= COALESCE(:start_date, tr.started_at)
  AND tr.started_at <= COALESCE(:end_date, tr.started_at)
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY cp.id, cp.category_name, cp.priority_level, cp.pass_rate, 
         cp.target_pass_rate, cp.goal_met, cp.avg_confidence,
         tr.started_at, tr.test_type, tr.environment, tr.id
ORDER BY tr.started_at DESC, cp.pass_rate ASC;

-- Get category performance comparison
-- name: get_category_performance_comparison
SELECT 
    cp.category_name,
    current_test.test_type as current_test_type,
    current_test.started_at as current_test_date,
    cp.pass_rate as current_pass_rate,
    cp.target_pass_rate,
    cp.goal_met as current_goal_met,
    previous_cp.pass_rate as previous_pass_rate,
    previous_cp.goal_met as previous_goal_met,
    previous_test.started_at as previous_test_date,
    (cp.pass_rate - previous_cp.pass_rate) as pass_rate_change,
    cp.avg_confidence as current_confidence,
    previous_cp.avg_confidence as previous_confidence,
    (cp.avg_confidence - previous_cp.avg_confidence) as confidence_change
FROM category_performance cp
JOIN test_runs current_test ON cp.test_run_id = current_test.id
LEFT JOIN LATERAL (
    SELECT cp2.*, tr2.started_at 
    FROM category_performance cp2
    JOIN test_runs tr2 ON cp2.test_run_id = tr2.id
    WHERE cp2.category_name = cp.category_name
      AND tr2.test_status = 'completed'
      AND tr2.started_at < current_test.started_at
      AND (:test_type IS NULL OR tr2.test_type = :test_type)
      AND (:environment IS NULL OR tr2.environment = :environment)
    ORDER BY tr2.started_at DESC
    LIMIT 1
) previous_cp ON true
LEFT JOIN test_runs previous_test ON previous_cp.test_run_id = previous_test.id
WHERE current_test.id = :test_run_id
ORDER BY cp.category_name;

-- Get underperforming categories
-- name: get_underperforming_categories
SELECT 
    cp.category_name,
    cp.category_type,
    cp.priority_level,
    COUNT(*) as test_count,
    AVG(cp.pass_rate) as avg_pass_rate,
    AVG(cp.target_pass_rate) as avg_target_pass_rate,
    COUNT(*) FILTER (WHERE cp.goal_met = FALSE) as goals_missed,
    AVG(cp.avg_confidence) as avg_confidence,
    MIN(cp.pass_rate) as worst_pass_rate,
    MAX(tr.started_at) as last_test_date
FROM category_performance cp
JOIN test_runs tr ON cp.test_run_id = tr.id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY cp.category_name, cp.category_type, cp.priority_level
HAVING AVG(cp.pass_rate) < :min_avg_pass_rate
   OR COUNT(*) FILTER (WHERE cp.goal_met = FALSE) > :max_goal_misses
ORDER BY avg_pass_rate ASC, goals_missed DESC;

-- =============================================================================
-- UPDATE OPERATIONS
-- =============================================================================

-- Update category performance metrics
-- name: update_category_performance
UPDATE category_performance 
SET 
    total_tests = :total_tests,
    passed_tests = :passed_tests,
    failed_tests = :failed_tests,
    pass_rate = :pass_rate,
    goal_met = :goal_met,
    avg_confidence = :avg_confidence,
    min_confidence = :min_confidence,
    max_confidence = :max_confidence,
    confidence_std_dev = :confidence_std_dev,
    avg_response_time_ms = :avg_response_time_ms
WHERE id = :category_performance_id;

-- =============================================================================
-- DELETE OPERATIONS
-- =============================================================================

-- Delete category performance by test run
-- name: delete_category_performance_by_test_run
DELETE FROM category_performance 
WHERE test_run_id = :test_run_id;

-- =============================================================================
-- ANALYSIS QUERIES
-- =============================================================================

-- Get category performance statistics
-- name: get_category_performance_statistics
SELECT 
    category_name,
    category_type,
    priority_level,
    COUNT(*) as total_tests_run,
    AVG(pass_rate) as avg_pass_rate,
    STDDEV(pass_rate) as pass_rate_std_dev,
    MIN(pass_rate) as min_pass_rate,
    MAX(pass_rate) as max_pass_rate,
    AVG(target_pass_rate) as avg_target_pass_rate,
    COUNT(*) FILTER (WHERE goal_met = TRUE) as goals_achieved,
    COUNT(*) FILTER (WHERE goal_met = FALSE) as goals_missed,
    ROUND((COUNT(*) FILTER (WHERE goal_met = TRUE)::decimal / COUNT(*)) * 100, 2) as goal_success_rate,
    AVG(avg_confidence) as avg_confidence_score,
    AVG(avg_response_time_ms) as avg_response_time
FROM category_performance cp
JOIN test_runs tr ON cp.test_run_id = tr.id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= COALESCE(:start_date, tr.started_at)
  AND tr.started_at <= COALESCE(:end_date, tr.started_at)
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY category_name, category_type, priority_level
ORDER BY avg_pass_rate DESC, goal_success_rate DESC;

-- Get category goal achievement summary
-- name: get_category_goal_achievement_summary
SELECT 
    cp.category_name,
    cp.is_critical,
    COUNT(*) as total_runs,
    COUNT(*) FILTER (WHERE cp.goal_met = TRUE) as goals_achieved,
    COUNT(*) FILTER (WHERE cp.goal_met = FALSE) as goals_missed,
    ROUND((COUNT(*) FILTER (WHERE cp.goal_met = TRUE)::decimal / COUNT(*)) * 100, 2) as achievement_rate,
    AVG(cp.pass_rate) as avg_pass_rate,
    AVG(cp.target_pass_rate) as avg_target_rate,
    AVG(cp.pass_rate - cp.target_pass_rate) as avg_rate_difference
FROM category_performance cp
JOIN test_runs tr ON cp.test_run_id = tr.id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY cp.category_name, cp.is_critical
ORDER BY cp.is_critical DESC, achievement_rate ASC;