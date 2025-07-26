-- sql/queries/test_runs.sql
-- Test Runs Database Operations for Ash-Thrash Testing Suite
-- Repository: https://github.com/The-Alphabet-Cartel/ash-thrash

-- =============================================================================
-- INSERT OPERATIONS
-- =============================================================================

-- Insert new test run
-- name: insert_test_run
INSERT INTO test_runs (
    test_type, 
    total_tests, 
    nlp_server_url, 
    environment, 
    git_commit_hash, 
    test_trigger,
    metadata
) VALUES (
    :test_type, 
    :total_tests, 
    :nlp_server_url, 
    :environment, 
    :git_commit_hash, 
    :test_trigger,
    :metadata
) RETURNING id, started_at;

-- =============================================================================
-- UPDATE OPERATIONS
-- =============================================================================

-- Update test run completion
-- name: complete_test_run
UPDATE test_runs 
SET 
    completed_at = NOW(),
    passed_tests = :passed_tests,
    failed_tests = :failed_tests,
    error_tests = :error_tests,
    overall_pass_rate = :overall_pass_rate,
    goal_achievement_rate = :goal_achievement_rate,
    avg_response_time_ms = :avg_response_time_ms,
    avg_processing_time_ms = :avg_processing_time_ms,
    execution_time_seconds = :execution_time_seconds,
    results_file_path = :results_file_path,
    test_status = 'completed',
    memory_usage_mb = :memory_usage_mb,
    cpu_usage_percent = :cpu_usage_percent,
    updated_at = NOW()
WHERE id = :test_run_id;

-- Update test run status
-- name: update_test_run_status
UPDATE test_runs 
SET 
    test_status = :status,
    error_message = :error_message,
    updated_at = NOW()
WHERE id = :test_run_id;

-- Update test run with progress
-- name: update_test_run_progress
UPDATE test_runs 
SET 
    passed_tests = :passed_tests,
    failed_tests = :failed_tests,
    error_tests = :error_tests,
    overall_pass_rate = :overall_pass_rate,
    avg_response_time_ms = :avg_response_time_ms,
    updated_at = NOW()
WHERE id = :test_run_id;

-- =============================================================================
-- SELECT OPERATIONS
-- =============================================================================

-- Get test run by ID
-- name: get_test_run_by_id
SELECT 
    tr.*,
    (tr.completed_at - tr.started_at) as duration,
    CASE 
        WHEN tr.test_status = 'completed' THEN 
            EXTRACT(EPOCH FROM (tr.completed_at - tr.started_at))
        ELSE 
            EXTRACT(EPOCH FROM (NOW() - tr.started_at))
    END as duration_seconds
FROM test_runs tr
WHERE tr.id = :test_run_id;

-- Get latest test run
-- name: get_latest_test_run
SELECT 
    tr.*,
    (tr.completed_at - tr.started_at) as duration,
    COUNT(cp.id) as categories_tested,
    COUNT(tf.id) as total_failures
FROM test_runs tr
LEFT JOIN category_performance cp ON tr.id = cp.test_run_id
LEFT JOIN test_failures tf ON tr.id = tf.test_run_id
WHERE tr.test_status = 'completed'
GROUP BY tr.id
ORDER BY tr.started_at DESC
LIMIT 1;

-- Get latest test run by type
-- name: get_latest_test_run_by_type
SELECT 
    tr.*,
    (tr.completed_at - tr.started_at) as duration,
    COUNT(cp.id) as categories_tested,
    COUNT(tf.id) as total_failures
FROM test_runs tr
LEFT JOIN category_performance cp ON tr.id = cp.test_run_id
LEFT JOIN test_failures tf ON tr.id = tf.test_run_id
WHERE tr.test_type = :test_type 
  AND tr.test_status = 'completed'
GROUP BY tr.id
ORDER BY tr.started_at DESC
LIMIT 1;

-- Get test runs history with pagination
-- name: get_test_runs_history
SELECT 
    tr.id,
    tr.test_type,
    tr.started_at,
    tr.completed_at,
    tr.overall_pass_rate,
    tr.goal_achievement_rate,
    tr.total_tests,
    tr.passed_tests,
    tr.failed_tests,
    tr.test_status,
    tr.environment,
    tr.test_trigger,
    COUNT(cp.id) as categories_tested,
    COUNT(tf.id) as total_failures,
    COUNT(tf.id) FILTER (WHERE tf.is_critical = TRUE) as critical_failures
FROM test_runs tr
LEFT JOIN category_performance cp ON tr.id = cp.test_run_id
LEFT JOIN test_failures tf ON tr.id = tf.test_run_id
WHERE (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
  AND (:status IS NULL OR tr.test_status = :status)
  AND tr.started_at >= COALESCE(:start_date, tr.started_at)
  AND tr.started_at <= COALESCE(:end_date, tr.started_at)
GROUP BY tr.id
ORDER BY tr.started_at DESC
LIMIT :limit OFFSET :offset;

-- Get running test runs
-- name: get_running_test_runs
SELECT 
    tr.*,
    EXTRACT(EPOCH FROM (NOW() - tr.started_at)) as running_duration_seconds
FROM test_runs tr
WHERE tr.test_status = 'running'
ORDER BY tr.started_at ASC;

-- Get test run summary statistics
-- name: get_test_run_statistics
SELECT 
    COUNT(*) as total_runs,
    COUNT(*) FILTER (WHERE test_status = 'completed') as completed_runs,
    COUNT(*) FILTER (WHERE test_status = 'failed') as failed_runs,
    COUNT(*) FILTER (WHERE test_status = 'running') as running_runs,
    AVG(overall_pass_rate) FILTER (WHERE test_status = 'completed') as avg_pass_rate,
    AVG(goal_achievement_rate) FILTER (WHERE test_status = 'completed') as avg_goal_achievement,
    AVG(execution_time_seconds) FILTER (WHERE test_status = 'completed') as avg_execution_time,
    MIN(started_at) as first_test_date,
    MAX(started_at) as last_test_date
FROM test_runs
WHERE started_at >= COALESCE(:start_date, started_at)
  AND started_at <= COALESCE(:end_date, started_at)
  AND (:test_type IS NULL OR test_type = :test_type)
  AND (:environment IS NULL OR environment = :environment);

-- Get test performance trends
-- name: get_test_performance_trends
SELECT 
    DATE_TRUNC(:period, started_at) as period_start,
    test_type,
    environment,
    COUNT(*) as test_count,
    AVG(overall_pass_rate) as avg_pass_rate,
    AVG(goal_achievement_rate) as avg_goal_achievement,
    AVG(avg_response_time_ms) as avg_response_time,
    AVG(execution_time_seconds) as avg_execution_time,
    COUNT(*) FILTER (WHERE overall_pass_rate >= 85) as good_tests,
    COUNT(*) FILTER (WHERE overall_pass_rate < 70) as poor_tests
FROM test_runs
WHERE test_status = 'completed'
  AND started_at >= :start_date
  AND started_at <= :end_date
  AND (:test_type IS NULL OR test_type = :test_type)
  AND (:environment IS NULL OR environment = :environment)
GROUP BY DATE_TRUNC(:period, started_at), test_type, environment
ORDER BY period_start DESC, test_type, environment;

-- =============================================================================
-- DELETE OPERATIONS
-- =============================================================================

-- Delete test run (cascades to related data)
-- name: delete_test_run
DELETE FROM test_runs 
WHERE id = :test_run_id;

-- Cleanup old test runs
-- name: cleanup_old_test_runs
DELETE FROM test_runs 
WHERE started_at < NOW() - INTERVAL ':days days'
  AND test_status IN ('completed', 'failed', 'cancelled')
RETURNING id, test_type, started_at;

-- =============================================================================
-- HEALTH CHECK OPERATIONS
-- =============================================================================

-- Get database health metrics
-- name: get_database_health
SELECT 
    'ash_thrash' as database_name,
    pg_database_size(current_database()) as database_size_bytes,
    (SELECT COUNT(*) FROM test_runs) as total_test_runs,
    (SELECT COUNT(*) FROM test_runs WHERE started_at >= NOW() - INTERVAL '24 hours') as recent_test_runs,
    (SELECT COUNT(*) FROM test_runs WHERE test_status = 'running') as running_test_runs,
    (SELECT AVG(overall_pass_rate) FROM test_runs WHERE started_at >= NOW() - INTERVAL '7 days' AND test_status = 'completed') as avg_pass_rate_7d,
    NOW() as checked_at;

-- Check for stuck test runs
-- name: get_stuck_test_runs
SELECT 
    tr.*,
    EXTRACT(EPOCH FROM (NOW() - tr.started_at)) as stuck_duration_seconds
FROM test_runs tr
WHERE tr.test_status = 'running'
  AND tr.started_at < NOW() - INTERVAL ':timeout_minutes minutes'
ORDER BY tr.started_at ASC;