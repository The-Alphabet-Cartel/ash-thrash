-- Ash-Thrash Testing Database Schema
-- Initialize PostgreSQL database for storing historical test results
-- Repository: https://github.com/The-Alphabet-Cartel/ash-thrash

-- Enable UUID extension for generating unique identifiers
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schema for ash-thrash if it doesn't exist
CREATE SCHEMA IF NOT EXISTS ash_thrash;

-- Set search path to include ash-thrash schema
SET search_path TO ash_thrash, public;

-- =============================================================================
-- MAIN TABLES
-- =============================================================================

-- Test runs table - stores overall test execution information
CREATE TABLE IF NOT EXISTS test_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_type VARCHAR(50) NOT NULL CHECK (test_type IN ('comprehensive', 'quick_validation', 'custom')),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    total_tests INTEGER NOT NULL DEFAULT 0,
    passed_tests INTEGER NOT NULL DEFAULT 0,
    failed_tests INTEGER NOT NULL DEFAULT 0,
    error_tests INTEGER NOT NULL DEFAULT 0,
    overall_pass_rate DECIMAL(5,2) NOT NULL DEFAULT 0.0 CHECK (overall_pass_rate >= 0 AND overall_pass_rate <= 100),
    avg_response_time_ms DECIMAL(8,2),
    avg_processing_time_ms DECIMAL(8,2),
    execution_time_seconds DECIMAL(8,2),
    goal_achievement_rate DECIMAL(5,2) CHECK (goal_achievement_rate >= 0 AND goal_achievement_rate <= 100),
    nlp_server_url VARCHAR(255),
    results_file_path TEXT,
    test_status VARCHAR(20) NOT NULL DEFAULT 'running' CHECK (test_status IN ('running', 'completed', 'failed', 'cancelled')),
    error_message TEXT,
    metadata JSONB, -- Store additional test metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Category performance table - stores performance by test category
CREATE TABLE IF NOT EXISTS category_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_run_id UUID NOT NULL REFERENCES test_runs(id) ON DELETE CASCADE,
    category_name VARCHAR(50) NOT NULL,
    category_type VARCHAR(20) NOT NULL CHECK (category_type IN ('definite', 'maybe')),
    priority_level VARCHAR(20) NOT NULL CHECK (priority_level IN ('high', 'medium', 'low', 'none')),
    total_tests INTEGER NOT NULL DEFAULT 0,
    passed_tests INTEGER NOT NULL DEFAULT 0,
    failed_tests INTEGER NOT NULL DEFAULT 0,
    pass_rate DECIMAL(5,2) NOT NULL DEFAULT 0.0 CHECK (pass_rate >= 0 AND pass_rate <= 100),
    target_pass_rate DECIMAL(5,2) NOT NULL DEFAULT 0.0 CHECK (target_pass_rate >= 0 AND target_pass_rate <= 100),
    goal_met BOOLEAN NOT NULL DEFAULT FALSE,
    avg_confidence DECIMAL(4,3) CHECK (avg_confidence >= 0 AND avg_confidence <= 1),
    avg_response_time_ms DECIMAL(8,2),
    is_critical BOOLEAN NOT NULL DEFAULT FALSE,
    allow_escalation BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Test failures table - stores detailed information about failed tests
CREATE TABLE IF NOT EXISTS test_failures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_run_id UUID NOT NULL REFERENCES test_runs(id) ON DELETE CASCADE,
    category_performance_id UUID REFERENCES category_performance(id) ON DELETE CASCADE,
    test_phrase TEXT NOT NULL,
    expected_priority VARCHAR(20) NOT NULL CHECK (expected_priority IN ('high', 'medium', 'low', 'none')),
    detected_priority VARCHAR(20) NOT NULL CHECK (detected_priority IN ('high', 'medium', 'low', 'none')),
    confidence_score DECIMAL(4,3) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    response_time_ms DECIMAL(8,2),
    processing_time_ms DECIMAL(8,2),
    detected_categories TEXT[], -- Array of detected categories
    failure_type VARCHAR(50) NOT NULL CHECK (failure_type IN ('false_positive', 'false_negative', 'wrong_priority', 'escalation_error')),
    is_critical BOOLEAN NOT NULL DEFAULT FALSE,
    error_message TEXT,
    phrase_metadata JSONB, -- Store additional phrase metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System performance table - stores system-level performance metrics
CREATE TABLE IF NOT EXISTS system_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_run_id UUID NOT NULL REFERENCES test_runs(id) ON DELETE CASCADE,
    cpu_usage_percent DECIMAL(5,2),
    memory_usage_percent DECIMAL(5,2),
    disk_usage_percent DECIMAL(5,2),
    network_latency_ms DECIMAL(8,2),
    server_load_avg DECIMAL(4,2),
    concurrent_tests INTEGER DEFAULT 1,
    server_status VARCHAR(20) CHECK (server_status IN ('healthy', 'degraded', 'unhealthy')),
    nlp_server_response_time_ms DECIMAL(8,2),
    database_response_time_ms DECIMAL(8,2),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Test configurations table - stores test configuration snapshots
CREATE TABLE IF NOT EXISTS test_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_run_id UUID NOT NULL REFERENCES test_runs(id) ON DELETE CASCADE,
    nlp_server_url VARCHAR(255) NOT NULL,
    max_concurrent_tests INTEGER DEFAULT 5,
    timeout_seconds INTEGER DEFAULT 300,
    retry_attempts INTEGER DEFAULT 3,
    testing_goals JSONB NOT NULL, -- Store testing goals configuration
    server_config JSONB, -- Store server configuration
    environment_variables JSONB, -- Store relevant environment variables
    ash_thrash_version VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Primary lookup indexes
CREATE INDEX IF NOT EXISTS idx_test_runs_started_at ON test_runs(started_at);
CREATE INDEX IF NOT EXISTS idx_test_runs_test_type ON test_runs(test_type);
CREATE INDEX IF NOT EXISTS idx_test_runs_status ON test_runs(test_status);
CREATE INDEX IF NOT EXISTS idx_test_runs_pass_rate ON test_runs(overall_pass_rate);

-- Category performance indexes
CREATE INDEX IF NOT EXISTS idx_category_performance_test_run ON category_performance(test_run_id);
CREATE INDEX IF NOT EXISTS idx_category_performance_category ON category_performance(category_name);
CREATE INDEX IF NOT EXISTS idx_category_performance_critical ON category_performance(is_critical);
CREATE INDEX IF NOT EXISTS idx_category_performance_goal_met ON category_performance(goal_met);

-- Test failures indexes
CREATE INDEX IF NOT EXISTS idx_test_failures_test_run ON test_failures(test_run_id);
CREATE INDEX IF NOT EXISTS idx_test_failures_category ON test_failures(category_performance_id);
CREATE INDEX IF NOT EXISTS idx_test_failures_type ON test_failures(failure_type);
CREATE INDEX IF NOT EXISTS idx_test_failures_critical ON test_failures(is_critical);
CREATE INDEX IF NOT EXISTS idx_test_failures_priorities ON test_failures(expected_priority, detected_priority);

-- System performance indexes
CREATE INDEX IF NOT EXISTS idx_system_performance_test_run ON system_performance(test_run_id);
CREATE INDEX IF NOT EXISTS idx_system_performance_recorded_at ON system_performance(recorded_at);

-- Configuration indexes
CREATE INDEX IF NOT EXISTS idx_test_configurations_test_run ON test_configurations(test_run_id);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_test_runs_type_date ON test_runs(test_type, started_at);
CREATE INDEX IF NOT EXISTS idx_category_goal_achievement ON category_performance(category_name, goal_met, pass_rate);

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- Latest test results view
CREATE OR REPLACE VIEW latest_test_summary AS
SELECT 
    tr.id,
    tr.test_type,
    tr.started_at,
    tr.completed_at,
    tr.overall_pass_rate,
    tr.goal_achievement_rate,
    tr.avg_response_time_ms,
    tr.total_tests,
    tr.test_status,
    COUNT(cp.id) as categories_tested,
    COUNT(cp.id) FILTER (WHERE cp.goal_met = TRUE) as goals_achieved,
    COUNT(tf.id) as total_failures,
    COUNT(tf.id) FILTER (WHERE tf.is_critical = TRUE) as critical_failures
FROM test_runs tr
LEFT JOIN category_performance cp ON tr.id = cp.test_run_id
LEFT JOIN test_failures tf ON tr.id = tf.test_run_id
WHERE tr.started_at = (
    SELECT MAX(started_at) 
    FROM test_runs 
    WHERE test_status = 'completed'
)
GROUP BY tr.id, tr.test_type, tr.started_at, tr.completed_at, 
         tr.overall_pass_rate, tr.goal_achievement_rate, 
         tr.avg_response_time_ms, tr.total_tests, tr.test_status;

-- Testing trends view (last 30 days)
CREATE OR REPLACE VIEW testing_trends AS
SELECT 
    DATE_TRUNC('day', tr.started_at) as test_date,
    tr.test_type,
    COUNT(*) as test_count,
    AVG(tr.overall_pass_rate) as avg_pass_rate,
    AVG(tr.goal_achievement_rate) as avg_goal_achievement,
    AVG(tr.avg_response_time_ms) as avg_response_time,
    MIN(tr.overall_pass_rate) as min_pass_rate,
    MAX(tr.overall_pass_rate) as max_pass_rate,
    COUNT(*) FILTER (WHERE tr.overall_pass_rate >= 85) as good_tests,
    COUNT(*) FILTER (WHERE tr.overall_pass_rate < 70) as poor_tests
FROM test_runs tr
WHERE tr.started_at >= NOW() - INTERVAL '30 days'
  AND tr.test_status = 'completed'
GROUP BY DATE_TRUNC('day', tr.started_at), tr.test_type
ORDER BY test_date DESC, tr.test_type;

-- Category performance trends
CREATE OR REPLACE VIEW category_trends AS
SELECT 
    cp.category_name,
    DATE_TRUNC('week', tr.started_at) as week_start,
    COUNT(*) as test_count,
    AVG(cp.pass_rate) as avg_pass_rate,
    AVG(cp.target_pass_rate) as target_pass_rate,
    COUNT(*) FILTER (WHERE cp.goal_met = TRUE) as goals_met,
    AVG(cp.avg_confidence) as avg_confidence,
    AVG(cp.avg_response_time_ms) as avg_response_time
FROM category_performance cp
JOIN test_runs tr ON cp.test_run_id = tr.id
WHERE tr.started_at >= NOW() - INTERVAL '90 days'
  AND tr.test_status = 'completed'
GROUP BY cp.category_name, DATE_TRUNC('week', tr.started_at)
ORDER BY week_start DESC, cp.category_name;

-- Critical failures summary
CREATE OR REPLACE VIEW critical_failures_summary AS
SELECT 
    tf.failure_type,
    tf.expected_priority,
    tf.detected_priority,
    COUNT(*) as failure_count,
    AVG(tf.confidence_score) as avg_confidence,
    MIN(tr.started_at) as first_occurrence,
    MAX(tr.started_at) as last_occurrence,
    COUNT(DISTINCT tr.id) as affected_test_runs
FROM test_failures tf
JOIN test_runs tr ON tf.test_run_id = tr.id
WHERE tf.is_critical = TRUE
  AND tr.started_at >= NOW() - INTERVAL '30 days'
  AND tr.test_status = 'completed'
GROUP BY tf.failure_type, tf.expected_priority, tf.detected_priority
ORDER BY failure_count DESC, last_occurrence DESC;

-- System health summary
CREATE OR REPLACE VIEW system_health_summary AS
SELECT 
    DATE_TRUNC('hour', sp.recorded_at) as hour_start,
    AVG(sp.cpu_usage_percent) as avg_cpu_usage,
    AVG(sp.memory_usage_percent) as avg_memory_usage,
    AVG(sp.nlp_server_response_time_ms) as avg_nlp_response_time,
    MAX(sp.concurrent_tests) as max_concurrent_tests,
    COUNT(*) FILTER (WHERE sp.server_status = 'healthy') as healthy_readings,
    COUNT(*) FILTER (WHERE sp.server_status = 'degraded') as degraded_readings,
    COUNT(*) FILTER (WHERE sp.server_status = 'unhealthy') as unhealthy_readings,
    COUNT(*) as total_readings
FROM system_performance sp
WHERE sp.recorded_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', sp.recorded_at)
ORDER BY hour_start DESC;

-- =============================================================================
-- FUNCTIONS FOR COMMON OPERATIONS
-- =============================================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at on test_runs
CREATE TRIGGER update_test_runs_updated_at
    BEFORE UPDATE ON test_runs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate goal achievement rate
CREATE OR REPLACE FUNCTION calculate_goal_achievement_rate(test_run_uuid UUID)
RETURNS DECIMAL(5,2) AS $$
DECLARE
    total_goals INTEGER;
    achieved_goals INTEGER;
BEGIN
    SELECT 
        COUNT(*),
        COUNT(*) FILTER (WHERE goal_met = TRUE)
    INTO total_goals, achieved_goals
    FROM category_performance
    WHERE test_run_id = test_run_uuid;
    
    IF total_goals = 0 THEN
        RETURN 0.0;
    END IF;
    
    RETURN ROUND((achieved_goals::DECIMAL / total_goals::DECIMAL) * 100, 2);
END;
$$ LANGUAGE plpgsql;

-- Function to get latest test results
CREATE OR REPLACE FUNCTION get_latest_test_results(test_type_filter VARCHAR DEFAULT NULL)
RETURNS TABLE (
    test_id UUID,
    test_type VARCHAR,
    started_at TIMESTAMP WITH TIME ZONE,
    pass_rate DECIMAL,
    goal_achievement DECIMAL,
    response_time DECIMAL,
    status VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        tr.id,
        tr.test_type,
        tr.started_at,
        tr.overall_pass_rate,
        tr.goal_achievement_rate,
        tr.avg_response_time_ms,
        tr.test_status
    FROM test_runs tr
    WHERE (test_type_filter IS NULL OR tr.test_type = test_type_filter)
      AND tr.test_status = 'completed'
    ORDER BY tr.started_at DESC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- INITIAL DATA AND CONFIGURATION
-- =============================================================================

-- Insert default testing goals configuration
INSERT INTO test_configurations (
    test_run_id,
    nlp_server_url,
    testing_goals,
    ash_thrash_version
) VALUES (
    uuid_generate_v4(), -- Placeholder ID for default config
    'http://10.20.30.253:8881',
    '{
        "definite_high": {"target_pass_rate": 100.0, "critical": true, "description": "High Priority Crisis (Safety First!)"},
        "definite_medium": {"target_pass_rate": 65.0, "critical": false, "description": "Medium Priority Crisis"},
        "definite_low": {"target_pass_rate": 65.0, "critical": false, "description": "Low Priority Crisis"},
        "definite_none": {"target_pass_rate": 95.0, "critical": true, "description": "No Priority Crisis (Prevent False Positives)"},
        "maybe_high_medium": {"target_pass_rate": 90.0, "critical": false, "description": "Maybe High/Medium (No Priority Drops)"},
        "maybe_medium_low": {"target_pass_rate": 80.0, "critical": false, "description": "Maybe Medium/Low (No Priority Drops)"},
        "maybe_low_none": {"target_pass_rate": 90.0, "critical": true, "description": "Maybe Low/None (Prevent False Positives)"}
    }'::jsonb,
    '1.0.0'
) ON CONFLICT DO NOTHING;

-- =============================================================================
-- GRANTS AND PERMISSIONS
-- =============================================================================

-- Grant permissions to ash_test user (created by Docker)
GRANT USAGE ON SCHEMA ash_thrash TO ash_test;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ash_thrash TO ash_test;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ash_thrash TO ash_test;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA ash_thrash TO ash_test;

-- Grant permissions for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA ash_thrash GRANT ALL ON TABLES TO ash_test;
ALTER DEFAULT PRIVILEGES IN SCHEMA ash_thrash GRANT ALL ON SEQUENCES TO ash_test;
ALTER DEFAULT PRIVILEGES IN SCHEMA ash_thrash GRANT EXECUTE ON FUNCTIONS TO ash_test;

-- =============================================================================
-- CLEANUP AND MAINTENANCE
-- =============================================================================

-- Function to cleanup old test data (keep last 90 days by default)
CREATE OR REPLACE FUNCTION cleanup_old_test_data(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM test_runs 
    WHERE started_at < NOW() - (days_to_keep || ' days')::INTERVAL
      AND test_status IN ('completed', 'failed', 'cancelled');
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Also cleanup orphaned system performance records
    DELETE FROM system_performance 
    WHERE recorded_at < NOW() - (days_to_keep || ' days')::INTERVAL;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- MONITORING AND HEALTH CHECKS
-- =============================================================================

-- View for database health monitoring
CREATE OR REPLACE VIEW database_health AS
SELECT 
    'ash_thrash' as database_name,
    pg_database_size(current_database()) as database_size_bytes,
    (SELECT COUNT(*) FROM test_runs) as total_test_runs,
    (SELECT COUNT(*) FROM test_runs WHERE started_at >= NOW() - INTERVAL '24 hours') as recent_test_runs,
    (SELECT COUNT(*) FROM test_failures WHERE created_at >= NOW() - INTERVAL '24 hours') as recent_failures,
    (SELECT AVG(overall_pass_rate) FROM test_runs WHERE started_at >= NOW() - INTERVAL '7 days' AND test_status = 'completed') as avg_pass_rate_7d,
    NOW() as checked_at;

-- =============================================================================
-- COMPLETION MESSAGE
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ Ash-Thrash database schema initialized successfully!';
    RAISE NOTICE '📊 Tables created: test_runs, category_performance, test_failures, system_performance, test_configurations';
    RAISE NOTICE '👁️ Views created: latest_test_summary, testing_trends, category_trends, critical_failures_summary, system_health_summary, database_health';
    RAISE NOTICE '⚙️ Functions created: calculate_goal_achievement_rate, get_latest_test_results, cleanup_old_test_data';
    RAISE NOTICE '🔗 Repository: https://github.com/The-Alphabet-Cartel/ash-thrash';
END $$;