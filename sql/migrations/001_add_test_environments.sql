-- Migration 001: Add test environments and enhanced tracking
-- Created: 2025-07-26
-- Description: Add support for multiple test environments and enhanced result tracking

-- Add environment tracking to test_runs
ALTER TABLE test_runs 
ADD COLUMN IF NOT EXISTS environment VARCHAR(50) DEFAULT 'production' CHECK (environment IN ('development', 'staging', 'production', 'testing'));

ALTER TABLE test_runs 
ADD COLUMN IF NOT EXISTS git_commit_hash VARCHAR(40);

ALTER TABLE test_runs 
ADD COLUMN IF NOT EXISTS test_trigger VARCHAR(50) DEFAULT 'manual' CHECK (test_trigger IN ('manual', 'scheduled', 'webhook', 'api', 'ci_cd'));

-- Add performance tracking
ALTER TABLE test_runs 
ADD COLUMN IF NOT EXISTS memory_usage_mb DECIMAL(8,2);

ALTER TABLE test_runs 
ADD COLUMN IF NOT EXISTS cpu_usage_percent DECIMAL(5,2);

-- Add confidence score statistics
ALTER TABLE category_performance 
ADD COLUMN IF NOT EXISTS min_confidence DECIMAL(4,3) CHECK (min_confidence >= 0 AND min_confidence <= 1);

ALTER TABLE category_performance 
ADD COLUMN IF NOT EXISTS max_confidence DECIMAL(4,3) CHECK (max_confidence >= 0 AND max_confidence <= 1);

ALTER TABLE category_performance 
ADD COLUMN IF NOT EXISTS confidence_std_dev DECIMAL(4,3);

-- Add phrase difficulty tracking
ALTER TABLE test_failures 
ADD COLUMN IF NOT EXISTS phrase_difficulty VARCHAR(20) CHECK (phrase_difficulty IN ('easy', 'medium', 'hard', 'edge_case'));

ALTER TABLE test_failures 
ADD COLUMN IF NOT EXISTS expected_confidence_range DECIMAL(4,3)[];

-- Create test environments table
CREATE TABLE IF NOT EXISTS test_environments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    environment_name VARCHAR(50) NOT NULL UNIQUE,
    nlp_server_url VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    configuration JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create test schedules table
CREATE TABLE IF NOT EXISTS test_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    schedule_name VARCHAR(100) NOT NULL,
    environment_id UUID REFERENCES test_environments(id),
    test_type VARCHAR(50) NOT NULL,
    cron_expression VARCHAR(100) NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    last_run_at TIMESTAMP WITH TIME ZONE,
    next_run_at TIMESTAMP WITH TIME ZONE,
    configuration JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for new columns
CREATE INDEX IF NOT EXISTS idx_test_runs_environment ON test_runs(environment);
CREATE INDEX IF NOT EXISTS idx_test_runs_trigger ON test_runs(test_trigger);
CREATE INDEX IF NOT EXISTS idx_test_runs_commit ON test_runs(git_commit_hash);
CREATE INDEX IF NOT EXISTS idx_test_failures_difficulty ON test_failures(phrase_difficulty);

-- Add trigger for test_environments updated_at
CREATE TRIGGER update_test_environments_updated_at
    BEFORE UPDATE ON test_environments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add trigger for test_schedules updated_at  
CREATE TRIGGER update_test_schedules_updated_at
    BEFORE UPDATE ON test_schedules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert default environments
INSERT INTO test_environments (environment_name, nlp_server_url, description, configuration) VALUES
('production', 'http://10.20.30.253:8881', 'Production NLP server environment', '{"timeout": 10, "retries": 3}'),
('development', 'http://localhost:8881', 'Local development environment', '{"timeout": 5, "retries": 1}'),
('staging', 'http://10.20.30.17:8881', 'Staging environment for testing', '{"timeout": 8, "retries": 2}')
ON CONFLICT (environment_name) DO NOTHING;

-- Create enhanced views with environment support
CREATE OR REPLACE VIEW environment_performance AS
SELECT 
    te.environment_name,
    te.nlp_server_url,
    COUNT(tr.id) as total_tests,
    AVG(tr.overall_pass_rate) as avg_pass_rate,
    AVG(tr.goal_achievement_rate) as avg_goal_achievement,
    AVG(tr.avg_response_time_ms) as avg_response_time,
    MIN(tr.started_at) as first_test,
    MAX(tr.started_at) as last_test,
    COUNT(tr.id) FILTER (WHERE tr.started_at >= NOW() - INTERVAL '7 days') as tests_last_7d
FROM test_environments te
LEFT JOIN test_runs tr ON te.environment_name = tr.environment
WHERE te.is_active = TRUE
GROUP BY te.environment_name, te.nlp_server_url
ORDER BY avg_pass_rate DESC;

-- Function to get environment comparison
CREATE OR REPLACE FUNCTION compare_environments(
    env1 VARCHAR,
    env2 VARCHAR,
    days_back INTEGER DEFAULT 30
)
RETURNS TABLE (
    metric VARCHAR,
    environment_1 DECIMAL,
    environment_2 DECIMAL,
    difference DECIMAL,
    better_environment VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    WITH env_stats AS (
        SELECT 
            tr.environment,
            AVG(tr.overall_pass_rate) as avg_pass_rate,
            AVG(tr.goal_achievement_rate) as avg_goal_achievement,
            AVG(tr.avg_response_time_ms) as avg_response_time,
            COUNT(*) as test_count
        FROM test_runs tr
        WHERE tr.environment IN (env1, env2)
          AND tr.started_at >= NOW() - (days_back || ' days')::INTERVAL
          AND tr.test_status = 'completed'
        GROUP BY tr.environment
    ),
    pivoted AS (
        SELECT 
            MAX(CASE WHEN environment = env1 THEN avg_pass_rate END) as env1_pass_rate,
            MAX(CASE WHEN environment = env2 THEN avg_pass_rate END) as env2_pass_rate,
            MAX(CASE WHEN environment = env1 THEN avg_goal_achievement END) as env1_goal_achievement,
            MAX(CASE WHEN environment = env2 THEN avg_goal_achievement END) as env2_goal_achievement,
            MAX(CASE WHEN environment = env1 THEN avg_response_time END) as env1_response_time,
            MAX(CASE WHEN environment = env2 THEN avg_response_time END) as env2_response_time
        FROM env_stats
    )
    SELECT 
        'pass_rate'::VARCHAR,
        p.env1_pass_rate,
        p.env2_pass_rate,
        p.env1_pass_rate - p.env2_pass_rate,
        CASE WHEN p.env1_pass_rate > p.env2_pass_rate THEN env1 ELSE env2 END
    FROM pivoted p
    UNION ALL
    SELECT 
        'goal_achievement'::VARCHAR,
        p.env1_goal_achievement,
        p.env2_goal_achievement,
        p.env1_goal_achievement - p.env2_goal_achievement,
        CASE WHEN p.env1_goal_achievement > p.env2_goal_achievement THEN env1 ELSE env2 END
    FROM pivoted p
    UNION ALL
    SELECT 
        'response_time'::VARCHAR,
        p.env1_response_time,
        p.env2_response_time,
        p.env1_response_time - p.env2_response_time,
        CASE WHEN p.env1_response_time < p.env2_response_time THEN env1 ELSE env2 END -- Lower is better for response time
    FROM pivoted p;
END;
$$ LANGUAGE plpgsql;

-- Migration completion
INSERT INTO test_runs (
    test_type,
    started_at,
    completed_at,
    total_tests,
    passed_tests,
    overall_pass_rate,
    test_status,
    environment,
    test_trigger,
    metadata
) VALUES (
    'migration',
    NOW(),
    NOW(),
    0,
    0,
    0,
    'completed',
    'system',
    'migration',
    '{"migration": "001_add_test_environments", "description": "Added environment tracking and enhanced metrics"}'::jsonb
);

-- Log migration completion
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 001 completed successfully!';
    RAISE NOTICE '🏗️ Added: environment tracking, test schedules, enhanced performance metrics';
    RAISE NOTICE '📊 New tables: test_environments, test_schedules';
    RAISE NOTICE '🔧 New functions: compare_environments';
END $$;