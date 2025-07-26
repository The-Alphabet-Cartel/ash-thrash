-- sql/queries/maintenance.sql
-- Database Maintenance and Utility Operations for Ash-Thrash Testing Suite
-- Repository: https://github.com/The-Alphabet-Cartel/ash-thrash

-- =============================================================================
-- DATA CLEANUP OPERATIONS
-- =============================================================================

-- Cleanup old test data (comprehensive cleanup)
-- name: cleanup_old_test_data
WITH deleted_runs AS (
    DELETE FROM test_runs 
    WHERE started_at < NOW() - INTERVAL ':retention_days days'
      AND test_status IN ('completed', 'failed', 'cancelled')
    RETURNING id, test_type, started_at
)
SELECT 
    COUNT(*) as deleted_test_runs,
    MIN(started_at) as oldest_deleted,
    MAX(started_at) as newest_deleted,
    COUNT(*) FILTER (WHERE test_type = 'comprehensive') as comprehensive_deleted,
    COUNT(*) FILTER (WHERE test_type = 'quick_validation') as quick_validation_deleted,
    COUNT(*) FILTER (WHERE test_type = 'custom') as custom_deleted
FROM deleted_runs;

-- Cleanup orphaned category performance records
-- name: cleanup_orphaned_category_performance
WITH deleted_categories AS (
    DELETE FROM category_performance cp
    WHERE NOT EXISTS (
        SELECT 1 FROM test_runs tr 
        WHERE tr.id = cp.test_run_id
    )
    RETURNING cp.id, cp.category_name, cp.created_at
)
SELECT 
    COUNT(*) as deleted_category_records,
    COUNT(DISTINCT category_name) as affected_categories,
    MIN(created_at) as oldest_deleted,
    MAX(created_at) as newest_deleted
FROM deleted_categories;

-- Cleanup orphaned test failure records
-- name: cleanup_orphaned_test_failures
WITH deleted_failures AS (
    DELETE FROM test_failures tf
    WHERE NOT EXISTS (
        SELECT 1 FROM test_runs tr 
        WHERE tr.id = tf.test_run_id
    )
    RETURNING tf.id, tf.failure_type, tf.created_at
)
SELECT 
    COUNT(*) as deleted_failure_records,
    COUNT(*) FILTER (WHERE failure_type = 'false_positive') as false_positive_deleted,
    COUNT(*) FILTER (WHERE failure_type = 'false_negative') as false_negative_deleted,
    COUNT(*) FILTER (WHERE failure_type = 'wrong_priority') as wrong_priority_deleted,
    COUNT(*) FILTER (WHERE failure_type = 'escalation_error') as escalation_error_deleted,
    MIN(created_at) as oldest_deleted,
    MAX(created_at) as newest_deleted
FROM deleted_failures;

-- Cleanup orphaned system performance records
-- name: cleanup_orphaned_system_performance
WITH deleted_performance AS (
    DELETE FROM system_performance sp
    WHERE NOT EXISTS (
        SELECT 1 FROM test_runs tr 
        WHERE tr.id = sp.test_run_id
    )
    RETURNING sp.id, sp.recorded_at
)
SELECT 
    COUNT(*) as deleted_performance_records,
    MIN(recorded_at) as oldest_deleted,
    MAX(recorded_at) as newest_deleted
FROM deleted_performance;

-- Archive old test data to backup tables
-- name: archive_old_test_data
-- Create backup tables for archiving
CREATE TABLE IF NOT EXISTS test_runs_archive AS 
SELECT * FROM test_runs WHERE FALSE;

CREATE TABLE IF NOT EXISTS category_performance_archive AS 
SELECT * FROM category_performance WHERE FALSE;

CREATE TABLE IF NOT EXISTS test_failures_archive AS 
SELECT * FROM test_failures WHERE FALSE;

CREATE TABLE IF NOT EXISTS system_performance_archive AS 
SELECT * FROM system_performance WHERE FALSE;

-- Archive test runs older than specified days
WITH archived_runs AS (
    INSERT INTO test_runs_archive 
    SELECT * FROM test_runs 
    WHERE started_at < NOW() - INTERVAL ':archive_days days'
      AND test_status IN ('completed', 'failed', 'cancelled')
    RETURNING id
),
archived_categories AS (
    INSERT INTO category_performance_archive
    SELECT cp.* FROM category_performance cp
    WHERE cp.test_run_id IN (SELECT id FROM archived_runs)
    RETURNING id
),
archived_failures AS (
    INSERT INTO test_failures_archive
    SELECT tf.* FROM test_failures tf
    WHERE tf.test_run_id IN (SELECT id FROM archived_runs)
    RETURNING id
),
archived_performance AS (
    INSERT INTO system_performance_archive
    SELECT sp.* FROM system_performance sp
    WHERE sp.test_run_id IN (SELECT id FROM archived_runs)
    RETURNING id
)
SELECT 
    (SELECT COUNT(*) FROM archived_runs) as archived_test_runs,
    (SELECT COUNT(*) FROM archived_categories) as archived_categories,
    (SELECT COUNT(*) FROM archived_failures) as archived_failures,
    (SELECT COUNT(*) FROM archived_performance) as archived_performance_records;

-- =============================================================================
-- DATABASE OPTIMIZATION OPERATIONS
-- =============================================================================

-- Analyze and vacuum tables for performance
-- name: optimize_database_tables
-- Note: This should be run as separate statements
ANALYZE test_runs;
ANALYZE category_performance;
ANALYZE test_failures;
ANALYZE system_performance;
ANALYZE test_configurations;

VACUUM ANALYZE test_runs;
VACUUM ANALYZE category_performance;
VACUUM ANALYZE test_failures;
VACUUM ANALYZE system_performance;
VACUUM ANALYZE test_configurations;

-- Reindex all tables for optimal performance
-- name: reindex_database_tables
REINDEX TABLE test_runs;
REINDEX TABLE category_performance;
REINDEX TABLE test_failures;
REINDEX TABLE system_performance;
REINDEX TABLE test_configurations;

-- Update table statistics for query optimization
-- name: update_table_statistics
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables 
WHERE schemaname = 'ash_thrash'
ORDER BY tablename;

-- =============================================================================
-- DATABASE HEALTH MONITORING
-- =============================================================================

-- Check database size and growth
-- name: check_database_size
SELECT 
    pg_database.datname as database_name,
    pg_size_pretty(pg_database_size(pg_database.datname)) as database_size,
    pg_database_size(pg_database.datname) as database_size_bytes
FROM pg_database 
WHERE pg_database.datname = current_database()

UNION ALL

SELECT 
    'ash_thrash_schema' as database_name,
    pg_size_pretty(SUM(pg_total_relation_size(schemaname||'.'||tablename))) as database_size,
    SUM(pg_total_relation_size(schemaname||'.'||tablename)) as database_size_bytes
FROM pg_tables 
WHERE schemaname = 'ash_thrash';

-- Check table sizes and row counts
-- name: check_table_sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) as index_size,
    pg_total_relation_size(schemaname||'.'||tablename) as total_size_bytes,
    (SELECT COUNT(*) FROM test_runs) as row_count
FROM pg_tables 
WHERE schemaname = 'ash_thrash' AND tablename = 'test_runs'

UNION ALL

SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) as index_size,
    pg_total_relation_size(schemaname||'.'||tablename) as total_size_bytes,
    (SELECT COUNT(*) FROM category_performance) as row_count
FROM pg_tables 
WHERE schemaname = 'ash_thrash' AND tablename = 'category_performance'

UNION ALL

SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) as index_size,
    pg_total_relation_size(schemaname||'.'||tablename) as total_size_bytes,
    (SELECT COUNT(*) FROM test_failures) as row_count
FROM pg_tables 
WHERE schemaname = 'ash_thrash' AND tablename = 'test_failures'

UNION ALL

SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) as index_size,
    pg_total_relation_size(schemaname||'.'||tablename) as total_size_bytes,
    (SELECT COUNT(*) FROM system_performance) as row_count
FROM pg_tables 
WHERE schemaname = 'ash_thrash' AND tablename = 'system_performance'

ORDER BY total_size_bytes DESC;

-- Check index usage and efficiency
-- name: check_index_usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan,
    CASE 
        WHEN idx_scan = 0 THEN 'Unused'
        WHEN idx_scan < 10 THEN 'Low Usage'
        WHEN idx_scan < 100 THEN 'Medium Usage'
        ELSE 'High Usage'
    END as usage_level,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes 
WHERE schemaname = 'ash_thrash'
ORDER BY idx_scan DESC, pg_relation_size(indexrelid) DESC;

-- Check for missing or duplicate indexes
-- name: check_index_recommendations
SELECT 
    schemaname,
    tablename,
    attname as column_name,
    n_distinct,
    correlation,
    CASE 
        WHEN n_distinct = -1 THEN 'High Cardinality (Index Recommended)'
        WHEN n_distinct > 100 THEN 'Medium Cardinality (Consider Index)'
        WHEN n_distinct < 10 THEN 'Low Cardinality (Index Not Recommended)'
        ELSE 'Unknown Cardinality'
    END as index_recommendation
FROM pg_stats 
WHERE schemaname = 'ash_thrash'
  AND tablename IN ('test_runs', 'category_performance', 'test_failures', 'system_performance')
ORDER BY tablename, n_distinct DESC;

-- =============================================================================
-- DATA INTEGRITY CHECKS
-- =============================================================================

-- Check for data consistency issues
-- name: check_data_integrity
-- Check for test runs with mismatched totals
SELECT 
    'Test Run Total Mismatch' as issue_type,
    COUNT(*) as issue_count,
    'Test runs where passed + failed + error != total' as description
FROM test_runs 
WHERE (passed_tests + failed_tests + error_tests) != total_tests

UNION ALL

-- Check for category performance without test runs
SELECT 
    'Orphaned Category Performance' as issue_type,
    COUNT(*) as issue_count,
    'Category performance records without valid test runs' as description
FROM category_performance cp
WHERE NOT EXISTS (SELECT 1 FROM test_runs tr WHERE tr.id = cp.test_run_id)

UNION ALL

-- Check for test failures without test runs
SELECT 
    'Orphaned Test Failures' as issue_type,
    COUNT(*) as issue_count,
    'Test failure records without valid test runs' as description
FROM test_failures tf
WHERE NOT EXISTS (SELECT 1 FROM test_runs tr WHERE tr.id = tf.test_run_id)

UNION ALL

-- Check for invalid pass rates
SELECT 
    'Invalid Pass Rates' as issue_type,
    COUNT(*) as issue_count,
    'Records with pass rates outside 0-100 range' as description
FROM (
    SELECT overall_pass_rate FROM test_runs WHERE overall_pass_rate < 0 OR overall_pass_rate > 100
    UNION ALL
    SELECT pass_rate FROM category_performance WHERE pass_rate < 0 OR pass_rate > 100
) invalid_rates

UNION ALL

-- Check for future test dates
SELECT 
    'Future Test Dates' as issue_type,
    COUNT(*) as issue_count,
    'Test runs with start dates in the future' as description
FROM test_runs 
WHERE started_at > NOW()

ORDER BY issue_count DESC;

-- Check for referential integrity
-- name: check_referential_integrity
SELECT 
    'Category Performance' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE test_run_id IS NOT NULL) as with_test_run,
    COUNT(*) - COUNT(*) FILTER (WHERE test_run_id IS NOT NULL) as orphaned_records
FROM category_performance

UNION ALL

SELECT 
    'Test Failures' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE test_run_id IS NOT NULL) as with_test_run,
    COUNT(*) - COUNT(*) FILTER (WHERE test_run_id IS NOT NULL) as orphaned_records
FROM test_failures

UNION ALL

SELECT 
    'System Performance' as table_name,
    COUNT(*) as total_records,
    COUNT(*) FILTER (WHERE test_run_id IS NOT NULL) as with_test_run,
    COUNT(*) - COUNT(*) FILTER (WHERE test_run_id IS NOT NULL) as orphaned_records
FROM system_performance

ORDER BY orphaned_records DESC;

-- =============================================================================
-- BACKUP AND RESTORE OPERATIONS
-- =============================================================================

-- Generate backup metadata
-- name: generate_backup_metadata
SELECT 
    'ash_thrash_backup_' || TO_CHAR(NOW(), 'YYYY_MM_DD_HH24_MI_SS') as backup_name,
    NOW() as backup_timestamp,
    (SELECT COUNT(*) FROM test_runs) as test_runs_count,
    (SELECT COUNT(*) FROM category_performance) as category_performance_count,
    (SELECT COUNT(*) FROM test_failures) as test_failures_count,
    (SELECT COUNT(*) FROM system_performance) as system_performance_count,
    (SELECT MIN(started_at) FROM test_runs) as oldest_test_date,
    (SELECT MAX(started_at) FROM test_runs) as newest_test_date,
    pg_database_size(current_database()) as database_size_bytes,
    pg_size_pretty(pg_database_size(current_database())) as database_size_pretty;

-- Get schema version information
-- name: get_schema_version
SELECT 
    'schema_version' as info_type,
    '1.0.0' as version,
    'Initial Ash-Thrash database schema' as description,
    NOW() as checked_at

UNION ALL

SELECT 
    'table_counts' as info_type,
    (SELECT COUNT(*) FROM test_runs)::text as version,
    'Total test runs in database' as description,
    NOW() as checked_at

UNION ALL

SELECT 
    'oldest_data' as info_type,
    (SELECT MIN(started_at)::text FROM test_runs) as version,
    'Oldest test run date' as description,
    NOW() as checked_at

UNION ALL

SELECT 
    'newest_data' as info_type,
    (SELECT MAX(started_at)::text FROM test_runs) as version,
    'Newest test run date' as description,
    NOW() as checked_at;

-- =============================================================================
-- UTILITY FUNCTIONS AND MAINTENANCE TASKS
-- =============================================================================

-- Reset auto-increment sequences
-- name: reset_sequences
-- Note: These should be run as individual statements when needed
SELECT setval('test_runs_id_seq', (SELECT MAX(id) FROM test_runs));
SELECT setval('category_performance_id_seq', (SELECT MAX(id) FROM category_performance));
SELECT setval('test_failures_id_seq', (SELECT MAX(id) FROM test_failures));
SELECT setval('system_performance_id_seq', (SELECT MAX(id) FROM system_performance));

-- Get connection and activity information
-- name: get_database_activity
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    backend_start,
    state,
    query_start,
    LEFT(query, 100) as current_query
FROM pg_stat_activity 
WHERE datname = current_database()
  AND state = 'active'
  AND pid != pg_backend_pid()
ORDER BY query_start DESC;

-- Get long-running queries
-- name: get_long_running_queries
SELECT 
    pid,
    usename,
    query_start,
    NOW() - query_start as duration,
    state,
    LEFT(query, 200) as query_text
FROM pg_stat_activity
WHERE datname = current_database()
  AND state = 'active'
  AND NOW() - query_start > INTERVAL ':duration_minutes minutes'
ORDER BY query_start ASC;