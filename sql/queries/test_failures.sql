-- sql/queries/test_failures.sql
-- Test Failures Database Operations for Ash-Thrash Testing Suite
-- Repository: https://github.com/The-Alphabet-Cartel/ash-thrash

-- =============================================================================
-- INSERT OPERATIONS
-- =============================================================================

-- Insert test failure record
-- name: insert_test_failure
INSERT INTO test_failures (
    test_run_id,
    category_performance_id,
    test_phrase,
    expected_priority,
    detected_priority,
    confidence_score,
    response_time_ms,
    processing_time_ms,
    detected_categories,
    failure_type,
    is_critical,
    error_message,
    phrase_difficulty,
    expected_confidence_range,
    phrase_metadata
) VALUES (
    :test_run_id,
    :category_performance_id,
    :test_phrase,
    :expected_priority,
    :detected_priority,
    :confidence_score,
    :response_time_ms,
    :processing_time_ms,
    :detected_categories,
    :failure_type,
    :is_critical,
    :error_message,
    :phrase_difficulty,
    :expected_confidence_range,
    :phrase_metadata
) RETURNING id, created_at;

-- Batch insert test failures
-- name: batch_insert_test_failures
INSERT INTO test_failures (
    test_run_id, category_performance_id, test_phrase, expected_priority,
    detected_priority, confidence_score, response_time_ms, processing_time_ms,
    detected_categories, failure_type, is_critical, error_message,
    phrase_difficulty, phrase_metadata
)
SELECT * FROM unnest(
    :test_run_ids::uuid[],
    :category_performance_ids::uuid[],
    :test_phrases::text[],
    :expected_priorities::text[],
    :detected_priorities::text[],
    :confidence_scores::decimal[],
    :response_times::decimal[],
    :processing_times::decimal[],
    :detected_categories_array::text[][],
    :failure_types::text[],
    :is_criticals::boolean[],
    :error_messages::text[],
    :phrase_difficulties::text[],
    :phrase_metadatas::jsonb[]
) RETURNING id;

-- =============================================================================
-- SELECT OPERATIONS
-- =============================================================================

-- Get test failures by test run
-- name: get_test_failures_by_test_run
SELECT 
    tf.*,
    cp.category_name,
    cp.category_type,
    cp.priority_level as category_priority,
    tr.test_type,
    tr.started_at as test_date,
    tr.environment
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
LEFT JOIN category_performance cp ON tf.category_performance_id = cp.id
WHERE tf.test_run_id = :test_run_id
  AND (:failure_type IS NULL OR tf.failure_type = :failure_type)
  AND (:is_critical IS NULL OR tf.is_critical = :is_critical)
ORDER BY tf.is_critical DESC, tf.created_at ASC;

-- Get critical test failures
-- name: get_critical_test_failures
SELECT 
    tf.*,
    cp.category_name,
    cp.category_type,
    cp.priority_level as category_priority,
    tr.test_type,
    tr.started_at as test_date,
    tr.environment,
    tr.overall_pass_rate as test_pass_rate
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
LEFT JOIN category_performance cp ON tf.category_performance_id = cp.id
WHERE tf.is_critical = TRUE
  AND tr.test_status = 'completed'
  AND tr.started_at >= COALESCE(:start_date, tr.started_at)
  AND tr.started_at <= COALESCE(:end_date, tr.started_at)
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
  AND (:failure_type IS NULL OR tf.failure_type = :failure_type)
ORDER BY tr.started_at DESC, tf.created_at ASC
LIMIT :limit OFFSET :offset;

-- Get failure patterns by phrase
-- name: get_failure_patterns_by_phrase
SELECT 
    tf.test_phrase,
    tf.expected_priority,
    tf.phrase_difficulty,
    COUNT(*) as failure_count,
    COUNT(DISTINCT tf.test_run_id) as test_runs_affected,
    ARRAY_AGG(DISTINCT tf.detected_priority) as detected_priorities,
    ARRAY_AGG(DISTINCT tf.failure_type) as failure_types,
    AVG(tf.confidence_score) as avg_confidence,
    MIN(tf.confidence_score) as min_confidence,
    MAX(tf.confidence_score) as max_confidence,
    AVG(tf.response_time_ms) as avg_response_time,
    MIN(tr.started_at) as first_failure,
    MAX(tr.started_at) as last_failure,
    COUNT(*) FILTER (WHERE tf.is_critical = TRUE) as critical_failures
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
  AND (:expected_priority IS NULL OR tf.expected_priority = :expected_priority)
  AND (:phrase_difficulty IS NULL OR tf.phrase_difficulty = :phrase_difficulty)
GROUP BY tf.test_phrase, tf.expected_priority, tf.phrase_difficulty
HAVING COUNT(*) >= :min_failure_count
ORDER BY failure_count DESC, last_failure DESC;

-- Get failure type analysis
-- name: get_failure_type_analysis
SELECT 
    tf.failure_type,
    tf.expected_priority,
    tf.detected_priority,
    COUNT(*) as failure_count,
    COUNT(DISTINCT tf.test_run_id) as test_runs_affected,
    COUNT(*) FILTER (WHERE tf.is_critical = TRUE) as critical_failures,
    AVG(tf.confidence_score) as avg_confidence,
    STDDEV(tf.confidence_score) as confidence_std_dev,
    AVG(tf.response_time_ms) as avg_response_time,
    COUNT(DISTINCT tf.test_phrase) as unique_phrases_affected,
    MIN(tr.started_at) as first_occurrence,
    MAX(tr.started_at) as last_occurrence
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY tf.failure_type, tf.expected_priority, tf.detected_priority
ORDER BY failure_count DESC, last_occurrence DESC;

-- Get recent failure trends
-- name: get_recent_failure_trends
SELECT 
    DATE_TRUNC(:period, tr.started_at) as period_start,
    tf.failure_type,
    COUNT(*) as failure_count,
    COUNT(*) FILTER (WHERE tf.is_critical = TRUE) as critical_failures,
    COUNT(DISTINCT tf.test_phrase) as unique_phrases,
    AVG(tf.confidence_score) as avg_confidence,
    COUNT(DISTINCT tr.id) as test_runs_affected
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY DATE_TRUNC(:period, tr.started_at), tf.failure_type
ORDER BY period_start DESC, failure_count DESC;

-- Get problematic phrases
-- name: get_problematic_phrases
SELECT 
    tf.test_phrase,
    tf.expected_priority,
    tf.phrase_difficulty,
    COUNT(*) as total_failures,
    COUNT(DISTINCT tf.test_run_id) as test_runs_with_failures,
    COUNT(*) FILTER (WHERE tf.failure_type = 'false_positive') as false_positives,
    COUNT(*) FILTER (WHERE tf.failure_type = 'false_negative') as false_negatives,
    COUNT(*) FILTER (WHERE tf.failure_type = 'wrong_priority') as wrong_priorities,
    COUNT(*) FILTER (WHERE tf.failure_type = 'escalation_error') as escalation_errors,
    COUNT(*) FILTER (WHERE tf.is_critical = TRUE) as critical_failures,
    AVG(tf.confidence_score) as avg_confidence,
    STDDEV(tf.confidence_score) as confidence_variation,
    AVG(tf.response_time_ms) as avg_response_time,
    ARRAY_AGG(DISTINCT tf.detected_priority) as detected_priorities,
    MIN(tr.started_at) as first_failure_date,
    MAX(tr.started_at) as last_failure_date
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY tf.test_phrase, tf.expected_priority, tf.phrase_difficulty
HAVING COUNT(*) >= :min_failure_threshold
ORDER BY total_failures DESC, critical_failures DESC;

-- Get confidence score analysis
-- name: get_confidence_score_analysis
SELECT 
    tf.expected_priority,
    tf.detected_priority,
    tf.failure_type,
    COUNT(*) as failure_count,
    AVG(tf.confidence_score) as avg_confidence,
    STDDEV(tf.confidence_score) as confidence_std_dev,
    MIN(tf.confidence_score) as min_confidence,
    MAX(tf.confidence_score) as max_confidence,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY tf.confidence_score) as confidence_q1,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY tf.confidence_score) as confidence_median,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY tf.confidence_score) as confidence_q3,
    COUNT(*) FILTER (WHERE tf.confidence_score < 0.5) as low_confidence_count,
    COUNT(*) FILTER (WHERE tf.confidence_score >= 0.8) as high_confidence_count
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
  AND tf.confidence_score IS NOT NULL
GROUP BY tf.expected_priority, tf.detected_priority, tf.failure_type
ORDER BY failure_count DESC, avg_confidence DESC;

-- =============================================================================
-- UPDATE OPERATIONS
-- =============================================================================

-- Update test failure classification
-- name: update_test_failure_classification
UPDATE test_failures 
SET 
    failure_type = :failure_type,
    is_critical = :is_critical,
    phrase_difficulty = :phrase_difficulty,
    phrase_metadata = :phrase_metadata
WHERE id = :failure_id;

-- =============================================================================
-- DELETE OPERATIONS
-- =============================================================================

-- Delete test failures by test run
-- name: delete_test_failures_by_test_run
DELETE FROM test_failures 
WHERE test_run_id = :test_run_id;

-- Delete old test failures
-- name: delete_old_test_failures
DELETE FROM test_failures tf
USING test_runs tr
WHERE tf.test_run_id = tr.id
  AND tr.started_at < NOW() - INTERVAL ':days days'
  AND tr.test_status IN ('completed', 'failed', 'cancelled')
RETURNING tf.id, tf.test_phrase, tr.started_at;

-- =============================================================================
-- REPORTING QUERIES
-- =============================================================================

-- Get failure summary report
-- name: get_failure_summary_report
SELECT 
    'Total Failures' as metric,
    COUNT(*)::text as value,
    'failures' as unit
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date

UNION ALL

SELECT 
    'Critical Failures' as metric,
    COUNT(*)::text as value,
    'failures' as unit
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
WHERE tf.is_critical = TRUE
  AND tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date

UNION ALL

SELECT 
    'False Positives' as metric,
    COUNT(*)::text as value,
    'failures' as unit
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
WHERE tf.failure_type = 'false_positive'
  AND tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date

UNION ALL

SELECT 
    'False Negatives' as metric,
    COUNT(*)::text as value,
    'failures' as unit
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
WHERE tf.failure_type = 'false_negative'
  AND tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date

UNION ALL

SELECT 
    'Average Confidence' as metric,
    ROUND(AVG(tf.confidence_score), 3)::text as value,
    'score' as unit
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date
  AND tf.confidence_score IS NOT NULL

ORDER BY 
    CASE metric
        WHEN 'Total Failures' THEN 1
        WHEN 'Critical Failures' THEN 2
        WHEN 'False Positives' THEN 3
        WHEN 'False Negatives' THEN 4
        WHEN 'Average Confidence' THEN 5
    END;

-- Get top failing phrases report
-- name: get_top_failing_phrases_report
SELECT 
    tf.test_phrase,
    tf.expected_priority,
    tf.phrase_difficulty,
    COUNT(*) as failure_count,
    COUNT(*) FILTER (WHERE tf.is_critical = TRUE) as critical_count,
    ROUND(AVG(tf.confidence_score), 3) as avg_confidence,
    ARRAY_AGG(DISTINCT tf.detected_priority ORDER BY tf.detected_priority) as detected_priorities,
    MAX(tr.started_at) as last_failure
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
WHERE tr.test_status = 'completed'
  AND tr.started_at >= :start_date
  AND tr.started_at <= :end_date
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY tf.test_phrase, tf.expected_priority, tf.phrase_difficulty
ORDER BY failure_count DESC, critical_count DESC
LIMIT :limit;