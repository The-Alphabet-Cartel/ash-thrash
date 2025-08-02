# Ash-Thrash v3.0 Troubleshooting Guide

**Repository**: https://github.com/the-alphabet-cartel/ash-thrash  
**Troubleshooting Guide**: Problem Resolution for v3.0  
**Document Location**: `docs/troubleshooting_v3_0.md`  
**Last Updated**: August 2025

---

## 🚨 Emergency Quick Fixes

### **Critical Issues (Production Down)**

#### **API Server Not Responding**
```bash
# 1. Quick restart persistent containers
docker compose restart ash-thrash-api

# 2. Check if services are running
docker compose ps

# 3. If still failing, force restart all
docker compose down
docker compose up -d

# 4. Verify services are healthy
docker compose exec ash-thrash python cli.py api health
```

#### **All Tests Failing (NLP Server Issue)**
```bash
# 1. Test NLP connectivity from container
docker compose exec ash-thrash curl http://10.20.30.253:8881/health

# 2. If NLP down, restart ash-nlp service
# (In ash-nlp directory)
docker compose restart ash-nlp

# 3. Verify connectivity restored from ash-thrash container
docker compose exec ash-thrash python cli.py api health
```

#### **False Negatives (Missing Crisis Detection)**
```bash
# 1. Emergency threshold lowering
# Edit ash-nlp/.env:
# NLP_HIGH_CRISIS_THRESHOLD=0.6  # Lower from 0.8

# 2. Restart NLP service
# (In ash-nlp directory)
docker compose restart ash-nlp

# 3. Immediate validation using persistent container
docker compose exec ash-thrash python cli.py test category definite_high
```

#### **Containers Won't Stay Running**
```bash
# 1. Check container status and exit codes
docker compose ps
docker compose logs ash-thrash
docker compose logs ash-thrash-api

# 2. Force clean restart
docker compose down -v
docker compose up -d

# 3. Check for resource constraints
docker stats
free -h
```

---

## 🔍 Diagnostic Tools

### **System Health Check**
```bash
# Complete system validation using persistent containers
docker compose up -d
docker compose exec ash-thrash python cli.py validate setup

# API health check from container
docker compose exec ash-thrash python cli.py api health

# Service status
docker compose ps

# Test data validation from container
docker compose exec ash-thrash python cli.py validate data
```

### **Network Connectivity Tests**
```bash
# Test NLP server connectivity from ash-thrash container
docker compose exec ash-thrash curl -I http://10.20.30.253:8881/health

# Test API server from external
curl -I http://localhost:8884/health

# Check port availability
netstat -tulpn | grep -E "(8881|8884)"

# Test connectivity from within container network
docker compose exec ash-thrash ping ash-nlp
docker compose exec ash-thrash ping 10.20.30.253
```

### **Docker Diagnostics**
```bash
# Container status
docker compose ps

# Service logs for persistent containers
docker compose logs ash-thrash-api
docker compose logs ash-thrash
docker compose logs -f  # Follow all logs

# Resource usage for running containers
docker stats ash-thrash-api ash-thrash

# Network connectivity between containers
docker compose exec ash-thrash ping ash-thrash-api
docker compose exec ash-thrash-api ping ash-nlp

# Container health inspection
docker inspect ash-thrash-api | jq '.[0].State.Health'
```

---

## 🛠️ Common Issues & Solutions

### **Installation & Setup Issues**

#### **Issue: `docker compose up -d` Fails**

**Symptoms:**
- Containers exit immediately
- Port binding errors
- Missing dependencies

**Diagnosis:**
```bash
# Check Docker daemon
docker version

# Check if ports are available
sudo netstat -tulpn | grep -E "(8884|8881)"

# View container startup logs
docker compose logs
```

**Solutions:**
```bash
# Stop conflicting services
sudo lsof -ti:8884 | xargs kill -9

# Clean up Docker resources
docker system prune -f

# Rebuild containers
docker compose down
docker compose build
docker compose up -d

# Check Docker Compose syntax
docker compose config

# Increase Docker resources (Docker Desktop)
# Settings > Resources > Memory > 4GB+
```

#### **Issue: `.env` File Not Created**

**Symptoms:**
- "Environment file not found" errors
- Default configuration being used
- Containers fail to start

**Solutions:**
```bash
# Manual .env creation
cp .env.template .env

# Edit with your settings
nano .env  # or vim, code, etc.

# Verify contents
cat .env | grep -v '^#'

# Restart containers with new config
docker compose down
docker compose up -d
```

### **Container Lifecycle Issues**

#### **Issue: Containers Keep Restarting**

**Symptoms:**
- Containers in restart loop
- Exit code 1 or 125
- Services marked as unhealthy

**Diagnosis:**
```bash
# Check container exit reasons
docker compose ps
docker compose logs ash-thrash
docker compose logs ash-thrash-api

# Check resource constraints
docker stats
free -h
df -h
```

**Solutions:**
```bash
# Increase container memory limits
# Edit docker-compose.yml:
# deploy:
#   resources:
#     limits:
#       memory: 4G  # Increase from 2G

# Fix file permissions
chmod 777 results logs reports

# Check for dependency issues
docker compose exec ash-thrash python cli.py validate setup

# Restart with clean state
docker compose down -v
docker compose up -d
```

#### **Issue: Cannot Execute Commands in Containers**

**Symptoms:**
- `docker compose exec` commands fail
- "Container not found" errors
- "Container not running" errors

**Diagnosis:**
```bash
# Check if containers are running
docker compose ps

# Check container health
docker compose exec ash-thrash echo "Container is accessible"

# Verify service names
docker compose config --services
```

**Solutions:**
```bash
# Ensure containers are running
docker compose up -d

# Wait for containers to be ready
sleep 10
docker compose ps

# Use correct service names
docker compose exec ash-thrash python cli.py validate setup
docker compose exec ash-thrash-api curl http://localhost:8884/health

# Check container logs for startup issues
docker compose logs ash-thrash
```

### **API & Testing Issues**

#### **Issue: API Server Returns 500 Errors**

**Symptoms:**
- Internal server errors
- API endpoints not responding
- FastAPI error traces

**Diagnosis:**
```bash
# Check API logs from persistent container
docker compose logs ash-thrash-api

# Test API endpoints manually
curl -v http://localhost:8884/health

# Check Python imports in container
docker compose exec ash-thrash-api python -c "from src.ash_thrash_core import AshThrashTester"
```

**Solutions:**
```bash
# Restart API service
docker compose restart ash-thrash-api

# Check environment variables in container
docker compose exec ash-thrash-api env | grep -E "(GLOBAL_|THRASH_)"

# Validate Python dependencies in container
docker compose exec ash-thrash-api pip list

# Check for code syntax errors
docker compose exec ash-thrash python -m py_compile src/ash_thrash_api.py
```

#### **Issue: Tests Always Fail**

**Symptoms:**
- All test phrases marked as failed
- 0% pass rates across all categories
- NLP server communication errors

**Diagnosis:**
```bash
# Test NLP server directly from container
docker compose exec ash-thrash curl -X POST http://10.20.30.253:8881/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "test message", "user_id": "test", "channel_id": "test"}'

# Check network routing from container
docker compose exec ash-thrash ping 10.20.30.253

# Verify DNS resolution in container
docker compose exec ash-thrash nslookup 10.20.30.253
```

**Solutions:**
```bash
# Update NLP server URL
# Edit .env:
# GLOBAL_NLP_API_URL=http://correct-nlp-server:8881

# Restart services with new config
docker compose down
docker compose up -d

# Test with different URL from container
docker compose exec ash-thrash python cli.py api health

# Check firewall settings
sudo ufw status
```

#### **Issue: Tests Take Too Long or Timeout**

**Symptoms:**
- Tests timeout before completion
- Very slow response times (>5 minutes)
- API timeout errors

**Diagnosis:**
```bash
# Check NLP server performance from container
docker compose exec ash-thrash bash -c "time curl http://10.20.30.253:8881/health"

# Monitor system resources during tests
docker stats ash-thrash ash-thrash-api

# Test single phrase from container
docker compose exec ash-thrash python cli.py test category definite_high --sample-size 1
```

**Solutions:**
```bash
# Reduce concurrent tests
# Edit .env:
# THRASH_MAX_CONCURRENT_TESTS=1

# Increase timeouts
# Edit .env:
# THRASH_REQUEST_TIMEOUT=60

# Use quick test mode from container
docker compose exec ash-thrash python cli.py test quick --sample-size 10

# Scale down other services temporarily
docker compose stop ash-dash  # If running
```

### **Integration Issues**

#### **Issue: Discord Webhooks Not Working**

**Symptoms:**
- No Discord notifications
- Webhook errors in logs
- 404 webhook responses

**Diagnosis:**
```bash
# Test webhook manually from container
docker compose exec ash-thrash-api curl -X POST "$THRASH_DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test message"}'

# Check webhook URL format in container
docker compose exec ash-thrash-api printenv THRASH_DISCORD_WEBHOOK_URL

# View webhook logs
docker compose logs ash-thrash-api | grep webhook
```

**Solutions:**
```bash
# Verify webhook URL format
# Should be: https://discord.com/api/webhooks/ID/TOKEN

# Update environment variable
# Edit .env:
# THRASH_DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Test webhook permissions
# Verify bot has "Manage Webhooks" permission in Discord

# Restart API with new webhook
docker compose restart ash-thrash-api
```

#### **Issue: Ash-Dash Integration Broken**

**Symptoms:**
- Dashboard shows no test data
- API endpoints not accessible from dashboard
- CORS errors in browser

**Diagnosis:**
```bash
# Test API from dashboard server
curl http://10.20.30.253:8884/api/test/latest

# Check CORS configuration from container
docker compose exec ash-thrash curl -H "Origin: http://dashboard-url" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -X OPTIONS http://localhost:8884/api/test/latest
```

**Solutions:**
```bash
# Enable CORS for dashboard
# Edit .env:
# THRASH_ENABLE_CORS=true
# THRASH_CORS_ORIGINS=http://dashboard-url,https://ashdash.alphabetcartel.net

# Restart API service
docker compose restart ash-thrash-api

# Verify dashboard configuration
# Check ash-dash .env for correct API URL:
# THRASH_API_URL=http://10.20.30.253:8884
```

---

## 🐛 Debugging Techniques

### **Verbose Logging for Persistent Containers**

#### **Enable Debug Logging**
```bash
# Edit .env
GLOBAL_LOG_LEVEL=DEBUG
THRASH_ENABLE_DEBUG_LOGGING=true

# Restart services
docker compose down
docker compose up -d

# View debug logs
docker compose logs -f
```

#### **Container-Based Debugging**
```bash
# Add debug prints and test immediately
docker compose exec ash-thrash python -c "
import asyncio
from src.ash_thrash_core import NLPClient

async def test_nlp():
    async with NLPClient('http://10.20.30.253:8881') as client:
        result = await client.analyze_message('I want to die')
        print(result)

asyncio.run(test_nlp())
"
```

### **Manual Testing with Persistent Containers**

#### **Test Individual Components**
```bash
# Test NLP integration directly from container
docker compose exec ash-thrash python -c "
import asyncio
from src.ash_thrash_core import AshThrashTester

async def test_phrase():
    tester = AshThrashTester()
    # Test will run automatically

asyncio.run(test_phrase())
"

# Test single phrase from container
docker compose exec ash-thrash python cli.py test phrase 'test phrase' --debug
```

#### **API Endpoint Testing from Containers**
```bash
# Test each endpoint from API container
docker compose exec ash-thrash-api curl http://localhost:8884/
docker compose exec ash-thrash-api curl http://localhost:8884/health
docker compose exec ash-thrash-api curl http://localhost:8884/api/test/data

# Test with verbose output from container
docker compose exec ash-thrash curl -v -X POST http://ash-thrash-api:8884/api/test/trigger \
  -H "Content-Type: application/json" \
  -d '{"test_type": "quick"}'
```

### **Performance Debugging with Persistent Containers**

#### **Monitor Resource Usage During Tests**
```bash
# Terminal 1: Start test from container
docker compose exec ash-thrash python cli.py test comprehensive

# Terminal 2: Monitor resources
watch -n 1 'docker stats --no-stream ash-thrash ash-thrash-api'

# Monitor network activity from container
docker compose exec ash-thrash netstat -i

# Monitor container logs in real-time
docker compose logs -f ash-thrash
```

---

## 📊 Performance Issues

### **Slow Test Execution with Persistent Containers**

#### **Symptoms:**
- Tests take >5 minutes for comprehensive
- API timeouts
- High CPU/memory usage

#### **Diagnosis:**
```bash
# Check system resources
free -h
df -h
docker stats ash-thrash ash-thrash-api

# Monitor network latency from container
docker compose exec ash-thrash ping 10.20.30.253

# Check NLP server performance from container
docker compose exec ash-thrash bash -c "time curl http://10.20.30.253:8881/health"

# Profile single test from container
docker compose exec ash-thrash bash -c "time python cli.py test category definite_high"
```

#### **Solutions:**
```bash
# Reduce concurrent tests
# Edit .env:
THRASH_MAX_CONCURRENT_TESTS=1

# Increase timeouts
THRASH_REQUEST_TIMEOUT=60
NLP_SERVER_TIMEOUT=45

# Use smaller test sets from container
docker compose exec ash-thrash python cli.py test quick --sample-size 10

# Check for resource constraints
# Increase Docker memory limits in docker-compose.yml
```

### **High Memory Usage with Persistent Containers**

#### **Symptoms:**
- Out of memory errors
- Container restarts
- System slowdown

#### **Diagnosis:**
```bash
# Check container memory usage
docker stats --no-stream ash-thrash ash-thrash-api

# Check system memory
free -h

# Monitor memory during tests
watch -n 1 'free -h && docker stats --no-stream'
```

#### **Solutions:**
```bash
# Increase Docker memory limits
# Edit docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 4G  # Increase from 2G

# Reduce concurrent operations
THRASH_MAX_CONCURRENT_TESTS=1

# Clear Docker cache
docker system prune -f

# Restart with more memory
docker compose down
docker compose up -d
```

---

## 🔐 Security Issues

### **Permission Problems with Persistent Containers**

#### **Issue: File Permission Errors**

**Symptoms:**
- "Permission denied" errors
- Cannot write to results directory
- Docker mount issues

**Solutions:**
```bash
# Fix directory permissions for container access
mkdir -p results logs reports
chmod 777 results logs reports  # For Docker

# Fix ownership if needed
sudo chown -R $USER:$USER .

# Test file access from container
docker compose exec ash-thrash touch /app/results/test_file
docker compose exec ash-thrash ls -la /app/results/
```

#### **Issue: Network Security Blocking**

**Symptoms:**
- Connection refused errors from container
- Timeout connecting to NLP server
- Firewall blocks

**Solutions:**
```bash
# Check firewall status
sudo ufw status

# Allow required ports
sudo ufw allow 8884
sudo ufw allow from 10.20.30.0/24

# Test with firewall disabled (temporarily) from container
sudo ufw disable
docker compose exec ash-thrash python cli.py api health
sudo ufw enable
```

---

## 🚨 Emergency Procedures for Persistent Containers

### **Production Emergency Response**

#### **Crisis Detection Failure**
1. **Immediate Action**: Lower detection thresholds
2. **Validation**: Run emergency high-crisis test from container
3. **Communication**: Alert team via Discord
4. **Monitoring**: Watch for continued issues
5. **Documentation**: Log incident details

```bash
# Emergency threshold adjustment
# Edit ash-nlp/.env:
NLP_HIGH_CRISIS_THRESHOLD=0.5  # Emergency low threshold

# Restart NLP service
docker compose restart ash-nlp

# Emergency validation from persistent container
docker compose exec ash-thrash python cli.py test category definite_high

# If still failing, manual review required
```

#### **System-Wide Failure**
1. **Assessment**: Determine scope of failure
2. **Isolation**: Identify failed components
3. **Recovery**: Restart services in order
4. **Validation**: Run comprehensive tests
5. **Monitoring**: Extended observation period

```bash
# Complete system restart
docker compose down
docker system prune -f
docker compose up -d

# Wait for services to stabilize
sleep 30

# Full system validation from container
docker compose exec ash-thrash python cli.py validate setup
docker compose exec ash-thrash python cli.py test comprehensive
```

### **Data Recovery for Persistent Containers**

#### **Lost Test Results**
```bash
# Check backup locations from container
docker compose exec ash-thrash ls -la /app/results/
docker compose exec ash-thrash ls -la /app/logs/

# Recover from Docker volumes
docker volume ls
docker run --rm -v ash-thrash_results:/backup alpine tar czf - /backup

# Copy results from container to host
docker compose cp ash-thrash:/app/results ./backup_results
```

#### **Configuration Recovery**
```bash
# Restore from template
cp .env.template .env

# Restore from git
git checkout HEAD -- .env.template

# Restart containers with restored config
docker compose down
docker compose up -d
```

---

## 📞 Getting Help

### **Support Escalation Path**

#### **Level 1: Self-Service**
- Check this troubleshooting guide
- Review container logs: `docker compose logs`
- Verify configuration: `docker compose exec ash-thrash python cli.py validate setup`
- Search GitHub Issues: https://github.com/the-alphabet-cartel/ash-thrash/issues

#### **Level 2: Community Support**
- Discord #ash-development channel
- GitHub Issues (create new issue)
- Team guide documentation

#### **Level 3: Emergency Escalation**
- Direct message team leads
- Emergency Discord channels
- Crisis team notification for safety issues

### **Information to Include When Asking for Help**

#### **System Information for Persistent Containers**
```bash
# Collect diagnostic information
echo "=== System Info ===" > debug_info.txt
uname -a >> debug_info.txt
docker version >> debug_info.txt
docker compose version >> debug_info.txt
python --version >> debug_info.txt

echo "=== Container Status ===" >> debug_info.txt
docker compose ps >> debug_info.txt

echo "=== Health Check ===" >> debug_info.txt
docker compose exec ash-thrash python cli.py api health >> debug_info.txt 2>&1

echo "=== Recent Logs ===" >> debug_info.txt
docker compose logs --tail 50 >> debug_info.txt 2>&1

echo "=== Environment ===" >> debug_info.txt
cat .env | grep -v '^#' >> debug_info.txt
```

#### **Error Reproduction**
- Exact command that failed (including `docker compose exec`)
- Complete error message
- Steps to reproduce with persistent containers
- Expected vs actual behavior
- Recent changes made

### **Common Support Questions**

#### **"Everything was working yesterday, now it's broken"**
- Check if ash-nlp server is running: `docker compose exec ash-thrash curl http://10.20.30.253:8881/health`
- Verify network connectivity from containers
- Review recent configuration changes
- Check Docker container status: `docker compose ps`

#### **"Tests are failing but NLP server seems fine"**
- Validate test data structure: `docker compose exec ash-thrash python cli.py validate data`
- Check environment variables in containers
- Review NLP server response format
- Test individual phrases manually from container

#### **"Performance is much slower than expected"**
- Check system resources: `docker stats`
- Monitor network latency from container
- Review concurrent test settings
- Verify NLP server performance from container

---

## 🔧 Advanced Troubleshooting with Persistent Containers

### **Custom Debugging Scripts**

#### **Network Connectivity Test for Containers**
```python
#!/usr/bin/env python3
# Save as debug_connectivity.py and run: docker compose exec ash-thrash python debug_connectivity.py
import requests
import time

def test_connectivity():
    nlp_url = "http://10.20.30.253:8881"
    api_url = "http://ash-thrash-api:8884"
    
    print("Testing NLP Server from container...")
    try:
        response = requests.get(f"{nlp_url}/health", timeout=5)
        print(f"✅ NLP Server: {response.status_code}")
    except Exception as e:
        print(f"❌ NLP Server: {e}")
    
    print("Testing API Server from container...")
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        print(f"✅ API Server: {response.status_code}")
    except Exception as e:
        print(f"❌ API Server: {e}")

if __name__ == "__main__":
    test_connectivity()
```

### **Log Analysis Tools for Persistent Containers**

#### **Error Pattern Detection**
```bash
# Find common error patterns in persistent container logs
docker compose logs ash-thrash | grep -i error | sort | uniq -c | sort -nr

# Check for specific issues
docker compose logs ash-thrash | grep -i "nlp.*unreachable"
docker compose logs ash-thrash | grep -i "timeout"
docker compose logs ash-thrash-api | grep -i "failed.*test"

# Analyze timing patterns
docker compose logs ash-thrash | grep -E "\d{4}-\d{2}-\d{2}.*ERROR" | \
  awk '{print $1, $2}' | sort | uniq -c
```

---

**This troubleshooting guide covers the most common issues encountered with Ash-Thrash v3.0 persistent container deployment. For issues not covered here, please create a GitHub issue with detailed diagnostic information.**

**Emergency Contact**: [Discord #ash-development](https://discord.gg/alphabetcartel)  
**Repository**: [https://github.com/the-alphabet-cartel/ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash)  
**Documentation**: [Complete documentation suite](../README.md)

*Keeping crisis detection systems running smoothly for safer communities.* 🛠️🔍