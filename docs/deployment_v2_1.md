# 🚀 Ash-Thrash Deployment Guide

> **Complete Production and Development Deployment Instructions**

**Repository:** https://github.com/The-Alphabet-Cartel/ash-thrash  
**Discord:** https://discord.gg/alphabetcartel  
**Target Environment:** Windows 11 with Docker (10.20.30.16)  
**Last Updated:** July 26, 2025

---

## 📋 Deployment Overview

Ash-Thrash supports multiple deployment scenarios tailored to different environments and use cases. This guide covers production deployment on your Windows 11 server, development setups, and various configuration options.

### Deployment Scenarios

1. **Production Deployment** - Full automated testing on Windows 11 server
2. **Development Environment** - Local testing and development setup
3. **Hybrid Deployment** - Mixed local/remote development
4. **CI/CD Integration** - Automated testing in pipelines
5. **Multi-Environment** - Testing across dev/staging/production

---

## 🎯 Production Deployment (Windows 11 Server)

### System Specifications

**Your Current Setup:**
- **Server:** Windows 11 (10.20.30.16) ✅
- **CPU:** AMD Ryzen 7 7700X ✅
- **RAM:** 64GB ✅
- **GPU:** NVIDIA RTX 3050 (for NLP server) ✅
- **Docker:** Docker Desktop for Windows ✅

### Pre-Deployment Checklist

**Required Services:**
- [ ] Ash NLP Server running on 10.20.30.16:8881
- [ ] Ash-Dash Dashboard accessible (optional integration)
- [ ] Docker Desktop installed and running
- [ ] GitHub access configured
- [ ] Network ports 8884 available

**Network Requirements:**
- [ ] Internal network connectivity (10.20.30.0/24)
- [ ] Port 8884 accessible for API
- [ ] Port 8881 accessible to reach NLP server
- [ ] DNS resolution working

### Step 1: System Preparation

**Update Windows and Docker:**
```powershell
# Update Windows (run as Administrator)
Install-Module PSWindowsUpdate
Get-WUInstall -AcceptAll -AutoReboot

# Update Docker Desktop
# Download latest from https://www.docker.com/products/docker-desktop
```

**Configure Windows Features:**
```powershell
# Enable required Windows features (run as Administrator)
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux

# Restart if required
Restart-Computer
```

**Create Deployment Directory:**
```powershell
# Create production directory
New-Item -ItemType Directory -Path "C:\Production\ash-thrash" -Force
Set-Location "C:\Production\ash-thrash"

# Set appropriate permissions
icacls "C:\Production\ash-thrash" /grant Everyone:F /T
```

### Step 2: Repository Setup

**Clone Production Repository:**
```powershell
# Clone repository (using GitHub CLI or HTTPS)
gh repo clone The-Alphabet-Cartel/ash-thrash .

# OR using HTTPS
git clone https://github.com/The-Alphabet-Cartel/ash-thrash.git .

# Switch to main branch
git checkout main
git pull origin main
```

**Verify Repository Structure:**
```powershell
# Check required files exist
Test-Path docker-compose.yml
Test-Path .env.template
Test-Path src/comprehensive_testing.py
Test-Path setup.sh

# List directory structure
Get-ChildItem -Recurse -Directory | Select-Object Name, FullName
```

### Step 3: Environment Configuration

**Create Production Environment File:**
```powershell
# Copy template
Copy-Item .env.template .env

# Edit with production values (use Atom or notepad)
notepad .env
```

**Production .env Configuration:**
```bash
# Production Configuration for Ash-Thrash
# Server: 10.20.30.16 (Windows 11)

# =============================================================================
# NLP Server Configuration
# =============================================================================
NLP_SERVER_HOST=10.20.30.16
NLP_SERVER_PORT=8881
NLP_SERVER_URL=http://10.20.30.16:8881
NLP_SERVER_TIMEOUT=30
NLP_CONNECTION_RETRIES=3

# =============================================================================
# Performance Settings (Optimized for Ryzen 7 7700X)
# =============================================================================
MAX_CONCURRENT_TESTS=8              # Utilize multiple cores
TEST_TIMEOUT_SECONDS=15             # Conservative timeout
RESULTS_RETENTION_DAYS=180          # Extended retention
ENABLE_DETAILED_LOGGING=true        # Comprehensive logging

# =============================================================================
# API Server Configuration
# =============================================================================
API_PORT=8884
API_HOST=0.0.0.0
API_DEBUG=false
API_WORKERS=4

# =============================================================================
# Production Scheduling
# =============================================================================
ENABLE_SCHEDULED_TESTING=true
COMPREHENSIVE_TEST_SCHEDULE=0 */6 * * *     # Every 6 hours
QUICK_VALIDATION_SCHEDULE=0 * * * *         # Every hour

# =============================================================================
# Dashboard Integration
# =============================================================================
ENABLE_DASHBOARD_INTEGRATION=true
DASHBOARD_API_URL=http://10.20.30.16:8883
DASHBOARD_UPDATE_INTERVAL=300               # 5 minutes

# =============================================================================
# Database Configuration (Optional)
# =============================================================================
ENABLE_DATABASE=false
DATABASE_URL=postgresql://ash_test:secure_password@localhost:5432/ash_testing
DATABASE_POOL_SIZE=10
DATABASE_TIMEOUT=30

# =============================================================================
# Monitoring and Alerts
# =============================================================================
ENABLE_ALERTS=true
ALERT_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
CRITICAL_FAILURE_THRESHOLD=95              # Alert if high priority < 95%
FALSE_POSITIVE_THRESHOLD=10                # Alert if false positive > 10%

# =============================================================================
# Security Settings
# =============================================================================
ENABLE_API_RATE_LIMITING=true
API_RATE_LIMIT=100                          # Requests per minute
ALLOWED_HOSTS=10.20.30.0/24                # Restrict to internal network

# =============================================================================
# Backup and Recovery
# =============================================================================
ENABLE_AUTO_BACKUP=true
BACKUP_SCHEDULE=0 2 * * *                  # Daily at 2 AM
BACKUP_RETENTION_DAYS=30
BACKUP_LOCATION=C:\Backups\ash-thrash
```

### Step 4: Network and Security Configuration

**Configure Windows Firewall:**
```powershell
# Allow ash-thrash API (run as Administrator)
New-NetFirewallRule -DisplayName "Ash-Thrash API" -Direction Inbound -Port 8884 -Protocol TCP -Action Allow -LocalAddress 10.20.30.0/24

# Allow access to NLP server
New-NetFirewallRule -DisplayName "Ash-NLP Access" -Direction Outbound -Port 8881 -Protocol TCP -Action Allow -RemoteAddress 10.20.30.16

# Verify rules
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*ash*"} | Format-Table DisplayName, Direction, Action
```

**Test Network Connectivity:**
```powershell
# Test NLP server connectivity
Test-NetConnection -ComputerName 10.20.30.16 -Port 8881

# Test port availability
$port = 8884
$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $port)
try {
    $listener.Start()
    Write-Host "Port $port is available" -ForegroundColor Green
    $listener.Stop()
} catch {
    Write-Host "Port $port is in use" -ForegroundColor Red
}
```

### Step 5: Docker Configuration

**Configure Docker Resources:**
```powershell
# Open Docker Desktop settings programmatically
Start-Process "dockerdesktop://settings"

# Alternatively, configure via CLI
```

**Recommended Docker Settings:**
- **Memory:** 16GB (25% of total RAM)
- **CPUs:** 6 cores (75% of total cores)
- **Disk:** 100GB
- **Swap:** 4GB

**Create Production Docker Compose Override:**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  ash-thrash:
    deploy:
      resources:
        limits:
          memory: 8G
          cpus: '4.0'
        reservations:
          memory: 4G
          cpus: '2.0'
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8884/health"]
      interval: 60s
      timeout: 10s
      retries: 3
      start_period: 30s

  ash-thrash-api:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8884/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 15s

  # Optional: Database for production
  ash-thrash-db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ash_testing
      POSTGRES_USER: ash_test
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
    volumes:
      - ash_thrash_prod_data:/var/lib/postgresql/data
    restart: unless-stopped
    profiles:
      - database

volumes:
  ash_thrash_prod_data:
    driver: local
```

### Step 6: Initial Deployment

**Build and Start Services:**
```powershell
# Pull latest images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull

# Build services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache

# Start services in production mode
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify services are running
docker-compose ps
```

**Initial Health Checks:**
```powershell
# Wait for services to start
Start-Sleep -Seconds 30

# Check API health
$response = Invoke-RestMethod -Uri "http://localhost:8884/health" -Method GET
Write-Host "API Health: $($response.status)" -ForegroundColor Green

# Check NLP server connectivity
$response = Invoke-RestMethod -Uri "http://localhost:8884/api/test/status" -Method GET
Write-Host "NLP Connectivity: OK" -ForegroundColor Green

# Verify Docker containers
docker-compose logs --tail=20 ash-thrash-api
```

### Step 7: Production Validation

**Run Initial Tests:**
```powershell
# Run quick validation test
docker-compose exec ash-thrash python src/quick_validation.py

# Run comprehensive test
docker-compose exec ash-thrash python src/comprehensive_testing.py

# Check results
Get-ChildItem -Path "results\comprehensive" | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content | ConvertFrom-Json
```

**Verify Scheduled Tasks:**
```powershell
# Check if scheduled tests are enabled
docker-compose exec ash-thrash env | Select-String "SCHEDULE"

# Monitor logs for scheduled execution
docker-compose logs -f ash-thrash | Select-String "schedule"
```

### Step 8: Monitoring Setup

**Create Health Check Script:**
```powershell
# Save as C:\Scripts\ash-thrash-health.ps1
param(
    [string]$LogPath = "C:\Logs\ash-thrash-health.log"
)

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Ensure log directory exists
$logDir = Split-Path $LogPath -Parent
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force
}

function Write-HealthLog {
    param($Message, $Level = "INFO")
    $logEntry = "$timestamp [$Level] $Message"
    $logEntry | Out-File -FilePath $LogPath -Append
    
    switch ($Level) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "WARN"  { Write-Host $logEntry -ForegroundColor Yellow }
        default { Write-Host $logEntry -ForegroundColor Green }
    }
}

try {
    # Check API health
    $apiHealth = Invoke-RestMethod -Uri "http://localhost:8884/health" -TimeoutSec 10
    if ($apiHealth.status -eq "healthy") {
        Write-HealthLog "API Health: OK"
    } else {
        Write-HealthLog "API Health: $($apiHealth.status)" "WARN"
    }
    
    # Check latest test results
    $testStatus = Invoke-RestMethod -Uri "http://localhost:8884/api/test/status" -TimeoutSec 10
    $passRate = $testStatus.last_test.pass_rate
    
    if ($passRate -ge 85) {
        Write-HealthLog "Pass Rate: $passRate% (Good)"
    } elseif ($passRate -ge 75) {
        Write-HealthLog "Pass Rate: $passRate% (Warning)" "WARN"
    } else {
        Write-HealthLog "Pass Rate: $passRate% (Critical)" "ERROR"
    }
    
    # Check high priority detection
    $highPriorityStatus = Invoke-RestMethod -Uri "http://localhost:8884/api/test/results/latest" -TimeoutSec 10
    $highPriorityRate = $highPriorityStatus.category_results.definite_high.pass_rate
    
    if ($highPriorityRate -lt 95) {
        Write-HealthLog "CRITICAL: High Priority Detection at $highPriorityRate%" "ERROR"
        
        # Send Discord alert if webhook configured
        if ($env:ALERT_WEBHOOK_URL) {
            $alertPayload = @{
                content = "🚨 **CRITICAL ALERT** 🚨`nHigh Priority Crisis Detection: $highPriorityRate%`nTarget: 100%`nServer: 10.20.30.16"
            } | ConvertTo-Json
            
            Invoke-RestMethod -Uri $env:ALERT_WEBHOOK_URL -Method Post -Body $alertPayload -ContentType "application/json"
        }
    } else {
        Write-HealthLog "High Priority Detection: $highPriorityRate% (OK)"
    }
    
} catch {
    Write-HealthLog "Health check failed: $($_.Exception.Message)" "ERROR"
}
```

**Schedule Health Monitoring:**
```powershell
# Create scheduled task for health monitoring
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\Scripts\ash-thrash-health.ps1"
$trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 5) -Once -At (Get-Date)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "Ash-Thrash Health Monitor" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force
```

---

## 💻 Development Environment Setup

### Local Development on Windows

**Prerequisites:**
- Python 3.11+
- Git
- Atom editor (your preference)
- Docker Desktop (optional for local testing)

**Setup Steps:**
```powershell
# Create development directory
New-Item -ItemType Directory -Path "C:\Dev\ash-thrash" -Force
Set-Location "C:\Dev\ash-thrash"

# Clone repository for development
git clone https://github.com/The-Alphabet-Cartel/ash-thrash.git .

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Copy environment template
Copy-Item .env.template .env.dev

# Edit development environment
atom .env.dev
```

**Development .env Configuration:**
```bash
# Development Configuration
NLP_SERVER_URL=http://10.20.30.16:8881    # Point to production NLP server
MAX_CONCURRENT_TESTS=3                     # Lower for development
TEST_TIMEOUT_SECONDS=20                    # Higher timeout for debugging
ENABLE_DETAILED_LOGGING=true               # Verbose logging
API_DEBUG=true                             # Enable debug mode
RESULTS_RETENTION_DAYS=7                   # Shorter retention
ENABLE_SCHEDULED_TESTING=false             # Disable for development
```

**Run Development Environment:**
```powershell
# Activate virtual environment
venv\Scripts\activate

# Run tests locally
python src/quick_validation.py
python src/comprehensive_testing.py --dry-run

# Start development API server
python -m flask --app src.api.app run --debug --port 8884

# Run with environment file
python -m python-dotenv -f .env.dev src/comprehensive_testing.py
```

### Development with Docker

**Development Docker Compose:**
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  ash-thrash-dev:
    build:
      context: .
      dockerfile: docker/Dockerfile.dev
    volumes:
      - .:/app
      - ./results:/app/results
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    ports:
      - "8884:8884"
    command: python -m flask --app src.api.app run --debug --host 0.0.0.0 --port 8884
```

**Development Commands:**
```powershell
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Run tests in development container
docker-compose -f docker-compose.dev.yml exec ash-thrash-dev python src/quick_validation.py

# Access development container shell
docker-compose -f docker-compose.dev.yml exec ash-thrash-dev bash

# View development logs
docker-compose -f docker-compose.dev.yml logs -f ash-thrash-dev
```

---

## 🔄 CI/CD Integration

### GitHub Actions Deployment

**Create Deployment Workflow:**
```yaml
# .github/workflows/deploy-production.yml
name: Deploy Ash-Thrash to Production

on:
  push:
    branches: [main]
    tags: ['v*']
  workflow_dispatch:

jobs:
  deploy:
    runs-on: self-hosted  # Your Windows server
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Stop existing services
      run: |
        cd C:\Production\ash-thrash
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
        
    - name: Backup current deployment
      run: |
        $timestamp = Get-Date -Format "yyyyMMdd-HHmm"
        Compress-Archive -Path "C:\Production\ash-thrash" -DestinationPath "C:\Backups\ash-thrash-$timestamp.zip"
        
    - name: Update deployment files
      run: |
        Copy-Item -Path $env:GITHUB_WORKSPACE\* -Destination C:\Production\ash-thrash\ -Recurse -Force
        
    - name: Deploy updated services
      run: |
        cd C:\Production\ash-thrash
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
        
    - name: Health check
      run: |
        Start-Sleep -Seconds 30
        $response = Invoke-RestMethod -Uri "http://localhost:8884/health"
        if ($response.status -ne "healthy") {
          throw "Health check failed: $($response.status)"
        }
        
    - name: Run validation test
      run: |
        cd C:\Production\ash-thrash
        docker-compose exec ash-thrash python src/quick_validation.py
        
    - name: Notify Discord
      if: always()
      run: |
        $status = if ($env:GITHUB_JOB_STATUS -eq "success") { "✅ SUCCESS" } else { "❌ FAILED" }
        $payload = @{
          content = "🚀 **Ash-Thrash Deployment** $status`nCommit: $env:GITHUB_SHA`nBranch: $env:GITHUB_REF_NAME"
        } | ConvertTo-Json
        Invoke-RestMethod -Uri $env:DISCORD_WEBHOOK -Method Post -Body $payload -ContentType "application/json"
      env:
        DISCORD_WEBHOOK: ${{ secrets.DISCORD_WEBHOOK_URL }}
        GITHUB_JOB_STATUS: ${{ job.status }}
```

### Automated Testing Pipeline

**Create Testing Workflow:**
```yaml
# .github/workflows/testing.yml
name: Automated Crisis Detection Testing

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  comprehensive-test:
    runs-on: self-hosted
    
    steps:
    - name: Run comprehensive test
      run: |
        cd C:\Production\ash-thrash
        docker-compose exec ash-thrash python src/comprehensive_testing.py --json-output
        
    - name: Analyze results
      run: |
        $results = Get-Content "results\comprehensive\latest.json" | ConvertFrom-Json
        $passRate = $results.summary.pass_rate
        $highPriorityRate = $results.category_results.definite_high.pass_rate
        
        if ($highPriorityRate -lt 95) {
          $alert = "🚨 **CRITICAL ALERT**`nHigh Priority Detection: $highPriorityRate%`nOverall Pass Rate: $passRate%"
          # Send Discord alert
        } elseif ($passRate -lt 80) {
          $alert = "⚠️ **WARNING**`nOverall Pass Rate: $passRate%`nHigh Priority: $highPriorityRate%"
          # Send Discord warning
        }
        
    - name: Upload test results
      uses: actions/upload-artifact@v3
      with:
        name: test-results-${{ github.run_number }}
        path: results/comprehensive/
        retention-days: 30
```

---

## 🌐 Multi-Environment Deployment

### Environment-Specific Configurations

**Development Environment:**
```bash
# .env.development
NLP_SERVER_URL=http://dev-nlp:8881
MAX_CONCURRENT_TESTS=2
ENABLE_SCHEDULED_TESTING=false
API_DEBUG=true
RESULTS_RETENTION_DAYS=7
```

**Staging Environment:**
```bash
# .env.staging
NLP_SERVER_URL=http://staging-nlp:8881
MAX_CONCURRENT_TESTS=4
ENABLE_SCHEDULED_TESTING=true
COMPREHENSIVE_TEST_SCHEDULE=0 */12 * * *
API_DEBUG=false
RESULTS_RETENTION_DAYS=30
```

**Production Environment:**
```bash
# .env.production
NLP_SERVER_URL=http://10.20.30.16:8881
MAX_CONCURRENT_TESTS=8
ENABLE_SCHEDULED_TESTING=true
COMPREHENSIVE_TEST_SCHEDULE=0 */6 * * *
API_DEBUG=false
RESULTS_RETENTION_DAYS=180
ENABLE_ALERTS=true
```

### Environment Deployment Script

**Deploy to Specific Environment:**
```powershell
# deploy-environment.ps1
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("development", "staging", "production")]
    [string]$Environment,
    
    [string]$GitBranch = "main"
)

$deployPath = "C:\Deployments\ash-thrash-$Environment"
$envFile = ".env.$Environment"

Write-Host "🚀 Deploying Ash-Thrash to $Environment environment" -ForegroundColor Blue

# Create deployment directory
New-Item -ItemType Directory -Path $deployPath -Force
Set-Location $deployPath

# Clone or update repository
if (Test-Path ".git") {
    git fetch origin
    git checkout $GitBranch
    git pull origin $GitBranch
} else {
    git clone https://github.com/The-Alphabet-Cartel/ash-thrash.git .
    git checkout $GitBranch
}

# Copy environment-specific configuration
if (Test-Path $envFile) {
    Copy-Item $envFile .env
} else {
    Write-Error "Environment file $envFile not found!"
    exit 1
}

# Deploy with Docker
$composeFiles = @("docker-compose.yml")
if (Test-Path "docker-compose.$Environment.yml") {
    $composeFiles += "docker-compose.$Environment.yml"
}

$composeArgs = $composeFiles | ForEach-Object { "-f", $_ }

& docker-compose @composeArgs down
& docker-compose @composeArgs pull
& docker-compose @composeArgs up -d --build

# Health check
Start-Sleep -Seconds 30
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8884/health"
    if ($health.status -eq "healthy") {
        Write-Host "✅ Deployment successful! Health check passed." -ForegroundColor Green
    } else {
        Write-Host "⚠️ Deployment completed but health check shows: $($health.status)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "🎯 Environment: $Environment" -ForegroundColor Blue
Write-Host "📍 API: http://localhost:8884" -ForegroundColor Blue
Write-Host "📊 Status: http://localhost:8884/api/test/status" -ForegroundColor Blue
```

---

## 🔧 Advanced Configuration

### Load Balancing (Future Expansion)

**Nginx Configuration for Multiple Instances:**
```nginx
# nginx.conf
upstream ash_thrash_api {
    server 10.20.30.16:8884;
    server 10.20.30.17:8884;  # Future second instance
    server 10.20.30.18:8884;  # Future third instance
}

server {
    listen 80;
    server_name ash-thrash.local;
    
    location / {
        proxy_pass http://ash_thrash_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /health {
        proxy_pass http://ash_thrash_api/health;
        access_log off;
    }
}
```

### Database Configuration (PostgreSQL)

**Production Database Setup:**
```yaml
# docker-compose.db.yml
version: '3.8'

services:
  ash-thrash-db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ash_testing
      POSTGRES_USER: ash_test
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
    volumes:
      - ash_thrash_db_data:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
      - ./sql/migrations:/docker-entrypoint-initdb.d/migrations
    ports:
      - "5433:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ash_test"]
      interval: 30s
      timeout: 10s
      retries: 5

volumes:
  ash_thrash_db_data:
    driver: local
```

**Database Initialization Script:**
```sql
-- sql/init.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Test results table
CREATE TABLE test_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_id VARCHAR(255) NOT NULL,
    test_type VARCHAR(50) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    total_phrases INTEGER NOT NULL,
    passed INTEGER NOT NULL DEFAULT 0,
    failed INTEGER NOT NULL DEFAULT 0,
    pass_rate DECIMAL(5,2),
    avg_response_time DECIMAL(8,3),
    goals_met INTEGER DEFAULT 0,
    total_goals INTEGER DEFAULT 7,
    results_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Test failures table
CREATE TABLE test_failures (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_result_id UUID REFERENCES test_results(id),
    phrase TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    expected_priority VARCHAR(20) NOT NULL,
    detected_priority VARCHAR(20) NOT NULL,
    confidence DECIMAL(5,3),
    response_time DECIMAL(8,3),
    failure_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_test_results_test_type ON test_results(test_type);
CREATE INDEX idx_test_results_started_at ON test_results(started_at);
CREATE INDEX idx_test_failures_category ON test_failures(category);
CREATE INDEX idx_test_failures_failure_type ON test_failures(failure_type);

-- Views for analytics
CREATE VIEW test_summary AS
SELECT 
    DATE(started_at) as test_date,
    test_type,
    COUNT(*) as total_tests,
    AVG(pass_rate) as avg_pass_rate,
    AVG(avg_response_time) as avg_response_time,
    SUM(CASE WHEN goals_met = total_goals THEN 1 ELSE 0 END) as tests_meeting_all_goals
FROM test_results 
WHERE completed_at IS NOT NULL
GROUP BY DATE(started_at), test_type;
```

---

## 📊 Monitoring and Maintenance

### Automated Backup System

**Create Backup Script:**
```powershell
# backup-ash-thrash.ps1
param(
    [string]$BackupPath = "C:\Backups\ash-thrash",
    [int]$RetentionDays = 30
)

$timestamp = Get-Date -Format "yyyyMMdd-HHmm"
$backupFile = "$BackupPath\ash-thrash-backup-$timestamp.zip"

# Ensure backup directory exists
New-Item -ItemType Directory -Path $BackupPath -Force

# Create backup
Compress-Archive -Path "C:\Production\ash-thrash" -DestinationPath $backupFile

# Backup results separately (larger files)
$resultsBackup = "$BackupPath\ash-thrash-results-$timestamp.zip"
Compress-Archive -Path "C:\Production\ash-thrash\results" -DestinationPath $resultsBackup

# Clean old backups
Get-ChildItem $BackupPath -Filter "*.zip" | Where-Object {
    $_.LastWriteTime -lt (Get-Date).AddDays(-$RetentionDays)
} | Remove-Item -Force

Write-Host "✅ Backup completed: $backupFile" -ForegroundColor Green
Write-Host "✅ Results backup: $resultsBackup" -ForegroundColor Green
```

**Schedule Automated Backups:**
```powershell
# Create scheduled backup task
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\Scripts\backup-ash-thrash.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At "2:00 AM"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "Ash-Thrash Daily Backup" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force
```

### Performance Monitoring

**Resource Monitoring Script:**
```powershell
# monitor-performance.ps1
$logPath = "C:\Logs\ash-thrash-performance.log"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# CPU Usage
$cpu = Get-Counter "\Processor(_Total)\% Processor Time" -SampleInterval 1 -MaxSamples 3 | 
    Select-Object -ExpandProperty CounterSamples | 
    Measure-Object -Property CookedValue -Average | 
    Select-Object -ExpandProperty Average

# Memory Usage
$memory = Get-Counter "\Memory\Available MBytes" -SampleInterval 1 -MaxSamples 1 | 
    Select-Object -ExpandProperty CounterSamples | 
    Select-Object -ExpandProperty CookedValue

$totalMemory = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1MB
$usedMemory = $totalMemory - $memory
$memoryPercent = ($usedMemory / $totalMemory) * 100

# Docker container stats
$dockerStats = docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | 
    Where-Object { $_ -like "*ash-thrash*" }

# Log performance data
$performanceData = @{
    timestamp = $timestamp
    cpu_percent = [math]::Round($cpu, 2)
    memory_percent = [math]::Round($memoryPercent, 2)
    memory_available_mb = [math]::Round($memory, 0)
    docker_containers = $dockerStats
}

$performanceData | ConvertTo-Json | Out-File -FilePath $logPath -Append

# Alert if resources are high
if ($cpu -gt 80 -or $memoryPercent -gt 90) {
    $alertMessage = "⚠️ **High Resource Usage**`nCPU: $([math]::Round($cpu, 1))%`nMemory: $([math]::Round($memoryPercent, 1))%"
    
    if ($env:ALERT_WEBHOOK_URL) {
        $payload = @{ content = $alertMessage } | ConvertTo-Json
        Invoke-RestMethod -Uri $env:ALERT_WEBHOOK_URL -Method Post -Body $payload -ContentType "application/json"
    }
}
```

---

## 🔄 Update and Maintenance Procedures

### Rolling Updates

**Zero-Downtime Update Script:**
```powershell
# rolling-update.ps1
param(
    [string]$GitTag = "latest"
)

$deployPath = "C:\Production\ash-thrash"
Set-Location $deployPath

Write-Host "🔄 Starting rolling update to $GitTag" -ForegroundColor Blue

# Backup current state
$timestamp = Get-Date -Format "yyyyMMdd-HHmm"
Compress-Archive -Path $deployPath -DestinationPath "C:\Backups\pre-update-$timestamp.zip"

# Pull latest changes
git fetch --tags
if ($GitTag -ne "latest") {
    git checkout $GitTag
} else {
    git checkout main
    git pull origin main
}

# Update images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull

# Rolling update strategy - update API first, then main service
Write-Host "📡 Updating API service..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps ash-thrash-api

# Wait and verify API
Start-Sleep -Seconds 20
$apiHealth = Invoke-RestMethod -Uri "http://localhost:8884/health"
if ($apiHealth.status -ne "healthy") {
    Write-Host "❌ API health check failed, rolling back..." -ForegroundColor Red
    # Rollback logic here
    exit 1
}

Write-Host "🧪 Updating main testing service..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps ash-thrash

# Final health check
Start-Sleep -Seconds 30
$finalHealth = Invoke-RestMethod -Uri "http://localhost:8884/api/test/status"

Write-Host "✅ Rolling update completed successfully!" -ForegroundColor Green
Write-Host "📊 System Status: $($finalHealth.status)" -ForegroundColor Blue
```

### Disaster Recovery

**Complete System Recovery Procedure:**
```powershell
# disaster-recovery.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$BackupFile
)

Write-Host "🚨 Starting disaster recovery from $BackupFile" -ForegroundColor Red

# Stop all services
docker-compose -f C:\Production\ash-thrash\docker-compose.yml -f C:\Production\ash-thrash\docker-compose.prod.yml down

# Remove existing deployment
Remove-Item "C:\Production\ash-thrash" -Recurse -Force

# Restore from backup
Expand-Archive -Path $BackupFile -DestinationPath "C:\Production"

# Restart services
Set-Location "C:\Production\ash-thrash"
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Wait for services to start
Start-Sleep -Seconds 60

# Verify recovery
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8884/health"
    if ($health.status -eq "healthy") {
        Write-Host "✅ Disaster recovery successful!" -ForegroundColor Green
        
        # Run validation test
        docker-compose exec ash-thrash python src/quick_validation.py
        Write-Host "✅ Validation test passed!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Recovery completed but system not healthy: $($health.status)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Recovery failed: $($_.Exception.Message)" -ForegroundColor Red
}
```

---

## 📞 Support and Troubleshooting

### Deployment Validation Checklist

**Post-Deployment Verification:**
- [ ] API health endpoint returns "healthy"
- [ ] NLP server connectivity verified
- [ ] Quick validation test passes
- [ ] Comprehensive test completes successfully
- [ ] Dashboard integration working (if enabled)
- [ ] Scheduled tests configured correctly
- [ ] Monitoring and alerts functional
- [ ] Backup system operational

**Common Deployment Issues:**

1. **Port Conflicts:**
   ```powershell
   netstat -an | Select-String "8884"
   # Kill conflicting processes
   Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process
   ```

2. **Docker Issues:**
   ```powershell
   # Reset Docker if needed
   docker system prune -a
   Restart-Service com.docker.service
   ```

3. **Permission Problems:**
   ```powershell
   # Fix directory permissions
   icacls "C:\Production\ash-thrash" /grant Everyone:F /T
   ```

### Getting Help

**Support Channels:**
- **GitHub Issues:** https://github.com/The-Alphabet-Cartel/ash-thrash/issues
- **Discord:** #tech-support in https://discord.gg/alphabetcartel
- **Documentation:** Complete guides in `/docs` directory
- **Emergency:** Direct contact for critical production issues

**When Requesting Support:**
- Include deployment environment details
- Provide relevant logs from Docker containers
- Describe specific error messages
- Include system resource information
- Mention any recent changes or updates

---

*Built with 🖤 for The Alphabet Cartel community*

**Deployment Guide v2.1**  
Last updated: July 26, 2025