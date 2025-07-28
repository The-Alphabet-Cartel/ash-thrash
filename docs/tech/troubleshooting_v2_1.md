# Ash-Thrash Troubleshooting Guide v2.1

**Comprehensive problem diagnosis and resolution guide for the Ash-Thrash testing suite on dedicated server infrastructure.**

---

## 🎯 Quick Problem Identification

### Emergency Triage

**🚨 CRITICAL (Immediate Action Required):**
- Crisis detection system completely down
- Ash-Thrash cannot connect to NLP server
- Database corruption or data loss
- Security breach or unauthorized access

**⚠️ HIGH PRIORITY (Fix Within 2 Hours):**
- Test success rates below 80%
- API completely unresponsive
- Scheduled tests consistently failing
- Dashboard integration broken

**📋 MEDIUM PRIORITY (Fix Within 24 Hours):**
- Individual test failures
- Performance degradation
- Non-critical API endpoints failing
- Log storage issues

**🔧 LOW PRIORITY (Fix When Convenient):**
- Documentation inconsistencies
- Minor UI issues
- Non-essential monitoring alerts
- Optimization opportunities

### 30-Second Health Check

```bash
# Quick system verification
echo "=== Ash-Thrash Quick Health Check ==="

# 1. API Connectivity
echo -n "API Health: "
if curl -s http://localhost:8884/health | grep -q "healthy"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

# 2. NLP Server Connectivity  
echo -n "NLP Server: "
if curl -s http://10.20.30.253:8881/health | grep -q "healthy"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

# 3. Database Connectivity
echo -n "Database: "
if docker-compose exec -T ash-thrash-db pg_isready -U ash_user >/dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

# 4. Recent Test Results
echo -n "Recent Tests: "
if curl -s http://localhost:8884/api/test/results/latest | grep -q "success_rate"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

echo "=== End Health Check ==="
```

---

## 🔧 Common Issues & Solutions

### API and Connectivity Issues

**Problem: API Returns 503 Service Unavailable**

**Symptoms:**
- `curl http://localhost:8884/health` returns 503
- Dashboard shows "Service Unavailable"
- Tests cannot be executed

**Diagnosis:**
```bash
# Check if container is running
docker-compose ps ash-thrash

# Check container logs
docker-compose logs ash-thrash --tail=50

# Check port binding
sudo netstat -tulpn | grep 8884

# Check process inside container
docker-compose exec ash-thrash ps aux
```

**Solutions:**
```bash
# Solution 1: Restart service
docker-compose restart ash-thrash

# Solution 2: Check configuration
docker-compose exec ash-thrash cat .env | grep -E "(API_|NLP_)"

# Solution 3: Rebuild container
docker-compose down
docker-compose build --no-cache ash-thrash
docker-compose up -d

# Solution 4: Check resource limits
docker stats ash-thrash
```

**Problem: Cannot Connect to NLP Server**

**Symptoms:**
- Tests fail with "NLP_SERVER_UNAVAILABLE"
- Health check shows NLP server as unhealthy
- Error message: "Cannot connect to http://10.20.30.253:8881"

**Diagnosis:**
```bash
# Test network connectivity
ping 10.20.30.253

# Test port connectivity
nc -zv 10.20.30.253 8881

# Check from inside container
docker-compose exec ash-thrash curl -v http://10.20.30.253:8881/health

# Check firewall rules
sudo ufw status
sudo iptables -L | grep 8881
```

**Solutions:**
```bash
# Solution 1: Verify NLP server is running
ssh user@10.20.30.253 "docker ps | grep nlp"

# Solution 2: Check network configuration
docker network ls
docker network inspect ash_ash-network

# Solution 3: Update configuration
# Edit .env file and restart
sed -i 's/GLOBAL_NLP_API_URL=.*/GLOBAL_NLP_API_URL=http:\/\/10.20.30.253:8881/g' .env
docker-compose restart ash-thrash

# Solution 4: Test with different timeout
curl -m 10 http://10.20.30.253:8881/health
```

### Database Issues

**Problem: Database Connection Failures**

**Symptoms:**
- Error: "could not connect to database"
- Tests fail to save results
- API returns database-related errors

**Diagnosis:**
```bash
# Check database container
docker-compose ps ash-thrash-db

# Check database logs
docker-compose logs ash-thrash-db --tail=50

# Test connection manually
docker-compose exec ash-thrash-db psql -U ash_user -d ash_thrash_prod -c "SELECT 1;"

# Check connection pool
docker-compose exec ash-thrash python -c "
from src.database import get_connection_pool
pool = get_connection_pool()
print(f'Pool status: {pool.get_stats()}')
"
```

**Solutions:**
```bash
# Solution 1: Restart database
docker-compose restart ash-thrash-db

# Solution 2: Check disk space
df -h
docker system df

# Solution 3: Reset connection pool
docker-compose restart ash-thrash

# Solution 4: Check database integrity
docker-compose exec ash-thrash-db psql -U ash_user -d ash_thrash_prod -c "
SELECT schemaname, tablename, n_dead_tup, n_live_tup 
FROM pg_stat_user_tables 
ORDER BY n_dead_tup DESC;"
```

**Problem: Database Performance Issues**

**Symptoms:**
- Slow API responses
- Test execution times increased
- Database queries timing out

**Diagnosis:**
```bash
# Check active connections
docker-compose exec ash-thrash-db psql -U ash_user -d ash_thrash_prod -c "
SELECT count(*) as active_connections, state 
FROM pg_stat_activity 
WHERE datname = 'ash_thrash_prod' 
GROUP BY state;"

# Check slow queries
docker-compose exec ash-thrash-db psql -U ash_user -d ash_thrash_prod -c "
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;"

# Check database size
docker-compose exec ash-thrash-db psql -U ash_user -d ash_thrash_prod -c "
SELECT pg_size_pretty(pg_database_size('ash_thrash_prod'));"
```

**Solutions:**
```bash
# Solution 1: Optimize database
docker-compose exec ash-thrash-db psql -U ash_user -d ash_thrash_prod -c "VACUUM ANALYZE;"

# Solution 2: Update statistics
docker-compose exec ash-thrash-db psql -U ash_user -d ash_thrash_prod -c "ANALYZE;"

# Solution 3: Increase connection pool
# Edit .env file
sed -i 's/THRASH_DATABASE_POOL_SIZE=.*/THRASH_DATABASE_POOL_SIZE=20/g' .env
docker-compose restart ash-thrash

# Solution 4: Clean old data
curl -X POST http://localhost:8884/api/maintenance/cleanup \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"older_than_days": 60}'
```

### Test Execution Issues

**Problem: Tests Consistently Failing**

**Symptoms:**
- Success rates below expected targets
- Multiple categories showing poor performance
- Specific phrases consistently failing

**Diagnosis:**
```bash
# Get detailed failure analysis
curl -s http://localhost:8884/api/analytics/failures?period=7d | jq '.'

# Check recent test results
curl -s http://localhost:8884/api/test/results/latest | jq '.category_performance'

# Review specific failed phrases
curl -s "http://localhost:8884/api/test/results/latest?include_details=true" | \
  jq '.results[] | select(.success == false) | {phrase_text, expected_category, detected_category}'

# Check NLP server performance
curl -s http://10.20.30.253:8881/metrics | grep response_time
```

**Solutions:**
```bash
# Solution 1: Update test phrases
# Review and update problematic phrases
curl -X GET http://localhost:8884/api/admin/phrases?category=immediate_crisis \
  -H "X-API-Key: your-api-key"

# Solution 2: Retrain NLP model (if applicable)
# This requires coordination with NLP server team

# Solution 3: Adjust confidence thresholds
# Update configuration if using confidence-based filtering

# Solution 4: Validate phrase categorization
# Review phrases with community for proper categorization
```

**Problem: Tests Timing Out**

**Symptoms:**
- Tests never complete
- Status remains "running" indefinitely
- Timeout errors in logs

**Diagnosis:**
```bash
# Check current test status
curl -s http://localhost:8884/api/test/status | jq '.'

# Check for stuck processes
docker-compose exec ash-thrash ps aux | grep python

# Check resource usage
docker stats ash-thrash

# Check timeout configuration
docker-compose exec ash-thrash grep -r "timeout" src/
```

**Solutions:**
```bash
# Solution 1: Kill stuck test
# Find and terminate stuck process
docker-compose exec ash-thrash pkill -f "comprehensive_testing"

# Solution 2: Increase timeout values
# Edit configuration
sed -i 's/TEST_TIMEOUT=.*/TEST_TIMEOUT=900/g' .env
docker-compose restart ash-thrash

# Solution 3: Restart service
docker-compose restart ash-thrash

# Solution 4: Check NLP server load
curl -s http://10.20.30.253:8881/health | jq '.performance'
```

### Performance Issues

**Problem: Slow API Response Times**

**Symptoms:**
- API responses taking >5 seconds
- Dashboard loading slowly
- Test execution significantly slower

**Diagnosis:**
```bash
# Test API response times
time curl -s http://localhost:8884/health

# Check system resources
docker stats ash-thrash
htop

# Check database performance
docker-compose exec ash-thrash-db psql -U ash_user -d ash_thrash_prod -c "
SELECT query, mean_exec_time, calls, total_exec_time 
FROM pg_stat_statements 
ORDER BY total_exec_time DESC 
LIMIT 5;"

# Check Redis performance
docker-compose exec ash-thrash-redis redis-cli info stats
```

**Solutions:**
```bash
# Solution 1: Enable Redis caching
# Update .env configuration
sed -i 's/ENABLE_CACHING=.*/ENABLE_CACHING=true/g' .env
sed -i 's/CACHE_TTL=.*/CACHE_TTL=300/g' .env
docker-compose restart ash-thrash

# Solution 2: Optimize database
docker-compose exec ash-thrash-db psql -U ash_user -d ash_thrash_prod -c "
REINDEX DATABASE ash_thrash_prod;"

# Solution 3: Increase worker processes
sed -i 's/API_MAX_WORKERS=.*/API_MAX_WORKERS=8/g' .env
docker-compose restart ash-thrash

# Solution 4: Clean up old data
curl -X POST http://localhost:8884/api/maintenance/cleanup \
  -H "X-API-Key: your-api-key" \
  -d '{"older_than_days": 30}'
```

### Storage and Resource Issues

**Problem: Disk Space Issues**

**Symptoms:**
- "No space left on device" errors
- Cannot write test results
- Docker containers failing to start

**Diagnosis:**
```bash
# Check disk usage
df -h
docker system df

# Check result directory size
du -sh /opt/ash-thrash/results/

# Check Docker volumes
docker volume ls
docker volume inspect ash-thrash_ash_thrash_prod_data

# Check log file sizes
ls -lh /opt/ash-thrash/logs/
```

**Solutions:**
```bash
# Solution 1: Clean up old results
find /opt/ash-thrash/results/ -name "*.json" -mtime +90 -delete

# Solution 2: Docker system cleanup
docker system prune -a -f
docker volume prune -f

# Solution 3: Compress old logs
gzip /opt/ash-thrash/logs/*.log

# Solution 4: Move data to external storage
# Create backup and move to external storage
tar -czf /backup/ash-thrash-results-$(date +%Y%m%d).tar.gz /opt/ash-thrash/results/
rm -rf /opt/ash-thrash/results/old_data/
```

**Problem: Memory Issues**

**Symptoms:**
- Out of memory errors
- Container killed by system
- Slow performance during large tests

**Diagnosis:**
```bash
# Check memory usage
free -h
docker stats ash-thrash

# Check memory limits
docker inspect ash-thrash | jq '.[0].HostConfig.Memory'

# Check for memory leaks
docker-compose exec ash-thrash python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

**Solutions:**
```bash
# Solution 1: Increase memory limits
# Edit docker-compose.yml
cat >> docker-compose.override.yml << EOF
version: '3.8'
services:
  ash-thrash:
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G
EOF
docker-compose up -d

# Solution 2: Optimize application
# Reduce batch sizes in configuration
sed -i 's/BATCH_SIZE=.*/BATCH_SIZE=10/g' .env

# Solution 3: Add swap space (if needed)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Solution 4: Restart service
docker-compose restart ash-thrash
```

---

## 🔍 Diagnostic Tools & Scripts

### System Health Script

```bash
#!/bin/bash
# comprehensive_diagnostics.sh - Complete system diagnostic

echo "=== Ash-Thrash Comprehensive Diagnostics ==="
echo "Timestamp: $(date)"
echo

# System Information
echo "--- System Information ---"
uname -a
cat /etc/debian_version
lscpu | grep "Model name"
free -h
df -h /opt/ash-thrash

# Docker Status
echo
echo "--- Docker Status ---"
docker --version
docker-compose --version
docker-compose ps

# Service Health
echo
echo "--- Service Health ---"
echo -n "Ash-Thrash API: "
if curl -s --max-time 5 http://localhost:8884/health | grep -q "healthy"; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy"
fi

echo -n "NLP Server: "
if curl -s --max-time 5 http://10.20.30.253:8881/health | grep -q "healthy"; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy"
fi

echo -n "Database: "
if docker-compose exec -T ash-thrash-db pg_isready -U ash_user >/dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy"
fi

# Recent Test Performance
echo
echo "--- Recent Test Performance ---"
if command -v jq >/dev/null; then
    latest_result=$(curl -s http://localhost:8884/api/test/results/latest)
    if [ "$latest_result" != "null" ] && [ -n "$latest_result" ]; then
        echo "Latest test success rate: $(echo "$latest_result" | jq -r '.summary.success_rate')%"
        echo "Test completed: $(echo "$latest_result" | jq -r '.completed_at')"
        echo "Execution time: $(echo "$latest_result" | jq -r '.summary.execution_time_seconds')s"
    else
        echo "No recent test results available"
    fi
else
    echo "jq not installed - cannot parse JSON results"
fi

# Resource Usage
echo
echo "--- Resource Usage ---"
docker stats --no-stream ash-thrash ash-thrash-db ash-thrash-redis

# Log Analysis
echo
echo "--- Recent Error Log Analysis ---"
echo "Recent errors in container logs:"
docker-compose logs ash-thrash --since=1h 2>&1 | grep -i error | tail -5

echo
echo "=== End Diagnostics ==="
```

### Performance Monitoring Script

```bash
#!/bin/bash
# performance_monitor.sh - Monitor performance metrics

LOG_FILE="/opt/ash-thrash/logs/performance.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Function to log with timestamp
log_metric() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
}

# API Response Time
api_response_time=$(curl -w "%{time_total}" -s -o /dev/null http://localhost:8884/health)
log_metric "API_RESPONSE_TIME: ${api_response_time}s"

# Memory Usage
memory_usage=$(docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}" | grep ash-thrash | awk '{print $2}')
log_metric "MEMORY_USAGE: $memory_usage"

# CPU Usage
cpu_usage=$(docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}" | grep ash-thrash | awk '{print $2}')
log_metric "CPU_USAGE: $cpu_usage"

# Database Connection Count
db_connections=$(docker-compose exec -T ash-thrash-db psql -U ash_user -d ash_thrash_prod -t -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'ash_thrash_prod';" 2>/dev/null | xargs)
log_metric "DB_CONNECTIONS: $db_connections"

# NLP Server Response Time
nlp_response_time=$(curl -w "%{time_total}" -s -o /dev/null http://10.20.30.253:8881/health)
log_metric "NLP_RESPONSE_TIME: ${nlp_response_time}s"

# Disk Usage
disk_usage=$(df /opt/ash-thrash | awk 'NR==2 {print $5}')
log_metric "DISK_USAGE: $disk_usage"

# Test Success Rate (if available)
if command -v jq >/dev/null; then
    success_rate=$(curl -s http://localhost:8884/api/test/results/latest | jq -r '.summary.success_rate // "N/A"')
    log_metric "SUCCESS_RATE: ${success_rate}%"
fi
```

### Error Analysis Script

```bash
#!/bin/bash
# error_analysis.sh - Analyze and categorize errors

echo "=== Error Analysis Report ==="
echo "Generated: $(date)"
echo

# Container Errors
echo "--- Container Errors (Last 24 Hours) ---"
docker-compose logs ash-thrash --since=24h 2>&1 | \
  grep -i error | \
  sed 's/.*ash-thrash[^|]*|//g' | \
  sort | uniq -c | sort -nr | head -10

# Database Errors
echo
echo "--- Database Errors ---"
docker-compose logs ash-thrash-db --since=24h 2>&1 | \
  grep -i error | \
  tail -10

# API Error Rates
echo
echo "--- API Error Analysis ---"
if command -v jq >/dev/null; then
    # Get error metrics from API
    curl -s http://localhost:8884/api/diagnostics/performance | \
      jq '.api_performance | {error_rate_percent, slow_endpoints}'
else
    echo "jq not available - cannot analyze API metrics"
fi

# Failed Test Analysis
echo
echo "--- Failed Test Analysis ---"
curl -s http://localhost:8884/api/analytics/failures?period=7d | \
  jq '.common_failure_patterns[] | {pattern, frequency}' 2>/dev/null || \
  echo "Unable to retrieve failure analysis"

echo
echo "=== End Error Analysis ==="
```

---

## 🚨 Emergency Procedures

### Complete System Recovery

**When Everything is Broken:**

```bash
#!/bin/bash
# emergency_recovery.sh - Nuclear option for complete system recovery

echo "🚨 EMERGENCY RECOVERY PROCEDURE 🚨"
echo "This will stop all services and restore from backup"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Recovery cancelled"
    exit 1
fi

echo "=== Step 1: Stop All Services ==="
cd /opt/ash-thrash
docker-compose down -v

echo "=== Step 2: Backup Current State ==="
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
tar -czf "/tmp/ash-thrash-emergency-backup-$TIMESTAMP.tar.gz" \
  --exclude='logs/*' \
  --exclude='results/*/temp/*' \
  /opt/ash-thrash

echo "=== Step 3: System Cleanup ==="
docker system prune -a -f
docker volume prune -f

echo "=== Step 4: Fresh Clone from Repository ==="
cd /opt
mv ash-thrash "ash-thrash-broken-$TIMESTAMP"
git clone https://github.com/the-alphabet-cartel/ash-thrash.git
cd ash-thrash

echo "=== Step 5: Restore Configuration ==="
if [ -f "/opt/ash-thrash-broken-$TIMESTAMP/.env" ]; then
    cp "/opt/ash-thrash-broken-$TIMESTAMP/.env" .env
    echo "✅ Configuration restored"
else
    echo "⚠️ No configuration found - using template"
    cp .env.template .env
fi

echo "=== Step 6: Rebuild and Start Services ==="
docker-compose build --no-cache
docker-compose up -d

echo "=== Step 7: Wait for Services to Start ==="
sleep 60

echo "=== Step 8: Verify Recovery ==="
if curl -s http://localhost:8884/health | grep -q "healthy"; then
    echo "✅ Recovery successful - API responding"
else
    echo "❌ Recovery failed - API not responding"
    echo "Check logs: docker-compose logs ash-thrash"
    exit 1
fi

echo "=== Recovery Complete ==="
echo "Backup of broken system: /opt/ash-thrash-broken-$TIMESTAMP"
echo "Emergency backup: /tmp/ash-thrash-emergency-backup-$TIMESTAMP.tar.gz"
```

### Data Recovery

**When Database is Corrupted:**

```bash
#!/bin/bash
# database_recovery.sh - Recover from database corruption

echo "=== Database Recovery Procedure ==="

# Stop application
echo "Stopping Ash-Thrash application..."
docker-compose stop ash-thrash

# Create database backup
echo "Creating current database backup..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T ash-thrash-db pg_dump -U ash_user ash_thrash_prod > \
  "/opt/backups/emergency-db-backup-$TIMESTAMP.sql"

# Check for recent good backup
echo "Looking for recent good backup..."
LATEST_BACKUP=$(ls -t /opt/backups/ash-thrash/database_*.sql 2>/dev/null | head -1)

if [ -n "$LATEST_BACKUP" ]; then
    echo "Found backup: $LATEST_BACKUP"
    
    # Drop and recreate database
    echo "Recreating database..."
    docker-compose exec -T ash-thrash-db psql -U postgres -c "
    SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'ash_thrash_prod';
    DROP DATABASE IF EXISTS ash_thrash_prod;
    CREATE DATABASE ash_thrash_prod OWNER ash_user;
    "
    
    # Restore from backup
    echo "Restoring from backup..."
    docker-compose exec -T ash-thrash-db psql -U ash_user ash_thrash_prod < "$LATEST_BACKUP"
    
    echo "✅ Database restored from backup"
else
    echo "❌ No backup found - creating fresh database"
    
    # Recreate database with schema
    docker-compose exec -T ash-thrash-db psql -U postgres -c "
    DROP DATABASE IF EXISTS ash_thrash_prod;
    CREATE DATABASE ash_thrash_prod OWNER ash_user;
    "
    
    # Apply schema
    docker-compose exec -T ash-thrash-db psql -U ash_user ash_thrash_prod < \
      /opt/ash-thrash/database/init/01-init-database.sql
    
    echo "✅ Fresh database created"
fi

# Restart application
echo "Restarting Ash-Thrash application..."
docker-compose start ash-thrash

# Verify recovery
sleep 30
if curl -s http://localhost:8884/health | grep -q "healthy"; then
    echo "✅ Database recovery successful"
else
    echo "❌ Database recovery failed"
    exit 1
fi
```

### Network Connectivity Recovery

**When NLP Server is Unreachable:**

```bash
#!/bin/bash
# network_recovery.sh - Diagnose and fix network connectivity

echo "=== Network Connectivity Recovery ==="

NLP_SERVER="10.20.30.253"
NLP_PORT="8881"

echo "Step 1: Basic Connectivity Test"
if ping -c 3 "$NLP_SERVER" >/dev/null; then
    echo "✅ Server reachable via ping"
else
    echo "❌ Server not reachable via ping"
    echo "Check physical network connectivity"
    exit 1
fi

echo "Step 2: Port Connectivity Test"
if nc -zv "$NLP_SERVER" "$NLP_PORT" 2>/dev/null; then
    echo "✅ Port $NLP_PORT is accessible"
else
    echo "❌ Port $NLP_PORT is not accessible"
    echo "Checking firewall rules..."
    
    # Check local firewall
    sudo ufw status | grep "$NLP_PORT"
    
    # Test from inside container
    docker-compose exec ash-thrash nc -zv "$NLP_SERVER" "$NLP_PORT"
    
    exit 1
fi

echo "Step 3: HTTP Service Test"
if curl -s --max-time 10 "http://$NLP_SERVER:$NLP_PORT/health" | grep -q "healthy"; then
    echo "✅ NLP service responding normally"
else
    echo "❌ NLP service not responding correctly"
    echo "Service may be down or overloaded"
    
    # Try to get more information
    echo "Service response:"
    curl -v --max-time 10 "http://$NLP_SERVER:$NLP_PORT/health" 2>&1 | head -20
    exit 1
fi

echo "Step 4: Configuration Verification"
echo "Current NLP configuration:"
docker-compose exec ash-thrash grep NLP .env

echo "Step 5: Container Network Test"
echo "Testing from inside Ash-Thrash container:"
docker-compose exec ash-thrash curl -s --max-time 5 "http://$NLP_SERVER:$NLP_PORT/health"

echo "✅ Network connectivity verified"
```

---

## 📞 Support and Escalation

### Support Matrix

**Level 1: Self-Service (0-30 minutes)**
- Use this troubleshooting guide
- Check recent GitHub issues
- Review Discord #tech-support channel
- Run diagnostic scripts

**Level 2: Community Support (30-60 minutes)**
- Post in Discord #tech-support with diagnostic output
- Create GitHub issue with logs and symptoms
- Tag technical team members in Discord

**Level 3: Direct Technical Support (1-2 hours)**
- Direct message Technical Lead with urgency level
- Include all diagnostic information
- Provide timeline of when issue started

**Level 4: Emergency Escalation (Critical Issues)**
- Crisis detection system completely down
- Security incidents or breaches
- Data loss or corruption
- Contact emergency contacts immediately

### Information to Gather Before Escalating

**System Information:**
```bash
# Gather this information before contacting support
echo "=== Support Information Package ===" > support_info.txt
echo "Timestamp: $(date)" >> support_info.txt
echo "Issue Description: [DESCRIBE YOUR ISSUE HERE]" >> support_info.txt
echo >> support_info.txt

echo "--- System Info ---" >> support_info.txt
uname -a >> support_info.txt
docker --version >> support_info.txt
docker-compose --version >> support_info.txt

echo "--- Service Status ---" >> support_info.txt
docker-compose ps >> support_info.txt

echo "--- Recent Logs ---" >> support_info.txt
docker-compose logs ash-thrash --tail=50 >> support_info.txt

echo "--- Health Check ---" >> support_info.txt
curl -s http://localhost:8884/health >> support_info.txt 2>&1

echo "--- Configuration ---" >> support_info.txt
docker-compose exec ash-thrash env | grep -E "(NLP_|API_|DATABASE_)" >> support_info.txt

echo "Package created: support_info.txt"
```

### Emergency Contact Procedures

**For Critical Issues:**
1. **Discord:** Post in #crisis-response with @everyone
2. **Email:** emergency@alphabetcartel.org
3. **GitHub:** Create issue with "CRITICAL" label
4. **Direct Contact:** Message Technical Lead directly

**Escalation Checklist:**
- [ ] Attempted self-service troubleshooting
- [ ] Gathered diagnostic information
- [ ] Documented timeline of issue
- [ ] Identified business impact
- [ ] Attempted workaround solutions

**Support Ticket Template:**
```
PRIORITY: [Critical/High/Medium/Low]
COMPONENT: Ash-Thrash Testing Suite
ENVIRONMENT: Production (10.20.30.253)

ISSUE SUMMARY:
[Brief description of the problem]

SYMPTOMS:
- [What you're seeing]
- [Error messages]
- [Affected functionality]

TIMELINE:
- [When issue started]
- [What changed recently]
- [When last working normally]

IMPACT:
- [Effect on crisis detection]
- [Effect on team operations]
- [Workarounds in place]

DIAGNOSTIC INFO:
[Attach output from diagnostic scripts]

ATTEMPTED SOLUTIONS:
- [What you've tried]
- [Results of attempts]
```

---

## 🔧 Prevention and Maintenance

### Proactive Monitoring

**Daily Health Checks:**
```bash
# Add to crontab: 0 */6 * * *
/opt/ash-thrash/scripts/health_monitor.sh
```

**Weekly Performance Review:**
```bash
# Add to crontab: 0 8 * * 1
/opt/ash-thrash/scripts/weekly_performance_report.sh
```

**Monthly Maintenance:**
```bash
# Add to crontab: 0 2 1 * *
/opt/ash-thrash/scripts/monthly_maintenance.sh
```

### Best Practices

**Configuration Management:**
- Always backup .env before changes
- Use version control for configuration changes
- Test configuration changes in staging first
- Document all configuration modifications

**Database Maintenance:**
- Regular database backups (automated)
- Monitor database size and growth
- Perform VACUUM and ANALYZE regularly
- Monitor for long-running queries

**Resource Management:**
- Monitor disk space usage
- Set up alerts for resource thresholds
- Regular cleanup of old test results
- Monitor memory usage trends

**Security Practices:**
- Regular security updates
- Monitor access logs
- Rotate API keys periodically
- Audit user permissions

---

**Built with 🖤 for chosen family everywhere.**

This troubleshooting guide ensures that when things go wrong, we can quickly diagnose and resolve issues to maintain the reliability of our crisis detection testing system. Remember that the ultimate goal is keeping our community safe and supported.

**The Alphabet Cartel** - Building inclusive gaming communities through technology.

**Discord:** https://discord.gg/alphabetcartel | **Website:** https://alphabetcartel.org | **GitHub:** https://github.com/the-alphabet-cartel

---

**Document Version:** 2.1  
**Last Updated:** July 27, 2025  
**Next Review:** August 27, 2025  
**Support:** #tech-support in Discord