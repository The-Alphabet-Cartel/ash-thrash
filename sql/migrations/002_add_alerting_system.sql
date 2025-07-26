-- Migration 002: Add alerting and notification system
-- Created: 2025-07-26
-- Description: Add comprehensive alerting system for test failures and performance issues

-- Create alert rules table
CREATE TABLE IF NOT EXISTS alert_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    rule_type VARCHAR(50) NOT NULL CHECK (rule_type IN ('pass_rate', 'response_time', 'goal_achievement', 'critical_failure', 'system_health')),
    condition_operator VARCHAR(10) NOT NULL CHECK (condition_operator IN ('<', '<=', '>', '>=', '=', '!=')),
    threshold_value DECIMAL(10,3) NOT NULL,
    environment_filter VARCHAR(50), -- NULL means all environments
    category_filter VARCHAR(50), -- NULL means all categories
    severity VARCHAR(20) NOT NULL DEFAULT 'warning' CHECK (severity IN ('info', 'warning', 'critical')),
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    cooldown_minutes INTEGER DEFAULT 60, -- Prevent alert spam
    notification_channels TEXT[], -- Array of notification channels
    configuration JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create alerts table for triggered alerts
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_rule_id UUID NOT NULL REFERENCES alert_rules(id) ON DELETE CASCADE,
    test_run_id UUID REFERENCES test_runs(id) ON DELETE CASCADE,
    alert_status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (alert_status IN ('active', 'acknowledged', 'resolved', 'suppressed')),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    actual_value DECIMAL(10,3),
    threshold_value DECIMAL(10,3),
    environment VARCHAR(50),
    category VARCHAR(50),
    triggered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by VARCHAR(100),
    resolved_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create notification channels table
CREATE TABLE IF NOT EXISTS notification_channels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    channel_name VARCHAR(100) NOT NULL UNIQUE,
    channel_type VARCHAR(50) NOT NULL CHECK (channel_type IN ('email', 'slack', 'discord', 'webhook', 'sms')),
    configuration JSONB NOT NULL, -- Store channel-specific config (URLs, tokens, etc.)
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    test_mode BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create alert notifications log
CREATE TABLE IF NOT EXISTS alert_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_id UUID NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
    notification_channel_id UUID NOT NULL REFERENCES notification_channels(id) ON DELETE CASCADE,
    notification_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (notification_status IN ('pending', 'sent', 'failed', 'skipped')),
    sent_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    response_data JSONB,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for alerting tables
CREATE INDEX IF NOT EXISTS idx_alert_rules_enabled ON alert_rules(is_enabled);
CREATE INDEX IF NOT EXISTS idx_alert_rules_type ON alert_rules(rule_type);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(alert_status);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_triggered_at ON alerts(triggered_at);
CREATE INDEX IF NOT EXISTS idx_alerts_test_run ON alerts(test_run_id);
CREATE INDEX IF NOT EXISTS idx_notification_channels_enabled ON notification_channels(is_enabled);
CREATE INDEX IF NOT EXISTS idx_alert_notifications_status ON alert_notifications(notification_status);

-- Add triggers for updated_at columns
CREATE TRIGGER update_alert_rules_updated_at
    BEFORE UPDATE ON alert_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notification_channels_updated_at
    BEFORE UPDATE ON notification_channels
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to check and trigger alerts for a test run
CREATE OR REPLACE FUNCTION check_alerts_for_test_run(test_run_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
    alerts_triggered INTEGER := 0;
    rule_record RECORD;
    test_record RECORD;
    category_record RECORD;
    alert_uuid UUID;
    alert_title VARCHAR(200);
    alert_message TEXT;
BEGIN
    -- Get test run data
    SELECT * INTO test_record FROM test_runs WHERE id = test_run_uuid;
    
    IF NOT FOUND THEN
        RETURN 0;
    END IF;
    
    -- Check each enabled alert rule
    FOR rule_record IN 
        SELECT * FROM alert_rules 
        WHERE is_enabled = TRUE 
          AND (environment_filter IS NULL OR environment_filter = test_record.environment)
    LOOP
        -- Check different rule types
        CASE rule_record.rule_type
            WHEN 'pass_rate' THEN
                IF (rule_record.condition_operator = '<' AND test_record.overall_pass_rate < rule_record.threshold_value) OR
                   (rule_record.condition_operator = '<=' AND test_record.overall_pass_rate <= rule_record.threshold_value) OR
                   (rule_record.condition_operator = '>' AND test_record.overall_pass_rate > rule_record.threshold_value) OR
                   (rule_record.condition_operator = '>=' AND test_record.overall_pass_rate >= rule_record.threshold_value) OR
                   (rule_record.condition_operator = '=' AND test_record.overall_pass_rate = rule_record.threshold_value) OR
                   (rule_record.condition_operator = '!=' AND test_record.overall_pass_rate != rule_record.threshold_value)
                THEN
                    alert_title := 'Pass Rate Alert: ' || rule_record.rule_name;
                    alert_message := 'Overall pass rate of ' || test_record.overall_pass_rate || '% ' || 
                                   rule_record.condition_operator || ' threshold of ' || rule_record.threshold_value || '%';
                    
                    INSERT INTO alerts (alert_rule_id, test_run_id, severity, title, message, actual_value, threshold_value, environment)
                    VALUES (rule_record.id, test_run_uuid, rule_record.severity, alert_title, alert_message, 
                           test_record.overall_pass_rate, rule_record.threshold_value, test_record.environment)
                    RETURNING id INTO alert_uuid;
                    
                    alerts_triggered := alerts_triggered + 1;
                END IF;
                
            WHEN 'response_time' THEN
                IF (rule_record.condition_operator = '<' AND test_record.avg_response_time_ms < rule_record.threshold_value) OR
                   (rule_record.condition_operator = '<=' AND test_record.avg_response_time_ms <= rule_record.threshold_value) OR
                   (rule_record.condition_operator = '>' AND test_record.avg_response_time_ms > rule_record.threshold_value) OR
                   (rule_record.condition_operator = '>=' AND test_record.avg_response_time_ms >= rule_record.threshold_value)
                THEN
                    alert_title := 'Response Time Alert: ' || rule_record.rule_name;
                    alert_message := 'Average response time of ' || test_record.avg_response_time_ms || 'ms ' || 
                                   rule_record.condition_operator || ' threshold of ' || rule_record.threshold_value || 'ms';
                    
                    INSERT INTO alerts (alert_rule_id, test_run_id, severity, title, message, actual_value, threshold_value, environment)
                    VALUES (rule_record.id, test_run_uuid, rule_record.severity, alert_title, alert_message, 
                           test_record.avg_response_time_ms, rule_record.threshold_value, test_record.environment)
                    RETURNING id INTO alert_uuid;
                    
                    alerts_triggered := alerts_triggered + 1;
                END IF;
                
            WHEN 'goal_achievement' THEN
                IF (rule_record.condition_operator = '<' AND test_record.goal_achievement_rate < rule_record.threshold_value) OR
                   (rule_record.condition_operator = '<=' AND test_record.goal_achievement_rate <= rule_record.threshold_value) OR
                   (rule_record.condition_operator = '>' AND test_record.goal_achievement_rate > rule_record.threshold_value) OR
                   (rule_record.condition_operator = '>=' AND test_record.goal_achievement_rate >= rule_record.threshold_value)
                THEN
                    alert_title := 'Goal Achievement Alert: ' || rule_record.rule_name;
                    alert_message := 'Goal achievement rate of ' || test_record.goal_achievement_rate || '% ' || 
                                   rule_record.condition_operator || ' threshold of ' || rule_record.threshold_value || '%';
                    
                    INSERT INTO alerts (alert_rule_id, test_run_id, severity, title, message, actual_value, threshold_value, environment)
                    VALUES (rule_record.id, test_run_uuid, rule_record.severity, alert_title, alert_message, 
                           test_record.goal_achievement_rate, rule_record.threshold_value, test_record.environment)
                    RETURNING id INTO alert_uuid;
                    
                    alerts_triggered := alerts_triggered + 1;
                END IF;
                
            WHEN 'critical_failure' THEN
                -- Check for critical failures in test results
                IF EXISTS (SELECT 1 FROM test_failures WHERE test_run_id = test_run_uuid AND is_critical = TRUE) THEN
                    alert_title := 'Critical Failure Alert: ' || rule_record.rule_name;
                    alert_message := 'Critical test failures detected in test run';
                    
                    INSERT INTO alerts (alert_rule_id, test_run_id, severity, title, message, environment)
                    VALUES (rule_record.id, test_run_uuid, rule_record.severity, alert_title, alert_message, test_record.environment)
                    RETURNING id INTO alert_uuid;
                    
                    alerts_triggered := alerts_triggered + 1;
                END IF;
        END CASE;
    END LOOP;
    
    -- Check category-specific alerts
    FOR rule_record IN 
        SELECT * FROM alert_rules 
        WHERE is_enabled = TRUE 
          AND category_filter IS NOT NULL
          AND (environment_filter IS NULL OR environment_filter = test_record.environment)
    LOOP
        -- Get category performance data
        SELECT * INTO category_record FROM category_performance 
        WHERE test_run_id = test_run_uuid AND category_name = rule_record.category_filter;
        
        IF FOUND THEN
            CASE rule_record.rule_type
                WHEN 'pass_rate' THEN
                    IF (rule_record.condition_operator = '<' AND category_record.pass_rate < rule_record.threshold_value) OR
                       (rule_record.condition_operator = '<=' AND category_record.pass_rate <= rule_record.threshold_value) OR
                       (rule_record.condition_operator = '>' AND category_record.pass_rate > rule_record.threshold_value) OR
                       (rule_record.condition_operator = '>=' AND category_record.pass_rate >= rule_record.threshold_value)
                    THEN
                        alert_title := 'Category Alert: ' || rule_record.category_filter || ' - ' || rule_record.rule_name;
                        alert_message := 'Category ' || rule_record.category_filter || ' pass rate of ' || 
                                       category_record.pass_rate || '% ' || rule_record.condition_operator || 
                                       ' threshold of ' || rule_record.threshold_value || '%';
                        
                        INSERT INTO alerts (alert_rule_id, test_run_id, severity, title, message, actual_value, threshold_value, environment, category)
                        VALUES (rule_record.id, test_run_uuid, rule_record.severity, alert_title, alert_message, 
                               category_record.pass_rate, rule_record.threshold_value, test_record.environment, rule_record.category_filter)
                        RETURNING id INTO alert_uuid;
                        
                        alerts_triggered := alerts_triggered + 1;
                    END IF;
            END CASE;
        END IF;
    END LOOP;
    
    RETURN alerts_triggered;
END;
$$ LANGUAGE plpgsql;

-- Function to acknowledge an alert
CREATE OR REPLACE FUNCTION acknowledge_alert(alert_uuid UUID, acknowledged_by_user VARCHAR)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE alerts 
    SET alert_status = 'acknowledged',
        acknowledged_at = NOW(),
        acknowledged_by = acknowledged_by_user
    WHERE id = alert_uuid AND alert_status = 'active';
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Function to resolve an alert
CREATE OR REPLACE FUNCTION resolve_alert(alert_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE alerts 
    SET alert_status = 'resolved',
        resolved_at = NOW()
    WHERE id = alert_uuid AND alert_status IN ('active', 'acknowledged');
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Create view for active alerts
CREATE OR REPLACE VIEW active_alerts AS
SELECT 
    a.id,
    a.title,
    a.message,
    a.severity,
    a.actual_value,
    a.threshold_value,
    a.environment,
    a.category,
    a.triggered_at,
    ar.rule_name,
    ar.rule_type,
    tr.test_type,
    tr.started_at as test_started_at,
    EXTRACT(EPOCH FROM (NOW() - a.triggered_at))/60 as minutes_active
FROM alerts a
JOIN alert_rules ar ON a.alert_rule_id = ar.id
LEFT JOIN test_runs tr ON a.test_run_id = tr.id
WHERE a.alert_status = 'active'
ORDER BY a.severity DESC, a.triggered_at DESC;

-- Insert default alert rules
INSERT INTO alert_rules (rule_name, description, rule_type, condition_operator, threshold_value, severity, notification_channels) VALUES
('Critical Pass Rate Drop', 'Alert when overall pass rate drops below 70%', 'pass_rate', '<', 70.0, 'critical', ARRAY['default']),
('High Response Time', 'Alert when average response time exceeds 300ms', 'response_time', '>', 300.0, 'warning', ARRAY['default']),
('Goal Achievement Failure', 'Alert when goal achievement drops below 60%', 'goal_achievement', '<', 60.0, 'warning', ARRAY['default']),
('Critical Test Failures', 'Alert on any critical test failures', 'critical_failure', '>', 0, 'critical', ARRAY['default']),
('High Priority Detection Failure', 'Alert when high priority detection fails', 'pass_rate', '<', 100.0, 'critical', ARRAY['default'])
ON CONFLICT (rule_name) DO NOTHING;

-- Update the last alert rule to be category-specific
UPDATE alert_rules 
SET category_filter = 'definite_high'
WHERE rule_name = 'High Priority Detection Failure';

-- Insert default notification channel
INSERT INTO notification_channels (channel_name, channel_type, configuration) VALUES
('default', 'webhook', '{"url": "http://localhost:8884/webhook/alerts", "method": "POST"}')
ON CONFLICT (channel_name) DO NOTHING;

-- Create trigger to automatically check alerts after test completion
CREATE OR REPLACE FUNCTION trigger_alert_check()
RETURNS TRIGGER AS $$
BEGIN
    -- Only check alerts for completed tests
    IF NEW.test_status = 'completed' AND (OLD.test_status IS NULL OR OLD.test_status != 'completed') THEN
        PERFORM check_alerts_for_test_run(NEW.id);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER test_completion_alert_check
    AFTER UPDATE ON test_runs
    FOR EACH ROW
    EXECUTE FUNCTION trigger_alert_check();

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
    '{"migration": "002_add_alerting_system", "description": "Added comprehensive alerting and notification system"}'::jsonb
);

-- Log migration completion
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 002 completed successfully!';
    RAISE NOTICE '🚨 Added: comprehensive alerting system with rules, notifications, and channels';
    RAISE NOTICE '📊 New tables: alert_rules, alerts, notification_channels, alert_notifications';
    RAISE NOTICE '🔧 New functions: check_alerts_for_test_run, acknowledge_alert, resolve_alert';
    RAISE NOTICE '👁️ New views: active_alerts';
    RAISE NOTICE '⚠️ Default alert rules configured for critical scenarios';
END $$;