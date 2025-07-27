# 🔧 Ash-Thrash Implementation Guide

> **Technical Setup and Deployment Guide for Crisis Detection Testing**

**Repository:** https://github.com/The-Alphabet-Cartel/ash-thrash  
**Discord:** https://discord.gg/alphabetcartel  
**Target Environment:** Windows 11 with Docker  
**Last Updated:** July 26, 2025

---

## 📋 System Requirements

### Hardware Requirements

**Minimum Specifications:**
- **CPU:** 4-core processor (Intel i5 or AMD Ryzen 5 equivalent)
- **RAM:** 8GB minimum, 16GB recommended
- **Storage:** 10GB free space for application and results
- **Network:** Reliable internet connection with access to 10.20.30.16

**Recommended Specifications (Your Current Setup):**
- **CPU:** AMD Ryzen 7 7700X ✅
- **RAM:** 64GB ✅
- **GPU:** NVIDIA RTX 3050 (not required for ash-thrash) ✅
- **OS:** Windows 11 ✅

### Software Requirements

**Required Software:**
- **Docker Desktop** - Latest version with Windows containers support
- **Docker Compose** - Included with Docker Desktop
- **Git** - For repository cloning and updates
- **GitHub Desktop** - Your preferred Git interface ✅

**Optional Development Tools:**
- **Atom Editor** - Your preferred editor ✅
- **Python 3.11+** - For local development and testing
- **PowerShell** - For Windows-based script execution

---

## 🚀 Initial Setup

### Step 1: Repository Setup

**Using GitHub Desktop (Your Preferred Method):**

1. Open GitHub Desktop
2. Click "Clone a repository from the Internet"
3. Repository URL: `https://github.com/The-Alphabet-Cartel/ash-thrash`
4. Local path: Choose your preferred location (e.g., `C:\Projects\ash-thrash`)
5. Click "Clone"

**Alternative - Command Line:**
```bash
git clone https://github.com/The-Alphabet-Cartel/ash-thrash.git
cd ash-thrash
```

### Step 2: Environment Configuration

**Create Environment File:**

1. Copy `.env.template` to `.env`
2. Open `.env` in Atom
3. Configure the following key settings:

```bash
# Core NLP Server Settings (Default for your setup)
NLP_SERVER_HOST=10.20.30.16
NLP_SERVER_PORT=8881
NLP_SERVER_URL=http://10.20.30.16:8881

# Performance Settings (Optimized for your hardware)
MAX_CONCURRENT_TESTS=8          # Increased for your powerful CPU
TEST_TIMEOUT_SECONDS=15         # Conservative timeout
RESULTS_RETENTION_DAYS=90       # Extended retention for your storage

# API Configuration
API_PORT=8884
API_HOST=0.0.0.0
API_DEBUG=false

# Scheduling
ENABLE_SCHEDULED_TESTING=true
COMPREHENSIVE_TEST_SCHEDULE=0 */6 * * *    # Every 6 hours
QUICK_VALIDATION_SCHEDULE=0 * * * *        # Every hour
```

### Step 3: Docker Setup

**Install Docker Desktop:**

1. Download from https://www.docker.com/products/docker-desktop
2. Install with default settings
3. Enable WSL 2 backend if prompted
4. Start Docker Desktop
5. Verify installation:

```powershell
docker --version
docker-compose --version
```

**Configure Docker Resources:**

1. Open Docker Desktop Settings
2. Go to Resources → Advanced
3. Set allocations:
   - **CPUs:** 6 (leave 2 for Windows)
   - **Memory:** 16GB (leave plenty for Windows)
   - **Swap:** 4GB
   - **Disk Image Size:** 60GB

### Step 4: Initial Deployment

**Using Docker Compose (Recommended):**

```powershell
# Navigate to project directory
cd C:\Projects\ash-thrash

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs for successful startup
docker-compose logs ash-thrash-api
```

**Expected Output:**
```
ash-thrash-api    | INFO: Started server process
ash-thrash-api    | INFO: Waiting for application startup.
ash-thrash-api    | INFO: Application startup complete.
ash-thrash-api    | INFO: Uvicorn running on http://0.0.0.0:8884
```

### Step 5: Initial Validation

**Run First Test:**

```powershell
# Quick validation test (10 phrases)
docker-compose exec ash-thrash python src/quick_validation.py
```

**Verify API Access:**
```powershell
# Test API health
curl http://localhost:8884/health

# Check testing status
curl http://localhost:8884/api/test/status
```

---

## 🔧 Configuration Details

### Network Configuration

**Firewall Rules:**

```powershell
# Allow inbound connections to ash-thrash API
New-NetFirewallRule -DisplayName "Ash-Thrash API" -Direction Inbound -Port 8884 -Protocol TCP -Action Allow

# Allow outbound connections to NLP server
New-NetFirewallRule -DisplayName "Ash-NLP Access" -Direction Outbound -Port 8881 -Protocol TCP -Action Allow
```

**Network Testing:**

```powershell
# Verify NLP server connectivity
Test-NetConnection -ComputerName 10.20.30.16 -Port 8881

# Verify local API
Test-NetConnection -ComputerName localhost -Port 8884
```

### Storage Configuration

**Directory Structure:**
```
C:\Projects\ash-thrash\
├── src/                    # Application source code
├── results/               # Test results storage
│   ├── comprehensive/    # Full 350-phrase test results
│   ├── quick_validation/ # Quick 10-phrase test results
│   ├── reports/          # Generated reports
│   └── backups/          # Archived results
├── config/               # Configuration files
├── docker/               # Docker configuration
├── docs/                 # Documentation
└── .env                  # Environment configuration
```

**Volume Mounts:**
```yaml
# In docker-compose.yml
volumes:
  - ./results:/app/results              # Results persistence
  - ./config:/app/config                # Configuration persistence
  - ./src:/app/src                      # Development volume
```

### Performance Tuning

**For Your Hardware (Ryzen 7 7700X, 64GB RAM):**

```bash
# Optimized settings for your system
MAX_CONCURRENT_TESTS=8              # Utilize multiple cores
TEST_TIMEOUT_SECONDS=10             # Fast hardware, shorter timeout
ENABLE_DETAILED_LOGGING=true        # Plenty of storage
RESULTS_RETENTION_DAYS=180          # Extended retention
MAX_MEMORY_USAGE=8GB               # Conservative memory limit
```

**Docker Resource Optimization:**
```yaml
# In docker-compose.yml
services:
  ash-thrash:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '4.0'
        reservations:
          memory: 2G
          cpus: '2.0'
```

---

## 🚀 Deployment Options

### Option 1: Development Deployment

**For testing and development work:**

```powershell
# Clone repository
git clone https://github.com/The-Alphabet-Cartel/ash-thrash.git
cd ash-thrash

# Setup development environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run locally
python src/comprehensive_testing.py
```

### Option 2: Production Deployment (Recommended)

**For continuous operation:**

```powershell
# Setup as Windows service using Docker
docker-compose up -d

# Enable auto-restart
docker-compose config | grep restart
# Should show: restart: unless-stopped

# Verify automatic startup
Restart-Computer
# After restart, check:
docker-compose ps
```

### Option 3: Hybrid Deployment

**Development with Docker backing:**

```powershell
# Start API services with Docker
docker-compose up -d ash-thrash-api

# Run tests locally
python src/comprehensive_testing.py --api-url http://localhost:8884
```

---

## 🔗 Integration Setup

### Ash-Dash Integration

**Method 1: Full Integration**

1. Copy integration components:
```powershell
# Copy to ash-dash repository
Copy-Item dashboard\routes.js ..\ash-dash\routes\testing.js
Copy-Item dashboard\styles\testing-dashboard.css ..\ash-dash\public\css\
Copy-Item dashboard\templates\testing-section.html ..\ash-dash\views\partials\
```

2. Update ash-dash server.js:
```javascript
// Add to server.js
const testingRoutes = require('./routes/testing');
app.use('/api/testing', testingRoutes);
```

**Method 2: API Integration Only**

1. Configure ash-dash to call ash-thrash API:
```javascript
// In ash-dash frontend
const testingApiUrl = 'http://10.20.30.16:8884';

// Fetch testing status
fetch(`${testingApiUrl}/api/test/status`)
  .then(response => response.json())
  .then(data => updateTestingDisplay(data));
```

### NLP Server Validation

**Verify NLP Server Connectivity:**

```powershell
# Direct API test
Invoke-RestMethod -Uri "http://10.20.30.16:8881/health" -Method GET

# Test crisis detection endpoint
$body = @{
    text = "I can't take this anymore"
    analyze_crisis = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://10.20.30.16:8881/api/analyze" -Method POST -Body $body -ContentType "application/json"
```

---

## 📊 Monitoring Setup

### Windows Performance Monitoring

**Set up performance counters:**

```powershell
# Monitor Docker resource usage
Get-Counter "\Docker\Memory Usage" -Continuous
Get-Counter "\Docker\CPU Usage" -Continuous

# Monitor network to NLP server
Get-Counter "\Network Interface(*)\Bytes Total/sec" -Continuous
```

### Log Management

**Configure log rotation:**

```yaml
# In docker-compose.yml
services:
  ash-thrash-api:
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"
```

**PowerShell log monitoring:**

```powershell
# Monitor Docker logs in real-time
docker-compose logs -f ash-thrash-api

# Search logs for errors
docker-compose logs ash-thrash-api | Select-String "ERROR"

# Export logs for analysis
docker-compose logs ash-thrash-api > C:\Logs\ash-thrash-$(Get-Date -Format 'yyyyMMdd').log
```

### Automated Health Checks

**Create PowerShell monitoring script:**

```powershell
# Save as monitor-ash-thrash.ps1
$apiUrl = "http://localhost:8884/health"
$nlpUrl = "http://10.20.30.16:8881/health"

# Check API health
try {
    $apiResponse = Invoke-RestMethod -Uri $apiUrl -TimeoutSec 5
    Write-Host "✅ Ash-Thrash API: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Ash-Thrash API: FAILED" -ForegroundColor Red
}

# Check NLP server health
try {
    $nlpResponse = Invoke-RestMethod -Uri $nlpUrl -TimeoutSec 5
    Write-Host "✅ NLP Server: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ NLP Server: FAILED" -ForegroundColor Red
}
```

**Schedule monitoring with Task Scheduler:**

```powershell
# Create scheduled task for monitoring
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\Scripts\monitor-ash-thrash.ps1"
$trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 5) -Once -At (Get-Date)
Register-ScheduledTask -TaskName "Ash-Thrash Monitor" -Action $action -Trigger $trigger
```

---

## 🔧 Maintenance Procedures

### Regular Maintenance

**Weekly Tasks:**

```powershell
# Update containers
docker-compose pull
docker-compose up -d

# Clean up old results (keep 30 days)
Get-ChildItem results\comprehensive\ -Recurse | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item

# Check disk usage
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, @{Name="Size(GB)";Expression={[math]::Round($_.Size/1GB,2)}}, @{Name="FreeSpace(GB)";Expression={[math]::Round($_.FreeSpace/1GB,2)}}
```

**Monthly Tasks:**

```powershell
# Full system backup
$date = Get-Date -Format "yyyyMMdd"
Compress-Archive -Path "C:\Projects\ash-thrash" -DestinationPath "C:\Backups\ash-thrash-$date.zip"

# Performance report
docker stats --no-stream > "C:\Reports\docker-stats-$date.txt"

# Update documentation
git pull origin main
```

### Troubleshooting

**Common Issues and Solutions:**

**Issue: "Cannot connect to NLP server"**
```powershell
# Check network connectivity
Test-NetConnection 10.20.30.16 -Port 8881

# Check Windows Defender Firewall
Get-NetFirewallRule -DisplayName "*ash*" | Format-Table
```

**Issue: "Docker service won't start"**
```powershell
# Restart Docker Desktop
Restart-Service com.docker.service

# Reset Docker to defaults (if needed)
docker system prune -a
```

**Issue: "High memory usage"**
```powershell
# Check container memory usage
docker stats --no-stream

# Restart containers to clear memory
docker-compose restart
```

### Updates and Upgrades

**Update Procedure:**

1. **Backup current installation:**
```powershell
$date = Get-Date -Format "yyyyMMdd"
Compress-Archive -Path "C:\Projects\ash-thrash" -DestinationPath "C:\Backups\ash-thrash-backup-$date.zip"
```

2. **Pull latest changes:**
```powershell
# Using GitHub Desktop
# Click "Fetch origin" then "Pull origin"

# Or command line
git pull origin main
```

3. **Update Docker images:**
```powershell
docker-compose pull
docker-compose up -d
```

4. **Verify update:**
```powershell
# Check version
curl http://localhost:8884/api/test/status | ConvertFrom-Json | Select-Object version

# Run test
docker-compose exec ash-thrash python src/quick_validation.py
```

---

## 📚 Development Environment

### Setting Up for Code Contributions

**Using Your Preferred Tools (Atom + GitHub Desktop):**

1. **Fork the repository** in GitHub
2. **Clone your fork** using GitHub Desktop
3. **Open in Atom** for editing
4. **Setup development environment:**

```powershell
# Install Python dependencies
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Code Style and Standards

**Python Standards:**
- Follow PEP 8 style guidelines
- Use type hints where possible
- Include docstrings for functions and classes
- Maximum line length: 88 characters (Black formatter)

**Testing:**
```powershell
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Format code
black src/
isort src/
```

### Contributing Workflow

1. **Create feature branch** using GitHub Desktop
2. **Make changes** in Atom
3. **Test changes** locally:
```powershell
# Test your changes
python src/comprehensive_testing.py --dry-run
pytest tests/test_your_feature.py
```
4. **Commit and push** using GitHub Desktop
5. **Create pull request** on GitHub

---

## 🔒 Security Considerations

### Network Security

**Firewall Configuration:**
```powershell
# Only allow necessary connections
New-NetFirewallRule -DisplayName "Ash-Thrash Inbound" -Direction Inbound -Port 8884 -Protocol TCP -Action Allow -LocalAddress 10.20.30.0/24
New-NetFirewallRule -DisplayName "Ash-NLP Outbound" -Direction Outbound -Port 8881 -Protocol TCP -Action Allow -RemoteAddress 10.20.30.16
```

**Access Control:**
- API accessible only from local network (10.20.30.0/24)
- No external internet access required for operation
- Uses secure HTTP within private network

### Data Protection

**Sensitive Data Handling:**
- Test phrases are stored locally only
- No personal information transmitted
- Results contain no identifiable information
- Regular cleanup of old test data

**Environment Security:**
```bash
# In .env file
API_DEBUG=false                    # Disable debug in production
ENABLE_DETAILED_LOGGING=false     # Limit logging detail
```

---

## 📞 Support and Resources

### Technical Support

**Primary Support Channels:**
- **GitHub Issues:** https://github.com/The-Alphabet-Cartel/ash-thrash/issues
- **Discord:** #tech-support in https://discord.gg/alphabetcartel
- **Documentation:** This guide and README.md

**Emergency Contacts:**
- Technical Lead: [Contact information]
- System Administrator: [Contact information]
- Crisis Response Lead: [Contact information]

### Useful Resources

**Documentation:**
- **Main README:** Comprehensive technical overview
- **Team Guide:** User-focused operation guide
- **API Documentation:** Endpoint specifications
- **Docker Guide:** Container management details

**External Resources:**
- **Docker Documentation:** https://docs.docker.com/desktop/windows/
- **Python Documentation:** https://docs.python.org/3/
- **PowerShell Documentation:** https://docs.microsoft.com/powershell/

---

## 📝 Appendix

### File Structure Reference

```
ash-thrash/
├── .env                           # Environment configuration
├── .env.template                  # Environment template
├── docker-compose.yml             # Docker services definition
├── requirements.txt               # Python dependencies
├── requirements-dev.txt           # Development dependencies
├── pytest.ini                     # Test configuration
├── .gitignore                     # Git ignore rules
├── setup.sh                       # Linux setup script
│
├── src/                           # Application source code
│   ├── comprehensive_testing.py   # Main 350-phrase test
│   ├── quick_validation.py        # Quick 10-phrase test
│   ├── api/                      # API server code
│   ├── test_data/                # Test phrase definitions
│   └── utils/                    # Utility functions
│
├── results/                       # Test results storage
│   ├── comprehensive/            # Full test results
│   ├── quick_validation/          # Quick test results
│   ├── reports/                  # Generated reports
│   └── backups/                  # Archived data
│
├── config/                        # Configuration files
│   ├── testing_goals.json        # Target success rates
│   └── categories.json           # Test category definitions
│
├── docs/                          # Documentation
│   ├── TEAM_GUIDE.md             # Team member guide
│   ├── IMPLEMENTATION_GUIDE.md   # This guide
│   ├── API.md                    # API documentation
│   └── TROUBLESHOOTING.md        # Common issues
│
├── dashboard/                     # Ash-dash integration
│   ├── routes.js                 # API routes
│   ├── styles/                   # CSS styles
│   └── templates/                # HTML templates
│
├── docker/                        # Docker configuration
│   ├── Dockerfile                # Main application container
│   ├── Dockerfile.api            # API server container
│   └── entrypoint.sh             # Container startup script
│
├── scripts/                       # Utility scripts
│   ├── backup_results.ps1        # Windows backup script
│   ├── monitor_health.ps1        # Health monitoring
│   └── generate_report.py        # Report generation
│
└── tests/                         # Test framework
    ├── test_api.py               # API tests
    ├── test_testing.py           # Testing framework tests
    └── conftest.py               # Test configuration
```

### Environment Variables Reference

```bash
# Core Settings
NLP_SERVER_HOST=10.20.30.16        # NLP server IP
NLP_SERVER_PORT=8881                # NLP server port
NLP_SERVER_URL=http://10.20.30.16:8881  # Full NLP URL

# Performance Settings
MAX_CONCURRENT_TESTS=8              # Parallel test count
TEST_TIMEOUT_SECONDS=15             # Per-test timeout
RESULTS_RETENTION_DAYS=90           # Result storage time

# API Settings
API_PORT=8884                       # API server port
API_HOST=0.0.0.0                   # API bind address
API_DEBUG=false                     # Debug mode

# Scheduling
ENABLE_SCHEDULED_TESTING=true       # Auto-run tests
COMPREHENSIVE_TEST_SCHEDULE=0 */6 * * *  # Cron schedule
QUICK_VALIDATION_SCHEDULE=0 * * * *      # Cron schedule

# Integration
ENABLE_DASHBOARD_INTEGRATION=true   # Ash-dash integration
DASHBOARD_API_URL=http://localhost:8883  # Dashboard URL

# Logging
LOG_LEVEL=INFO                      # Logging verbosity
ENABLE_DETAILED_LOGGING=true        # Detailed logs
```

---

*Built with 🖤 for The Alphabet Cartel community*

**Implementation Guide v1.0**  
Last updated: July 26, 2025