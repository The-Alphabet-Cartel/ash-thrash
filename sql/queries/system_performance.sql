-- sql/queries/system_performance.sql
-- System Performance Database Operations for Ash-Thrash Testing Suite
-- Repository: https://github.com/The-Alphabet-Cartel/ash-thrash

-- =============================================================================
-- INSERT OPERATIONS
-- =============================================================================

-- Insert system performance record
-- name: insert_system_performance
INSERT INTO system_performance (
    test_run_id,
    cpu_usage_percent,
    memory_usage_percent,
    disk_usage_percent,
    network_latency_ms,
    server_load_avg,
    concurrent_tests,
    server_status,
    nlp_server_response_time_ms,
    database_response_time_ms
) VALUES (
    :test_run_id,
    :cpu_usage_percent,
    :memory_usage_percent,
    :disk_usage_percent,
    :network_latency_ms,
    :server_load_avg,
    :concurrent_tests,
    :server_status,
    :nlp_server_response_time_ms,
    :database_response_time_ms
) RETURNING id, recorded_at;

-- Batch insert system performance records
-- name: batch_insert_system_performance
INSERT INTO system_performance (
    test_run_id, cpu_usage_percent, memory_usage_percent, disk_usage_percent,
    network_latency_ms, server_load_avg, concurrent_tests, server_status,
    nlp_server_response_time_ms, database_response_time_ms
)
SELECT * FROM unnest(
    :test_run_ids::uuid[],
    :cpu_usages::decimal[],
    :memory_usages::decimal[],
    :disk_usages::decimal[],
    :network_latencies::decimal[],
    :server_loads::decimal[],
    :concurrent_tests_array::integer[],
    :server_statuses::text[],
    :nlp_response_times::decimal[],
    :db_response_times::decimal[]
) RETURNING id, recorded_at;

-- =============================================================================
-- SELECT OPERATIONS
-- =============================================================================

-- Get system performance by test run
-- name: get_system_performance_by_test_run
SELECT 
    sp.*,
    tr.test_type,
    tr.started_at as test_started_at,
    tr.environment,
    tr.test_status
FROM system_performance sp
JOIN test_runs tr ON sp.test_run_id = tr.id
WHERE sp.test_run_id = :test_run_id
ORDER BY sp.recorded_at ASC;

-- Get latest system performance
-- name: get_latest_system_performance
SELECT 
    sp.*,
    tr.test_type,
    tr.started_at as test_started_at,
    tr.environment,
    tr.test_status
FROM system_performance sp
JOIN test_runs tr ON sp.test_run_id = tr.id
WHERE tr.test_status = 'completed'
ORDER BY sp.recorded_at DESC
LIMIT 1;

-- Get system performance trends
-- name: get_system_performance_trends
SELECT 
    DATE_TRUNC(:period, sp.recorded_at) as period_start,
    COUNT(*) as measurement_count,
    AVG(sp.cpu_usage_percent) as avg_cpu_usage,
    MAX(sp.cpu_usage_percent) as max_cpu_usage,
    AVG(sp.memory_usage_percent) as avg_memory_usage,
    MAX(sp.memory_usage_percent) as max_memory_usage,
    AVG(sp.disk_usage_percent) as avg_disk_usage,
    MAX(sp.disk_usage_percent) as max_disk_usage,
    AVG(sp.network_latency_ms) as avg_network_latency,
    MAX(sp.network_latency_ms) as max_network_latency,
    AVG(sp.server_load_avg) as avg_server_load,
    MAX(sp.server_load_avg) as max_server_load,
    AVG(sp.concurrent_tests) as avg_concurrent_tests,
    MAX(sp.concurrent_tests) as max_concurrent_tests,
    AVG(sp.nlp_server_response_time_ms) as avg_nlp_response_time,
    MAX(sp.nlp_server_response_time_ms) as max_nlp_response_time,
    AVG(sp.database_response_time_ms) as avg_db_response_time,
    MAX(sp.database_response_time_ms) as max_db_response_time,
    COUNT(*) FILTER (WHERE sp.server_status = 'healthy') as healthy_readings,
    COUNT(*) FILTER (WHERE sp.server_status = 'degraded') as degraded_readings,
    COUNT(*) FILTER (WHERE sp.server_status = 'unhealthy') as unhealthy_readings
FROM system_performance sp
JOIN test_runs tr ON sp.test_run_id = tr.id
WHERE sp.recorded_at >= :start_date
  AND sp.recorded_at <= :end_date
  AND (:test_type IS NULL OR tr.test_type = :test_type)
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY DATE_TRUNC(:period, sp.recorded_at)
ORDER BY period_start DESC;

-- Get system health status
-- name: get_system_health_status
SELECT 
    COUNT(*) as total_measurements,
    COUNT(*) FILTER (WHERE sp.server_status = 'healthy') as healthy_count,
    COUNT(*) FILTER (WHERE sp.server_status = 'degraded') as degraded_count,
    COUNT(*) FILTER (WHERE sp.server_status = 'unhealthy') as unhealthy_count,
    ROUND((COUNT(*) FILTER (WHERE sp.server_status = 'healthy')::decimal / COUNT(*)) * 100, 2) as health_percentage,
    AVG(sp.cpu_usage_percent) as avg_cpu_usage,
    AVG(sp.memory_usage_percent) as avg_memory_usage,
    AVG(sp.network_latency_ms) as avg_network_latency,
    AVG(sp.nlp_server_response_time_ms) as avg_nlp_response_time,
    MAX(sp.recorded_at) as last_measurement
FROM system_performance sp
JOIN test_runs tr ON sp.test_run_id = tr.id
WHERE sp.recorded_at >= COALESCE(:start_date, NOW() - INTERVAL '24 hours')
  AND sp.recorded_at <= COALESCE(:end_date, NOW())
  AND (:environment IS NULL OR tr.environment = :environment);

-- Get performance alerts
-- name: get_performance_alerts
SELECT 
    sp.*,
    tr.test_type,
    tr.environment,
    CASE 
        WHEN sp.cpu_usage_percent > :cpu_threshold THEN 'High CPU Usage'
        WHEN sp.memory_usage_percent > :memory_threshold THEN 'High Memory Usage'
        WHEN sp.network_latency_ms > :latency_threshold THEN 'High Network Latency'
        WHEN sp.nlp_server_response_time_ms > :nlp_response_threshold THEN 'Slow NLP Response'
        WHEN sp.database_response_time_ms > :db_response_threshold THEN 'Slow Database Response'
        ELSE 'Unknown Alert'
    END as alert_type
FROM system_performance sp
JOIN test_runs tr ON sp.test_run_id = tr.id
WHERE sp.recorded_at >= COALESCE(:start_date, NOW() - INTERVAL '24 hours')
  AND sp.recorded_at <= COALESCE(:end_date, NOW())
  AND (:environment IS NULL OR tr.environment = :environment)
  AND (
    sp.cpu_usage_percent > :cpu_threshold OR
    sp.memory_usage_percent > :memory_threshold OR
    sp.network_latency_ms > :latency_threshold OR
    sp.nlp_server_response_time_ms > :nlp_response_threshold OR
    sp.database_response_time_ms > :db_response_threshold OR
    sp.server_status IN ('degraded', 'unhealthy')
  )
ORDER BY sp.recorded_at DESC
LIMIT :limit OFFSET :offset;

-- Get resource utilization statistics
-- name: get_resource_utilization_statistics
SELECT 
    'CPU Usage' as resource_type,
    ROUND(AVG(sp.cpu_usage_percent), 2) as avg_usage,
    ROUND(MIN(sp.cpu_usage_percent), 2) as min_usage,
    ROUND(MAX(sp.cpu_usage_percent), 2) as max_usage,
    ROUND(STDDEV(sp.cpu_usage_percent), 2) as std_dev,
    COUNT(*) FILTER (WHERE sp.cpu_usage_percent > 80) as high_usage_count,
    COUNT(*) as total_measurements
FROM system_performance sp
JOIN test_runs tr ON sp.test_run_id = tr.id
WHERE sp.recorded_at >= :start_date
  AND sp.recorded_at <= :end_date
  AND (:environment IS NULL OR tr.environment = :environment)

UNION ALL

SELECT 
    'Memory Usage' as resource_type,
    ROUND(AVG(sp.memory_usage_percent), 2) as avg_usage,
    ROUND(MIN(sp.memory_usage_percent), 2) as min_usage,
    ROUND(MAX(sp.memory_usage_percent), 2) as max_usage,
    ROUND(STDDEV(sp.memory_usage_percent), 2) as std_dev,
    COUNT(*) FILTER (WHERE sp.memory_usage_percent > 80) as high_usage_count,
    COUNT(*) as total_measurements
FROM system_performance sp
JOIN test_runs tr ON sp.test_run_id = tr.id
WHERE sp.recorded_at >= :start_date
  AND sp.recorded_at <= :end_date
  AND (:environment IS NULL OR tr.environment = :environment)

UNION ALL

SELECT 
    'Disk Usage' as resource_type,
    ROUND(AVG(sp.disk_usage_percent), 2) as avg_usage,
    ROUND(MIN(sp.disk_usage_percent), 2) as min_usage,
    ROUND(MAX(sp.disk_usage_percent), 2) as max_usage,
    ROUND(STDDEV(sp.disk_usage_percent), 2) as std_dev,
    COUNT(*) FILTER (WHERE sp.disk_usage_percent > 80) as high_usage_count,
    COUNT(*) as total_measurements
FROM system_performance sp
JOIN test_runs tr ON sp.test_run_id = tr.id
WHERE sp.recorded_at >= :start_date
  AND sp.recorded_at <= :end_date
  AND (:environment IS NULL OR tr.environment = :environment)

ORDER BY resource_type;

-- Get response time analysis
-- name: get_response_time_analysis
SELECT 
    'NLP Server Response Time' as metric_type,
    ROUND(AVG(sp.nlp_server_response_time_ms), 2) as avg_time_ms,
    ROUND(MIN(sp.nlp_server_response_time_ms), 2) as min_time_ms,
    ROUND(MAX(sp.nlp_server_response_time_ms), 2) as max_time_ms,
    ROUND(STDDEV(sp.nlp_server_response_time_ms), 2) as std_dev_ms,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY sp.nlp_server_response_time_ms), 2) as median_ms,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY sp.nlp_server_response_time_ms), 2) as p95_ms,
    ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY sp.nlp_server_response_time_ms), 2) as p99_ms,
    COUNT(*) as measurement_count
FROM system_performance sp
JOIN test_runs tr ON sp.test_run_id = tr.id
WHERE sp.recorded_at >= :start_date
  AND sp.recorded_at <= :end_date
  AND (:environment IS NULL OR tr.environment = :environment)
  AND sp.nlp_server_response_time_ms IS NOT NULL

UNION ALL

SELECT 
    'Database Response Time' as metric_type,
    ROUND(AVG(sp.database_response_time_ms), 2) as avg_time_ms,
    ROUND(MIN(sp.database_response_time_ms), 2) as min_time_ms,
    ROUND(MAX(sp.database_response_time_ms), 2) as max_time_ms,
    ROUND(STDDEV(sp.database_response_time_ms), 2) as std_dev_ms,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY sp.database_response_time_ms), 2) as median_ms,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY sp.database_response_time_ms), 2) as p95_ms,
    ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY sp.database_response_time_ms), 2) as p99_ms,
    COUNT(*) as measurement_count
FROM system_performance sp
JOIN test_runs tr ON sp.test_run_id = tr.id
WHERE sp.recorded_at >= :start_date
  AND sp.recorded_at <= :end_date
  AND (:environment IS NULL OR tr.environment = :environment)
  AND sp.database_response_time_ms IS NOT NULL

ORDER BY metric_type;

-- Get concurrent test load analysis
-- name: get_concurrent_test_load_analysis
SELECT 
    sp.concurrent_tests,
    COUNT(*) as measurement_count,
    ROUND(AVG(sp.cpu_usage_percent), 2) as avg_cpu_usage,
    ROUND(AVG(sp.memory_usage_percent), 2) as avg_memory_usage,
    ROUND(AVG(sp.nlp_server_response_time_ms), 2) as avg_nlp_response_time,
    ROUND(AVG(sp.database_response_time_ms), 2) as avg_db_response_time,
    COUNT(*) FILTER (WHERE sp.server_status = 'healthy') as healthy_count,
    COUNT(*) FILTER (WHERE sp.server_status = 'degraded') as degraded_count,
    COUNT(*) FILTER (WHERE sp.server_status = 'unhealthy') as unhealthy_count
FROM system_performance sp
JOIN test_runs tr ON sp.test_run_id = tr.id
WHERE sp.recorded_at >= :start_date
  AND sp.recorded_at <= :end_date
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY sp.concurrent_tests
ORDER BY sp.concurrent_tests ASC;

-- =============================================================================
-- UPDATE OPERATIONS
-- =============================================================================

-- Update system performance record
-- name: update_system_performance
UPDATE system_performance 
SET 
    cpu_usage_percent = :cpu_usage_percent,
    memory_usage_percent = :memory_usage_percent,
    disk_usage_percent = :disk_usage_percent,
    network_latency_ms = :network_latency_ms,
    server_load_avg = :server_load_avg,
    concurrent_tests = :concurrent_tests,
    server_status = :server_status,
    nlp_server_response_time_ms = :nlp_server_response_time_ms,
    database_response_time_ms = :database_response_time_ms
WHERE id = :performance_id;

-- =============================================================================
-- DELETE OPERATIONS
-- =============================================================================

-- Delete system performance by test run
-- name: delete_system_performance_by_test_run
DELETE FROM system_performance 
WHERE test_run_id = :test_run_id;

-- Delete old system performance records
-- name: delete_old_system_performance
DELETE FROM system_performance sp
USING test_runs tr
WHERE sp.test_run_id = tr.id
  AND tr.started_at < NOW() - INTERVAL ':days days'
  AND tr.test_status IN ('completed', 'failed', 'cancelled')
RETURNING sp.id, sp.recorded_at;

-- =============================================================================
-- MONITORING QUERIES
-- =============================================================================

-- Get system health dashboard
-- name: get_system_health_dashboard
SELECT 
    DATE_TRUNC('hour', sp.recorded_at) as hour_start,
    AVG(sp.cpu_usage_percent) as avg_cpu,
    MAX(sp.cpu_usage_percent) as max_cpu,
    AVG(sp.memory_usage_percent) as avg_memory,
    MAX(sp.memory_usage_percent) as max_memory,
    AVG(sp.nlp_server_response_time_ms) as avg_nlp_response,
    MAX(sp.nlp_server_response_time_ms) as max_nlp_response,
    COUNT(*) FILTER (WHERE sp.server_status = 'healthy') as healthy_readings,
    COUNT(*) FILTER (WHERE sp.server_status = 'degraded') as degraded_readings,
    COUNT(*) FILTER (WHERE sp.server_status = 'unhealthy') as unhealthy_readings,
    COUNT(*) as total_readings
FROM system_performance sp
JOIN test_runs tr ON sp.test_run_id = tr.id
WHERE sp.recorded_at >= NOW() - INTERVAL ':hours hours'
  AND (:environment IS NULL OR tr.environment = :environment)
GROUP BY DATE_TRUNC('hour', sp.recorded_at)
ORDER BY hour_start DESC;

-- Get system performance summary
-- name: get_system_performance_summary
SELECT 
    COUNT(*) as total_measurements,
    ROUND(AVG(sp.cpu_usage_percent), 2) as avg_cpu_usage,
    ROUND(MAX(sp.cpu_usage_percent), 2) as max_cpu_usage,
    ROUND(AVG(sp.memory_usage_percent), 2) as avg_memory_usage,
    ROUND(MAX(sp.memory_usage_percent), 2) as max_memory_usage,
    ROUND(AVG(sp.network_latency_ms), 2) as avg_network_latency,
    ROUND(MAX(sp.network_latency_ms), 2) as max_network_latency,
    ROUND(AVG(sp.nlp_server_response_time_ms), 2) as avg_nlp_response_time,
    ROUND(MAX(sp.nlp_server_response_time_ms), 2) as max_nlp_response_time,
    ROUND(AVG(sp.database_response_time_ms), 2) as avg_db_response_time,
    ROUND(MAX(sp.database_response_time_ms), 2) as max_db_response_time,
    ROUND(AVG(sp.concurrent_tests), 1) as avg_concurrent_tests,
    MAX(sp.concurrent_tests) as max_concurrent_tests,
    COUNT(*) FILTER (WHERE sp.server_status = 'healthy') as healthy_count,
    COUNT(*) FILTER (WHERE sp.server_status = 'degraded') as degraded_count,
    COUNT(*) FILTER (WHERE sp.server_status = 'unhealthy') as unhealthy_count,
    MIN(sp.recorded_at) as period_start,
    MAX(sp.recorded_at) as period_end
FROM system_performance sp
JOIN test_runs tr ON sp.test_run_id = tr.id
WHERE sp.recorded_at >= :start_date
  AND sp.recorded_at <= :end_date
  AND (:environment IS NULL OR tr.environment = :environment);