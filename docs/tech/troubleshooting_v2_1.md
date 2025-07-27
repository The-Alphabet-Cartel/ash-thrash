# 🔧 Ash-Thrash Troubleshooting Guide

> **Comprehensive Problem Resolution for Crisis Detection Testing**

**Repository:** https://github.com/The-Alphabet-Cartel/ash-thrash  
**Discord:** https://discord.gg/alphabetcartel  
**System:** Windows 11 with Docker (10.20.30.16)  
**Last Updated:** July 26, 2025

---

## 📋 Quick Diagnostic Checklist

### Before You Start

**Essential Information to Gather:**
1. **System Status:**
   - Windows 11 server status (10.20.30.16)
   - Docker Desktop status
   - Available disk space and memory
   - Recent system changes or updates

2. **Service Status:**
   - Ash-Thrash API (port 8884)
   - Ash NLP Server (port 8881) 
   - Ash-Dash Dashboard (port 8883)
   - Network connectivity between services

3. **Recent Activity:**
   - Last successful test completion
   - Recent error messages or alerts
   - Any configuration changes
   - System restarts or updates

---

## 🚨 Critical Issues (Immediate Action Required)

### Issue: "High Priority Detection Below 95%"

**Symptoms:**
- Definite high priority phrases not being detected correctly
- Crisis detection failing on critical phrases
- Dashboard showing red alerts

**Immediate Actions:**
```powershell
# 1. Check NLP server status
curl http://10.20.30.16:8881/health

# 2. Run manual test on known high-priority phrase
curl -X POST http://10.20.30.16:8881/api/analyze `
  -H "Content-Type: application/json" `
  -d '{"text": "I want to end it all", "analyze_crisis": true}'

# 3. Check recent test results
curl http://10.20.30.16:8884/api/test/results/latest | ConvertFrom-Json | Select-Object -ExpandProperty category_results | Select-Object -ExpandProperty definite_high
```

**Root Cause Analysis:**
1. **NLP Model Issues:**
   - Model weights corrupted
   - GPU memory issues on AI server
   - Model loading errors

2. **Configuration Problems:**
   - Detection thresholds changed
   - Category definitions modified
   - Environment variables incorrect

3. **Resource Constraints:**
   - AI server overloaded
   - Network latency issues
   - Insufficient GPU memory

**Resolution Steps:**
```powershell
# Restart NLP server
docker-compose -f ..\ash-nlp\docker-compose.yml restart

# Clear GPU cache (if applicable)
docker-compose -f ..\ash-nlp\docker-compose.yml exec ash-nlp python -c "import torch; torch.cuda.empty_cache()"

# Verify configuration
docker-compose exec ash-thrash cat /app/.env | Select-String "NLP_SERVER"
```

### Issue: "System Completely Unreachable"

**Symptoms:**
- API returns 503 Service Unavailable
- Cannot connect to testing endpoints
- Dashboard shows offline status

**Emergency Checklist:**
```powershell
# 1. Check if Windows server is responding
Test-NetConnection 10.20.30.16 -Port 22

# 2. Check Docker services on server
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 3. Check service health
docker-compose exec ash-thrash python -c "import requests; print(requests.get('http://localhost:8884/health').status_code)"
```

**Resolution Priority:**
1. **Restart Docker services**
2. **Check Windows server resources**
3. **Verify network connectivity**
4. **Contact system administrator if server unresponsive**

---

## ⚠️ Common Issues & Solutions

### Connection Issues

#### "Cannot Connect to NLP Server"

**Error Messages:**
- `Connection refused to 10.20.30.16:8881`
- `NLP server timeout`
- `Failed to connect to ash-nlp`

**Diagnostic Steps:**
```powershell
# Test basic connectivity
Test-NetConnection 10.20.30.16 -Port 8881

# Check NLP container status
docker ps | Select-String "ash-nlp"

# Check NLP server logs
docker logs ash-nlp | Select-Object -Last 50

# Verify NLP server health endpoint
curl http://10.20.30.16:8881/health
```

**Common Causes & Fixes:**

**1. NLP Server Down:**
```powershell
# Restart NLP server
cd ..\ash-nlp
docker-compose restart

# Check startup logs
docker-compose logs -f ash-nlp
```

**2. Windows Firewall Blocking:**
```powershell
# Check firewall rules
Get-NetFirewallRule -DisplayName "*ash*" | Format-Table

# Add firewall rule if missing
New-NetFirewallRule -DisplayName "Ash-NLP Server" -Direction Inbound -Port 8881 -Protocol TCP -Action Allow
```

**3. Network Configuration:**
```powershell
# Check network adapter
Get-NetAdapter | Where-Object {$_.Status -eq "Up"}

# Check IP configuration
ipconfig /all | Select-String "10.20.30"

# Reset network if needed
ipconfig /release
ipconfig /renew
```

#### "API Server Not Responding"

**Error Messages:**
- `Connection refused to localhost:8884`
- `API server timeout`
- `502 Bad Gateway`

**Quick Fixes:**
```powershell
# Restart ash-thrash API
docker-compose restart ash-thrash-api

# Check port availability
netstat -an | Select-String "8884"

# Verify container health
docker-compose exec ash-thrash-api curl http://localhost:8884/health
```

### Performance Issues

#### "Tests Running Very Slowly"

**Symptoms:**
- Comprehensive tests taking > 20 minutes
- Individual phrase analysis > 5 seconds
- High CPU/memory usage

**Performance Diagnostics:**
```powershell
# Check system resources
Get-Counter "\Processor(_Total)\% Processor Time" -SampleInterval 5 -MaxSamples 3
Get-Counter "\Memory\Available MBytes" -SampleInterval 5 -MaxSamples 3

# Check Docker resource usage
docker stats --no-stream

# Check GPU usage (if applicable)
nvidia-smi
```

**Optimization Steps:**

**1. Reduce Concurrent Tests:**
```bash
# In .env file
MAX_CONCURRENT_TESTS=3    # Reduce from default 5 or 8
TEST_TIMEOUT_SECONDS=20   # Increase timeout
```

**2. Check AI Server Resources:**
```powershell
# Monitor GPU memory
nvidia-smi dmon -s m

# Check for memory leaks
docker stats ash-nlp --no-stream
```

**3. Network Optimization:**
```bash
# In .env file
NLP_SERVER_TIMEOUT=30     # Increase network timeout
ENABLE_DETAILED_LOGGING=false  # Reduce logging overhead
```

#### "High Memory Usage"

**Symptoms:**
- System becoming unresponsive
- Docker containers killed by OS
- Out of memory errors

**Memory Management:**
```powershell
# Check memory usage by process
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10

# Check Docker memory limits
docker inspect ash-thrash-api | Select-String "Memory"

# Clear system memory
docker system prune -f
```

### Test Result Issues

#### "Inconsistent Test Results"

**Symptoms:**
- Same phrases getting different results
- Pass rates fluctuating wildly
- Confidence scores varying significantly

**Investigation Steps:**
```powershell
# Compare recent test results
curl http://10.20.30.16:8884/api/test/results/history?days=3 | ConvertFrom-Json

# Check for specific phrase patterns
curl http://10.20.30.16:8884/api/analytics/failures | ConvertFrom-Json | Select-Object -ExpandProperty failure_patterns

# Test individual phrases manually
curl -X POST http://10.20.30.16:8881/api/analyze `
  -H "Content-Type: application/json" `
  -d '{"text": "test phrase here", "analyze_crisis": true}'
```

**Common Causes:**
1. **NLP Model Instability** - Model weights changing between tests
2. **Resource Constraints** - Insufficient GPU memory causing degraded performance
3. **Network Issues** - Intermittent connectivity affecting results
4. **Temperature Scaling** - Model confidence calibration issues

#### "False Positive Rate Too High"

**Symptoms:**
- Non-crisis phrases being flagged as crises
- "Definite None" category failing targets
- Alert fatigue in production

**Analysis:**
```powershell
# Get detailed false positive analysis
curl http://10.20.30.16:8884/api/analytics/failures?category=definite_none | ConvertFrom-Json

# Check specific failed phrases
curl http://10.20.30.16:8884/api/test/results/latest?include_failures=true | ConvertFrom-Json | Select-Object -ExpandProperty category_results | Select-Object -ExpandProperty definite_none | Select-Object -ExpandProperty failures
```

**Resolution:**
1. **Review Detection Thresholds** - May need adjustment in NLP model
2. **Update Test Phrases** - Ensure test phrases reflect real usage
3. **Model Retraining** - Consider retraining with updated data

---

## 🔧 System-Specific Troubleshooting

### Windows 11 Specific Issues

#### "Docker Desktop Won't Start"

**Common Causes:**
- WSL 2 backend issues
- Hyper-V conflicts
- Windows updates interfering

**Resolution:**
```powershell
# Check WSL status
wsl --status

# Reset WSL if needed
wsl --shutdown
wsl --update

# Restart Docker Desktop
Stop-Process -Name "Docker Desktop" -Force
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Check Docker service
Get-Service | Where-Object {$_.Name -like "*docker*"}
```

#### "Windows Firewall Blocking Services"

**Symptoms:**
- Services work locally but not remotely
- Intermittent connectivity issues
- Specific ports being blocked

**Firewall Configuration:**
```powershell
# Check current firewall rules
Get-NetFirewallRule | Where-Object {$_.Enabled -eq "True" -and $_.Direction -eq "Inbound"} | Select-Object DisplayName, LocalPort

# Add required rules
New-NetFirewallRule -DisplayName "Ash-Thrash API" -Direction Inbound -Port 8884 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Ash-NLP Server" -Direction Inbound -Port 8881 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Ash-Dashboard" -Direction Inbound -Port 8883 -Protocol TCP -Action Allow

# Allow Docker network
New-NetFirewallRule -DisplayName "Docker Network" -Direction Inbound -LocalAddress 172.16.0.0/12 -Action Allow
```

### Docker-Specific Issues

#### "Container Won't Start"

**Error Messages:**
- `driver failed programming external connectivity`
- `port already in use`
- `image not found`

**Diagnostic Steps:**
```powershell
# Check port conflicts
netstat -an | Select-String "8884"

# Check Docker images
docker images | Select-String "ash-thrash"

# Check container logs
docker-compose logs ash-thrash-api

# Check Docker daemon
docker version
```

**Resolution:**
```powershell
# Stop conflicting services
Stop-Process -Name "python" -Force
Stop-Service W3SVC -Force  # If IIS is running

# Clean Docker environment
docker-compose down
docker system prune -f

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d
```

#### "Volume Mount Issues"

**Symptoms:**
- Configuration changes not persisting
- Results not being saved
- Permission denied errors

**Fix Volume Issues:**
```powershell
# Check volume mounts
docker-compose config | Select-String "volumes"

# Fix permissions (if needed)
icacls "C:\Projects\ash-thrash\results" /grant Everyone:F /T

# Verify volume paths
docker-compose exec ash-thrash ls -la /app/results/
```

---

## 📊 Monitoring and Alerts

### Setting Up Monitoring

**PowerShell Health Check Script:**
```powershell
# Save as C:\Scripts\ash-thrash-monitor.ps1
param(
    [int]$AlertThreshold = 80,
    [string]$LogPath = "C:\Logs\ash-thrash-monitor.log"
)

function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $LogPath -Append
    Write-Host "$timestamp - $Message"
}

# Test API Health
try {
    $apiHealth = Invoke-RestMethod -Uri "http://localhost:8884/health" -TimeoutSec 10
    Write-Log "✅ API Health: OK"
} catch {
    Write-Log "❌ API Health: FAILED - $($_.Exception.Message)"
    # Send alert here
}

# Test NLP Server
try {
    $nlpHealth = Invoke-RestMethod -Uri "http://10.20.30.16:8881/health" -TimeoutSec 10
    Write-Log "✅ NLP Server: OK"
} catch {
    Write-Log "❌ NLP Server: FAILED - $($_.Exception.Message)"
    # Send alert here
}

# Check latest test results
try {
    $results = Invoke-RestMethod -Uri "http://localhost:8884/api/test/results/latest" -TimeoutSec 10
    $passRate = $results.summary.pass_rate
    
    if ($passRate -lt $AlertThreshold) {
        Write-Log "⚠️ Pass Rate Below Threshold: $passRate% (Target: $AlertThreshold%)"
        # Send alert here
    } else {
        Write-Log "✅ Pass Rate: $passRate%"
    }
} catch {
    Write-Log "❌ Could not retrieve test results - $($_.Exception.Message)"
}

# Check high priority detection
try {
    $highPriorityRate = $results.category_results.definite_high.pass_rate
    if ($highPriorityRate -lt 95) {
        Write-Log "🚨 CRITICAL: High Priority Detection at $highPriorityRate% (Target: 100%)"
        # Send critical alert here
    }
} catch {
    Write-Log "❌ Could not check high priority detection"
}
```

**Schedule Monitoring:**
```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\Scripts\ash-thrash-monitor.ps1"
$trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 5) -Once -At (Get-Date)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "Ash-Thrash Monitor" -Action $action -Trigger $trigger -Settings $settings
```

### Alert Configuration

**Discord Webhook Integration:**
```powershell
function Send-DiscordAlert {
    param(
        [string]$Message,
        [string]$WebhookUrl = "YOUR_DISCORD_WEBHOOK_URL",
        [string]$Severity = "warning"
    )
    
    $colorMap = @{
        "info" = 3447003      # Blue
        "warning" = 16776960  # Yellow
        "critical" = 15158332 # Red
    }
    
    $payload = @{
        embeds = @(@{
            title = "Ash-Thrash Alert"
            description = $Message
            color = $colorMap[$Severity]
            timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
            footer = @{
                text = "Ash-Thrash Monitoring System"
            }
        })
    } | ConvertTo-Json -Depth 3
    
    try {
        Invoke-RestMethod -Uri $WebhookUrl -Method Post -Body $payload -ContentType "application/json"
    } catch {
        Write-Log "Failed to send Discord alert: $($_.Exception.Message)"
    }
}
```

---

## 🔍 Advanced Diagnostics

### Log Analysis

**Viewing Detailed Logs:**
```powershell
# View API logs
docker-compose logs ash-thrash-api | Select-Object -Last 100

# View NLP server logs
docker-compose -f ..\ash-nlp\docker-compose.yml logs ash-nlp | Select-Object -Last 100

# Search for specific errors
docker-compose logs ash-thrash-api | Select-String "ERROR"
docker-compose logs ash-thrash-api | Select-String "TIMEOUT"
docker-compose logs ash-thrash-api | Select-String "FAILED"

# Export logs for analysis
docker-compose logs ash-thrash-api > "C:\Logs\ash-thrash-$(Get-Date -Format 'yyyyMMdd-HHmm').log"
```

**Log Patterns to Watch:**
- `Connection refused` - Network connectivity issues
- `Timeout` - Performance or overload issues
- `Memory error` - Resource constraint issues
- `404` or `500` errors - API or configuration issues

### Performance Profiling

**Resource Usage Analysis:**
```powershell
# System performance baseline
Get-Counter "\Processor(_Total)\% Processor Time" -Continuous -SampleInterval 5

# Memory usage monitoring
Get-Counter "\Memory\Available MBytes" -Continuous -SampleInterval 5

# Network performance
Get-Counter "\Network Interface(*)\Bytes Total/sec" -Continuous -SampleInterval 5

# Docker container stats
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
```

**Performance Benchmarking:**
```powershell
# Time a comprehensive test
$start = Get-Date
docker-compose exec ash-thrash python src/comprehensive_testing.py
$end = Get-Date
$duration = $end - $start
Write-Host "Test completed in: $($duration.TotalMinutes) minutes"

# Measure API response time
$start = Get-Date
$response = Invoke-RestMethod -Uri "http://localhost:8884/api/test/status"
$end = Get-Date
$responseTime = ($end - $start).TotalMilliseconds
Write-Host "API response time: $responseTime ms"
```

### Network Diagnostics

**Comprehensive Network Testing:**
```powershell
# Test all required connections
$endpoints = @(
    @{Name="Ash-Thrash API"; Host="localhost"; Port=8884},
    @{Name="NLP Server"; Host="10.20.30.16"; Port=8881},
    @{Name="Ash-Dashboard"; Host="10.20.30.16"; Port=8883}
)

foreach ($endpoint in $endpoints) {
    $result = Test-NetConnection -ComputerName $endpoint.Host -Port $endpoint.Port -WarningAction SilentlyContinue
    if ($result.TcpTestSucceeded) {
        Write-Host "✅ $($endpoint.Name): Connected" -ForegroundColor Green
    } else {
        Write-Host "❌ $($endpoint.Name): Failed" -ForegroundColor Red
    }
}

# Test DNS resolution
Resolve-DnsName "10.20.30.16"

# Test routing
tracert 10.20.30.16
```

---

## 🆘 Emergency Procedures

### Complete System Recovery

**When Everything Fails:**

1. **Backup Current State:**
```powershell
$timestamp = Get-Date -Format "yyyyMMdd-HHmm"
Compress-Archive -Path "C:\Projects\ash-thrash" -DestinationPath "C:\Backups\ash-thrash-emergency-$timestamp.zip"
```

2. **Stop All Services:**
```powershell
docker-compose down
docker system prune -a -f
```

3. **Reset to Known Good State:**
```powershell
# Pull latest from GitHub
cd C:\Projects\ash-thrash
git stash
git pull origin main

# Rebuild everything
docker-compose build --no-cache
docker-compose up -d
```

4. **Verify Recovery:**
```powershell
# Test all components
curl http://localhost:8884/health
curl http://10.20.30.16:8881/health
docker-compose exec ash-thrash python src/quick_validation.py
```

### Emergency Contact Procedures

**Escalation Matrix:**

**Level 1 - Self-Service (0-30 minutes):**
- Use this troubleshooting guide
- Check Discord #tech-support channel
- Review recent GitHub issues

**Level 2 - Team Support (30-60 minutes):**
- Post in Discord #crisis-response channel
- Tag @Technical Team in Discord
- Create GitHub issue with logs

**Level 3 - Emergency (Critical system failure):**
- Contact Technical Lead directly
- If main Ash bot affected, consider manual monitoring
- Document timeline and symptoms

---

## 📚 Reference Information

### Common Error Codes

**HTTP Status Codes:**
- `503 Service Unavailable` - NLP server down or overloaded
- `504 Gateway Timeout` - Network timeout to NLP server
- `409 Conflict` - Test already running
- `422 Unprocessable Entity` - Invalid test parameters

**Application Error Codes:**
- `NLP_SERVER_UNREACHABLE` - Cannot connect to NLP server
- `TEST_ALREADY_RUNNING` - Another test in progress
- `INVALID_CATEGORY` - Unknown test category specified
- `TIMEOUT_EXCEEDED` - Test took too long to complete

### Configuration File Locations

**Key Files:**
- **Environment:** `C:\Projects\ash-thrash\.env`
- **Docker Compose:** `C:\Projects\ash-thrash\docker-compose.yml`
- **Test Data:** `C:\Projects\ash-thrash\src\test_data\`
- **Results:** `C:\Projects\ash-thrash\results\`
- **Logs:** Docker container logs (view with `docker-compose logs`)

### Default Port Assignments

**Service Ports:**
- **Ash-Thrash API:** 8884
- **Ash NLP Server:** 8881  
- **Ash-Dash Dashboard:** 8883
- **Main Ash Bot:** No direct port (Discord WebSocket)

### Resource Requirements

**Minimum System Requirements:**
- **CPU:** 4 cores, 2.5GHz
- **RAM:** 8GB total, 4GB available for Docker
- **Storage:** 10GB free space
- **Network:** 100Mbps local network

**Recommended for Your Setup:**
- **CPU:** AMD Ryzen 7 7700X ✅
- **RAM:** 64GB (plenty of headroom) ✅
- **GPU:** NVIDIA RTX 3050 (for NLP server) ✅
- **Storage:** NVMe SSD recommended ✅

---

## 📞 Getting Additional Help

### Support Channels

**Primary Support:**
- **Discord:** #tech-support in https://discord.gg/alphabetcartel
- **GitHub Issues:** https://github.com/The-Alphabet-Cartel/ash-thrash/issues
- **Documentation:** README.md and team guides

**When Contacting Support:**

**Include This Information:**
1. **Error Description:** What happened and when
2. **Steps to Reproduce:** What you were doing before the error
3. **System Info:** Windows version, Docker version, available resources
4. **Logs:** Recent Docker logs and error messages
5. **Recent Changes:** Any configuration or system changes

**Log Collection Script:**
```powershell
# Collect diagnostic information
$timestamp = Get-Date -Format "yyyyMMdd-HHmm"
$diagPath = "C:\Temp\ash-thrash-diag-$timestamp"
New-Item -ItemType Directory -Path $diagPath -Force

# System information
Get-ComputerInfo | Out-File "$diagPath\system-info.txt"
docker version | Out-File "$diagPath\docker-version.txt"
docker-compose version | Out-File "$diagPath\docker-compose-version.txt"

# Service status
docker ps -a | Out-File "$diagPath\docker-containers.txt"
netstat -an | Select-String "8884|8881|8883" | Out-File "$diagPath\port-status.txt"

# Recent logs
docker-compose logs --tail=100 ash-thrash-api | Out-File "$diagPath\api-logs.txt"
docker-compose logs --tail=100 ash-thrash | Out-File "$diagPath\thrash-logs.txt"

# Configuration
Copy-Item ".env" "$diagPath\env-config.txt"
Copy-Item "docker-compose.yml" "$diagPath\docker-compose.yml"

# Compress for sharing
Compress-Archive -Path $diagPath -DestinationPath "$diagPath.zip"
Write-Host "Diagnostic package created: $diagPath.zip"
```

### Community Resources

**Useful Links:**
- **Main Documentation:** Comprehensive setup and usage guides
- **GitHub Repository:** Source code and issue tracking
- **Discord Community:** Real-time help and community support
- **Video Tutorials:** Available in Discord resources channel

---

*Built with 🖤 for The Alphabet Cartel community*

**Troubleshooting Guide v2.1**  
Last updated: July 26, 2025