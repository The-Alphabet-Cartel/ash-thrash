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
# 1. Quick restart
python main.py stop
python main.py start

# 2. Check if services are running
python main.py status

# 3. If still failing, force restart
docker-compose down -v
docker-compose up -d
```

#### **All Tests Failing (NLP Server Issue)**
```bash
# 1. Test NLP connectivity directly
curl http://10.20.30.253:8881/health

# 2. If NLP down, restart ash-nlp service
# (In ash-nlp directory)
docker-compose restart ash-nlp

# 3. Verify connectivity restored
python cli.py api health
```

#### **False Negatives (Missing Crisis Detection)**
```bash
# 1. Emergency threshold lowering
# Edit ash-nlp/.env:
# NLP_HIGH_CRISIS_THRESHOLD=0.6  # Lower from 0.8

# 2. Restart NLP service
# (In ash-nlp directory)
docker-compose restart ash-nlp

# 3. Immediate validation
python cli.py test category definite_high
```

---

## 🔍 Diagnostic Tools

### **System Health Check**
```bash
# Complete system validation
python cli.py validate setup

# API health check
python cli.py api health

# Service status
python main.py status

# Test data validation
python cli.py validate data
```

### **Network Connectivity Tests**
```bash
# Test NLP server connectivity
curl -I http://10.20.30.253:8881/health

# Test API server
curl -I http://localhost:8884/health

# Check port availability
netstat -tulpn | grep -E "(8881|8884)"

# DNS resolution test
nslookup 10.20.30.253
```

### **Docker Diagnostics**
```bash
# Container status
docker-compose ps

# Service logs
python main.py logs --follow ash-thrash-api

# Resource usage
docker stats ash-thrash-api

# Network connectivity
docker exec ash-thrash-api ping 10.20.30.253

# Container health
docker inspect ash-thrash-api | jq '.[0].State.Health'
```

---

## 🛠️ Common Issues & Solutions

### **Installation & Setup Issues**

#### **Issue: `python main.py setup` Fails**

**Symptoms:**
- Command not found errors
- Permission denied
- Missing dependencies

**Diagnosis:**
```bash
# Check Python version
python --version

# Check if in correct directory
pwd
ls -la main.py

# Check file permissions
ls -la main.py cli.py
```

**Solutions:**
```bash
# Fix permissions
chmod +x main.py cli.py

# Install dependencies
pip install -r requirements.txt

# Use Python 3 explicitly
python3 main.py setup

# Virtual environment (if needed)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### **Issue: `.env` File Not Created**

**Symptoms:**
- "Environment file not found" errors
- Default configuration being used

**Solutions:**
```bash
# Manual .env creation
cp .env.template .env

# Edit with your settings
nano .env  # or vim, code, etc.

# Verify contents
cat .env | grep -v '^#'

# Export variables
export $(cat .env | grep -v '^#' | xargs)
```

### **Docker & Container Issues**

#### **Issue: Containers Won't Start**

**Symptoms:**
- `docker-compose up` fails
- Container exits immediately
- Port binding errors

**Diagnosis:**
```bash
# Check Docker daemon
docker version

# Check port conflicts
sudo netstat -tulpn | grep 8884

# View container logs
docker-compose logs ash-thrash-api

# Check resource usage
docker system df
free -h
```

**Solutions:**
```bash
# Stop conflicting services
sudo lsof -ti:8884 | xargs kill -9

# Clean up Docker resources
docker system prune -f

# Rebuild containers
python main.py clean --force
python main.py build

# Check Docker Compose syntax
docker-compose config

# Increase Docker resources (Docker Desktop)
# Settings > Resources > Memory > 4GB+
```

#### **Issue: Container Health Checks Failing**

**Symptoms:**
- Containers marked as unhealthy
- Health check timeouts

**Diagnosis:**
```bash
# Manual health check
docker exec ash-thrash-api curl -f http://localhost:8884/health

# Check health check logs
docker inspect ash-thrash-api | jq '.[0].State.Health.Log'

# Test connectivity inside container
docker exec ash-thrash-api ping google.com
```

**Solutions:**
```bash
# Increase health check timeout
# Edit docker-compose.yml:
# healthcheck:
#   timeout: 30s  # Increase from 10s

# Disable health checks temporarily
# Comment out healthcheck section in docker-compose.yml

# Fix DNS resolution
# Add to docker-compose.yml:
# dns:
#   - 8.8.8.8
#   - 8.8.4.4
```

### **API & Testing Issues**

#### **Issue: API Server Returns 500 Errors**

**Symptoms:**
- Internal server errors
- API endpoints not responding
- FastAPI error traces

**Diagnosis:**
```bash
# Check API logs
python main.py logs ash-thrash-api

# Test API endpoints manually
curl -v http://localhost:8884/health

# Check Python imports
docker exec ash-thrash-api python -c "from src.ash_thrash_core import AshThrashTester"
```

**Solutions:**
```bash
# Restart API service
docker-compose restart ash-thrash-api

# Check environment variables
docker exec ash-thrash-api env | grep -E "(GLOBAL_|THRASH_)"

# Validate Python dependencies
docker exec ash-thrash-api pip list

# Check for code syntax errors
python -m py_compile src/ash_thrash_api.py
```

#### **Issue: Tests Always Fail**

**Symptoms:**
- All test phrases marked as failed
- 0% pass rates across all categories
- NLP server communication errors

**Diagnosis:**
```bash
# Test NLP server directly
curl -X POST http://10.20.30.253:8881/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "test message", "user_id": "test", "channel_id": "test"}'

# Check network routing
traceroute 10.20.30.253

# Verify DNS resolution
ping 10.20.30.253
```

**Solutions:**
```bash
# Update NLP server URL
# Edit .env:
# GLOBAL_NLP_API_URL=http://correct-nlp-server:8881

# Restart services with new config
python main.py stop
python main.py start

# Test with different URL
python cli.py api health --api-url http://alternative-server:8881

# Check firewall settings
sudo ufw status
```

#### **Issue: Tests Take Too Long**

**Symptoms:**
- Tests timeout before completion
- Very slow response times (>5 minutes)
- API timeout errors

**Diagnosis:**
```bash
# Check NLP server performance
time curl http://10.20.30.253:8881/health

# Monitor system resources
top
htop
docker stats

# Test single phrase
python cli.py test category definite_high --sample-size 1
```

**Solutions:**
```bash
# Reduce concurrent tests
# Edit .env:
# THRASH_MAX_CONCURRENT_TESTS=1

# Increase timeouts
# Edit .env:
# THRASH_REQUEST_TIMEOUT=60

# Use quick test mode
python cli.py test quick --sample-size 10

# Scale down other services temporarily
docker-compose stop ash-dash  # If running
```

### **Integration Issues**

#### **Issue: Discord Webhooks Not Working**

**Symptoms:**
- No Discord notifications
- Webhook errors in logs
- 404 webhook responses

**Diagnosis:**
```bash
# Test webhook manually
curl -X POST "$THRASH_DISCORD_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test message"}'

# Check webhook URL format
echo $THRASH_DISCORD_WEBHOOK_URL

# View webhook logs
python main.py logs ash-thrash-api | grep webhook
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
docker-compose restart ash-thrash-api
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

# Check CORS configuration
curl -H "Origin: http://dashboard-url" \
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
docker-compose restart ash-thrash-api

# Verify dashboard configuration
# Check ash-dash .env for correct API URL:
# THRASH_API_URL=http://10.20.30.253:8884
```

---

## 🐛 Debugging Techniques

### **Verbose Logging**

#### **Enable Debug Logging**
```bash
# Edit .env
GLOBAL_LOG_LEVEL=DEBUG
THRASH_ENABLE_DEBUG_LOGGING=true

# Restart services
python main.py stop
python main.py start

# View debug logs
python main.py logs --follow
```

#### **Python Debugging**
```python
# Add to src/ash_thrash_core.py for debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
print(f"DEBUG: Testing phrase: {phrase}")
print(f"DEBUG: NLP response: {response}")
```

### **Manual Testing**

#### **Test Individual Components**
```bash
# Test NLP integration directly
python -c "
import asyncio
from src.ash_thrash_core import NLPClient

async def test_nlp():
    async with NLPClient('http://10.20.30.253:8881') as client:
        result = await client.analyze_message('I want to die')
        print(result)

asyncio.run(test_nlp())
"

# Test single phrase
python -c "
import asyncio
from src.ash_thrash_core import AshThrashTester

async def test_phrase():
    tester = AshThrashTester()
    # Test will run automatically

asyncio.run(test_phrase())
"
```

#### **API Endpoint Testing**
```bash
# Test each endpoint individually
curl http://localhost:8884/
curl http://localhost:8884/health
curl http://localhost:8884/api/test/data

# Test with verbose output
curl -v -X POST http://localhost:8884/api/test/trigger \
  -H "Content-Type: application/json" \
  -d '{"test_type": "quick"}'
```

### **Performance Debugging**

#### **Profile Test Execution**
```python
# Add timing to test functions
import time

start_time = time.time()
# ... test execution ...
end_time = time.time()
print(f"Test took {end_time - start_time:.2f} seconds")
```

#### **Monitor Resource Usage**
```bash
# Monitor during test execution
# Terminal 1: Start test
python cli.py test comprehensive

# Terminal 2: Monitor resources
watch -n 1 'docker stats --no-stream'

# Monitor network activity
sudo netstat -i 1

# Monitor disk I/O
iostat -x 1
```

---

## 📊 Performance Issues

### **Slow Test Execution**

#### **Symptoms:**
- Tests take >5 minutes for comprehensive
- API timeouts
- High CPU/memory usage

#### **Diagnosis:**
```bash
# Check system resources
free -h
df -h
top

# Monitor network latency
ping 10.20.30.253

# Check NLP server performance
time curl http://10.20.30.253:8881/health

# Profile single test
time python cli.py test category definite_high
```

#### **Solutions:**
```bash
# Reduce concurrent tests
# Edit .env:
THRASH_MAX_CONCURRENT_TESTS=1

# Increase timeouts
THRASH_REQUEST_TIMEOUT=60
NLP_SERVER_TIMEOUT=45

# Use smaller test sets
python cli.py test quick --sample-size 10

# Check for resource constraints
# Increase Docker memory limits in docker-compose.yml
```

### **High Memory Usage**

#### **Symptoms:**
- Out of memory errors
- Container restarts
- System slowdown

#### **Diagnosis:**
```bash
# Check container memory usage
docker stats --no-stream

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
docker-compose down
docker-compose up -d
```

---

## 🔐 Security Issues

### **Permission Problems**

#### **Issue: File Permission Errors**

**Symptoms:**
- "Permission denied" errors
- Cannot write to results directory
- Docker mount issues

**Solutions:**
```bash
# Fix script permissions
chmod +x main.py cli.py

# Fix directory permissions
sudo chown -R $USER:$USER .
chmod -R 755 .

# Fix Docker volume permissions
mkdir -p results logs reports
chmod 777 results logs reports  # For Docker

# Use proper user in Docker
# Edit Dockerfile to match host user ID
```

#### **Issue: Network Security Blocking**

**Symptoms:**
- Connection refused errors
- Timeout connecting to NLP server
- Firewall blocks

**Solutions:**
```bash
# Check firewall status
sudo ufw status

# Allow required ports
sudo ufw allow 8884
sudo ufw allow from 10.20.30.0/24

# Check iptables rules
sudo iptables -L

# Test with firewall disabled (temporarily)
sudo ufw disable
# Run test
sudo ufw enable
```

---

## 🚨 Emergency Procedures

### **Production Emergency Response**

#### **Crisis Detection Failure**
1. **Immediate Action**: Lower detection thresholds
2. **Validation**: Run emergency high-crisis test
3. **Communication**: Alert team via Discord
4. **Monitoring**: Watch for continued issues
5. **Documentation**: Log incident details

```bash
# Emergency threshold adjustment
# Edit ash-nlp/.env:
NLP_HIGH_CRISIS_THRESHOLD=0.5  # Emergency low threshold

# Restart NLP service
docker-compose restart ash-nlp

# Emergency validation
python cli.py test category definite_high

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
python main.py stop
docker system prune -f
python main.py start

# Wait for services to stabilize
sleep 30

# Full system validation
python cli.py validate setup
python cli.py test comprehensive
```

### **Data Recovery**

#### **Lost Test Results**
```bash
# Check backup locations
ls -la results/
ls -la logs/

# Recover from Docker volumes
docker volume ls
docker run --rm -v ash-thrash_results:/backup alpine tar czf - /backup

# Restore from recent backups
# (Implementation depends on backup system)
```

#### **Configuration Recovery**
```bash
# Restore from template
cp .env.template .env

# Restore from git
git checkout HEAD -- .env.template

# Restore from backup
# (Implementation depends on backup system)
```

---

## 📞 Getting Help

### **Support Escalation Path**

#### **Level 1: Self-Service**
- Check this troubleshooting guide
- Review error logs: `python main.py logs`
- Verify configuration: `python cli.py validate setup`
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

#### **System Information**
```bash
# Collect diagnostic information
echo "=== System Info ===" > debug_info.txt
uname -a >> debug_info.txt
docker version >> debug_info.txt
python --version >> debug_info.txt

echo "=== Service Status ===" >> debug_info.txt
python main.py status >> debug_info.txt

echo "=== Health Check ===" >> debug_info.txt
python cli.py api health >> debug_info.txt 2>&1

echo "=== Recent Logs ===" >> debug_info.txt
python main.py logs --tail 50 >> debug_info.txt 2>&1

echo "=== Environment ===" >> debug_info.txt
cat .env | grep -v '^#' >> debug_info.txt
```

#### **Error Reproduction**
- Exact command that failed
- Complete error message
- Steps to reproduce
- Expected vs actual behavior
- Recent changes made

### **Common Support Questions**

#### **"Everything was working yesterday, now it's broken"**
- Check if ash-nlp server is running
- Verify network connectivity
- Review recent configuration changes
- Check Docker container status

#### **"Tests are failing but NLP server seems fine"**
- Validate test data structure
- Check environment variables
- Review NLP server response format
- Test individual phrases manually

#### **"Performance is much slower than expected"**
- Check system resources
- Monitor network latency
- Review concurrent test settings
- Verify NLP server performance

---

## 🔧 Advanced Troubleshooting

### **Custom Debugging Scripts**

#### **Network Connectivity Test**
```python
#!/usr/bin/env python3
import requests
import time

def test_connectivity():
    nlp_url = "http://10.20.30.253:8881"
    api_url = "http://localhost:8884"
    
    print("Testing NLP Server...")
    try:
        response = requests.get(f"{nlp_url}/health", timeout=5)
        print(f"✅ NLP Server: {response.status_code}")
    except Exception as e:
        print(f"❌ NLP Server: {e}")
    
    print("Testing API Server...")
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        print(f"✅ API Server: {response.status_code}")
    except Exception as e:
        print(f"❌ API Server: {e}")

if __name__ == "__main__":
    test_connectivity()
```

#### **Performance Benchmark**
```python
#!/usr/bin/env python3
import time
import requests

def benchmark_api():
    base_url = "http://localhost:8884"
    
    # Test response times
    endpoints = [
        "/health",
        "/api/test/data", 
        "/api/test/goals"
    ]
    
    for endpoint in endpoints:
        start_time = time.time()
        try:
            response = requests.get(f"{base_url}{endpoint}")
            end_time = time.time()
            print(f"{endpoint}: {(end_time - start_time)*1000:.1f}ms")
        except Exception as e:
            print(f"{endpoint}: ERROR - {e}")

if __name__ == "__main__":
    benchmark_api()
```

### **Log Analysis Tools**

#### **Error Pattern Detection**
```bash
# Find common error patterns
grep -i error logs/ash-thrash.log | sort | uniq -c | sort -nr

# Check for specific issues
grep -i "nlp.*unreachable" logs/ash-thrash.log
grep -i "timeout" logs/ash-thrash.log
grep -i "failed.*test" logs/ash-thrash.log

# Analyze timing patterns
grep -E "\d{4}-\d{2}-\d{2}.*ERROR" logs/ash-thrash.log | \
  awk '{print $1, $2}' | sort | uniq -c
```

#### **Performance Analysis**
```bash
# Extract response times
grep -o "processing_time_ms.*" logs/ash-thrash.log | \
  sed 's/.*: //' | sort -n

# Find slow operations
grep -E "(took|duration).*[0-9]+.*ms" logs/ash-thrash.log | \
  grep -E "[0-9]{4,}ms"  # Over 1 second

# Analyze test patterns
grep "test.*completed" logs/ash-thrash.log | \
  awk '{print $NF}' | sort | uniq -c
```

---

**This troubleshooting guide covers the most common issues encountered with Ash-Thrash v3.0. For issues not covered here, please create a GitHub issue with detailed diagnostic information.**

**Emergency Contact**: [Discord #ash-development](https://discord.gg/alphabetcartel)  
**Repository**: [https://github.com/the-alphabet-cartel/ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash)  
**Documentation**: [Complete documentation suite](../README.md)

*Keeping crisis detection systems running smoothly for safer communities.* 🛠️🔍