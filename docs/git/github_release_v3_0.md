# Ash-Thrash v3.0 GitHub Release Guide

**Repository**: https://github.com/the-alphabet-cartel/ash-thrash  
**Release**: v3.0.0 - Complete System Rewrite with Persistent Container Architecture  
**Document Location**: `docs/git/github_release_v3_0.md`  
**Release Date**: August 2025

---

## 🎉 Release Overview

Ash-Thrash v3.0 represents a **complete ground-up rewrite** of the crisis detection testing suite, transforming it from a bash-script-based system to a modern, enterprise-grade Python and Docker solution with **persistent container architecture** that eliminates orphan containers and provides instant test execution.

### Release Highlights

- **🔄 Complete Rewrite**: No legacy code carried over - built from scratch
- **🐍 Python-First**: Pure Python implementation with no external UI dependencies
- **🐳 Docker Native**: Full Docker Compose orchestration with persistent containers
- **📊 REST API**: Comprehensive API on port 8884 for integration
- **🧪 350 Test Phrases**: Curated across 7 crisis detection categories
- **🚀 Modern Stack**: FastAPI with lifespan events, no deprecation warnings
- **⚡ Instant Execution**: Persistent containers eliminate startup delays
- **🔧 Zero Orphans**: Clean container management with Docker Compose

---

## 📋 What's New in v3.0

### **Revolutionary Architecture Changes**

#### **1. Persistent Container Architecture**
- **Before**: `docker compose run` creating orphan containers
- **After**: `docker compose up -d` with persistent services + `docker compose exec` for execution
- **Benefit**: Zero orphan containers, instant test execution, clean lifecycle management

#### **2. Python-First Approach**
- **Before**: Bash scripts with limited functionality
- **After**: Pure Python CLI using standard library (argparse)
- **Benefit**: Better error handling, cross-platform compatibility, maintainable code

#### **3. Docker Compose Integration**
- **Before**: Manual container management
- **After**: Full orchestration with persistent services
- **Benefit**: Production-ready deployment, health monitoring, service discovery

#### **4. REST API Server**
- **Before**: No API capabilities
- **After**: Full FastAPI server on port 8884 with OpenAPI documentation (persistent)
- **Benefit**: Integration with ash-dash, automation, remote testing

#### **5. Comprehensive Testing Framework**
- **Before**: Basic keyword testing
- **After**: 350 phrases across 7 categories with bidirectional testing
- **Benefit**: Accurate NLP tuning, comprehensive coverage, goal-based validation

### **Major Feature Additions**

#### **🧪 Advanced Testing System with Persistent Containers**
```bash
# Start persistent services once
docker compose up -d

# Execute tests instantly (no container startup delays)
docker compose exec ash-thrash python cli.py test comprehensive
docker compose exec ash-thrash python cli.py test quick --sample-size 30
docker compose exec ash-thrash python cli.py test category definite_high

# Stop services when completely done
docker compose down
```

#### **📊 REST API Integration (Always Available)**
```bash
# API server runs persistently
curl http://localhost:8884/health               # Always available
curl -X POST http://localhost:8884/api/test/trigger  # Instant response
```

#### **🔧 NLP Tuning Suggestions**
```
🔧 TUNING SUGGESTIONS:
🚨 HIGH PRIORITY: definite_high only 85.0% (need 100.0%). 
   Consider lowering NLP_HIGH_CRISIS_THRESHOLD from 0.8 to 0.7
```

#### **📱 Discord Integration**
- Rich embed notifications with test results
- Configurable webhook integration
- Real-time test completion alerts

### **Development Experience Improvements**

#### **🐍 Simplified Command Structure**
```bash
# Management operations
docker compose up -d      # Start persistent services
docker compose ps         # Check service status
docker compose down       # Stop services

# Direct testing from persistent containers
docker compose exec ash-thrash python cli.py test comprehensive
docker compose exec ash-thrash python cli.py validate setup
```

#### **🐳 Container Simplification**
```bash
# Easy to remember commands with persistent containers
docker compose exec ash-thrash python cli.py test comprehensive
docker compose exec ash-thrash python cli.py validate setup

# No more orphan containers or cleanup needed
```

#### **⚡ Automated Building**
- GitHub workflow builds Docker images automatically
- Multi-tag strategy (latest, v3.0, commit-specific)
- Fast AMD64-only builds optimized for development

---

## 🚀 Migration from Previous Versions

### **Breaking Changes**

⚠️ **Complete API Change**: All previous bash scripts are replaced  
⚠️ **New Environment Variables**: Configuration format completely changed  
⚠️ **Docker Structure**: New persistent container architecture  
⚠️ **Testing Categories**: New 7-category system with bidirectional testing  
⚠️ **Command Structure**: `docker compose run` → `docker compose exec` pattern

### **Migration Steps**

#### **1. Backup Current Setup**
```bash
# Backup your current configuration
cp -r ash-thrash ash-thrash-backup-v2
```

#### **2. Clean Installation**
```bash
# Remove old version completely
cd ash-thrash
git checkout main
git pull origin main

# Clean slate approach recommended
rm -rf *  # Only if you're comfortable with complete replacement
```

#### **3. Fresh Setup with Persistent Containers**
```bash
# Follow new installation process
python main.py setup
# Edit .env with your configuration

# Start persistent services
docker compose up -d

# Verify installation
docker compose exec ash-thrash python cli.py validate setup
```

#### **4. Configuration Mapping**

| **Old Configuration** | **New Configuration** |
|----------------------|----------------------|
| `NLP_SERVER_URL` | `GLOBAL_NLP_API_URL` |
| `DISCORD_WEBHOOK` | `THRASH_DISCORD_WEBHOOK_URL` |
| `LOG_LEVEL` | `GLOBAL_LOG_LEVEL` |
| Bash script parameters | Environment variables in `.env` |
| `docker compose run --rm` | `docker compose exec` |

---

## 📦 Installation & Deployment

### **Quick Start (Docker - Recommended)**

```bash
# 1. Clone repository
git clone https://github.com/the-alphabet-cartel/ash-thrash.git
cd ash-thrash

# 2. Setup environment
python main.py setup

# 3. Configure settings
# Edit .env file with your NLP server URL and preferences

# 4. Start persistent services
docker compose up -d

# 5. Verify installation
docker compose ps
docker compose exec ash-thrash python cli.py validate setup
docker compose exec ash-thrash python cli.py test quick
```

### **Development Installation**

```bash
# 1. Local Python setup
pip install -r requirements.txt

# 2. Environment configuration
cp .env.template .env
# Edit .env with your settings

# 3. Validation
python cli.py validate setup

# 4. Run tests
python cli.py test comprehensive
```

### **Production Deployment**

#### **Using Pre-built Images with Persistent Architecture**
```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/the-alphabet-cartel/ash-thrash:v3.0

# Deploy with persistent containers
version: '3.8'
services:
  ash-thrash-api:
    image: ghcr.io/the-alphabet-cartel/ash-thrash:v3.0
    command: ["python", "-m", "uvicorn", "src.ash_thrash_api:app", "--host", "0.0.0.0", "--port", "8884"]
    restart: unless-stopped
    ports:
      - "8884:8884"

  ash-thrash:
    image: ghcr.io/the-alphabet-cartel/ash-thrash:v3.0
    command: ["tail", "-f", "/dev/null"]
    restart: unless-stopped
```

#### **Automated Deployment**
- GitHub workflow automatically builds on main branch pushes
- Images tagged as `latest`, `v3.0`, and commit-specific
- Ready for production use with health checks

---

## 🔧 Configuration Guide

### **Environment Variables (`.env`)**

```bash
# Core Configuration
GLOBAL_NLP_API_URL=http://10.20.30.253:8881
GLOBAL_THRASH_API_PORT=8884

# Discord Integration
THRASH_DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
DISCORD_NOTIFICATIONS_ENABLED=true

# Testing Configuration  
THRASH_MAX_CONCURRENT_TESTS=3
THRASH_QUICK_TEST_SAMPLE_SIZE=50

# Logging
GLOBAL_LOG_LEVEL=INFO
```

### **Docker Compose Configuration**

The included `docker-compose.yml` provides persistent container architecture:
- **ash-thrash-api**: Persistent API server (port 8884) with `uvicorn` command
- **ash-thrash**: Persistent CLI container with `tail -f /dev/null` command
- **Health checks**: Automatic dependency validation
- **Networking**: Integration with ash ecosystem (172.20.0.0/16)
- **Restart policy**: `unless-stopped` for automatic recovery

---

## 📊 Performance & Scaling

### **Performance Benchmarks with Persistent Containers**

| **Test Type** | **Duration** | **Startup Time** | **Memory** | **CPU** |
|---------------|-------------|------------------|------------|---------|
| Comprehensive (350 phrases) | ~3 minutes | **0 seconds** | 2GB | 1-2 cores |
| Quick Validation (50 phrases) | ~30 seconds | **0 seconds** | 1GB | 1 core |
| Category Test (50 phrases) | ~25 seconds | **0 seconds** | 1GB | 1 core |

### **Scaling Recommendations**

#### **Development Environment**
```bash
# Single persistent instance sufficient
docker compose up -d
docker compose exec ash-thrash python cli.py test comprehensive
```

#### **Production Environment**
```bash
# Scale API for high load while maintaining persistent containers
docker compose up -d --scale ash-thrash-api=3

# Load balancer configuration
# Configure nginx/traefik to distribute load
```

### **Resource Requirements**

- **Minimum**: 2GB RAM, 1 CPU core
- **Recommended**: 4GB RAM, 2 CPU cores  
- **High Load**: 8GB RAM, 4 CPU cores, multiple API instances
- **Persistent overhead**: ~500MB additional RAM for always-running containers

---

## 🧪 Testing Framework

### **Test Categories & Goals**

| **Category** | **Phrases** | **Target** | **Type** |
|-------------|-------------|------------|----------|
| `definite_high` | 50 | 100% | Suicidal ideation |
| `definite_medium` | 50 | 65% | Severe episodes |
| `definite_low` | 50 | 65% | Mild distress |
| `definite_none` | 50 | 95% | Normal conversation |
| `maybe_high_medium` | 50 | 90% | Bidirectional |
| `maybe_medium_low` | 50 | 80% | Bidirectional |
| `maybe_low_none` | 50 | 90% | Bidirectional |

### **Testing Modes with Persistent Containers**

```bash
# Start persistent services
docker compose up -d

# Comprehensive testing (all 350 phrases) - instant execution
docker compose exec ash-thrash python cli.py test comprehensive

# Quick validation (subset) - no startup delay
docker compose exec ash-thrash python cli.py test quick --sample-size 30

# Category-specific testing - immediate response
docker compose exec ash-thrash python cli.py test category definite_high

# API-triggered testing (persistent API server)
curl -X POST http://localhost:8884/api/test/trigger \
  -H "Content-Type: application/json" \
  -d '{"test_type": "comprehensive"}'
```

---

## 🔗 Integration Points

### **Ash Ecosystem Integration**

#### **Ash-NLP Integration**
- Uses identical API endpoints as ash-bot
- Same message preprocessing pipeline
- Validates real-world behavior
- **Persistent connection** for faster testing

#### **Ash-Dash Integration**
- REST API provides data for dashboard visualization (always available)
- Real-time test status and results
- Historical performance tracking
- **Zero downtime** integration with persistent API

#### **Ash-Bot Compatibility**
- Tests same detection logic used in production
- Validates tuning changes before deployment
- Ensures consistency across system

### **External Integrations**

#### **Discord Webhooks**
- Automated test completion notifications
- Rich embed formatting with results summary
- Configurable notification preferences

#### **GitHub Actions**
- Automated Docker image building
- Continuous integration testing
- Release automation

---

## 🔍 Monitoring & Observability

### **Health Monitoring with Persistent Containers**

```bash
# Service health checks (always available)
docker compose ps
docker compose exec ash-thrash python cli.py api health

# API health endpoint (persistent service)
curl http://localhost:8884/health

# Individual service logs
docker compose logs ash-thrash-api
docker compose logs ash-thrash
```

### **Performance Monitoring**

```bash
# Test execution metrics (instant access)
docker compose exec ash-thrash python cli.py results latest
curl http://localhost:8884/api/test/history    # Historical performance
curl http://localhost:8884/api/test/goals      # Goal achievement tracking
```

### **Alerting**

- Discord webhook notifications for test completions
- Health check failures logged with details
- API response time monitoring built-in
- **Persistent monitoring** without service interruption

---

## 🛠️ Development & Debugging

### **Development Workflow with Persistent Containers**

```bash
# 1. Start persistent development environment
docker compose up -d

# 2. Make code changes
# Edit src/ash_thrash_core.py or other files

# 3. Test changes immediately (no container rebuild needed)
docker compose exec ash-thrash python cli.py validate setup
docker compose exec ash-thrash python cli.py test quick

# 4. For API changes, restart API service
docker compose restart ash-thrash-api

# 5. Push changes (auto-builds via GitHub Actions)
git add .
git commit -m "feat: your changes"
git push origin main
```

### **Debugging Tools with Persistent Containers**

```bash
# Validate test data structure (instant access)
docker compose exec ash-thrash python cli.py validate data

# Check NLP server connectivity (no container startup delay)
docker compose exec ash-thrash python cli.py api health

# Debug API responses (persistent API server)
curl -X POST http://localhost:8884/api/test/trigger \
  -H "Content-Type: application/json" \
  -d '{"test_type": "quick"}' | jq '.'

# Access container shell for debugging
docker compose exec ash-thrash bash
docker compose exec ash-thrash-api bash
```

### **Log Analysis with Persistent Containers**

```bash
# View detailed application logs (real-time)
docker compose logs -f ash-thrash
docker compose logs -f ash-thrash-api

# Filter logs by level
docker compose logs ash-thrash | grep ERROR

# Export logs for analysis
docker compose logs ash-thrash > ash-thrash-logs.txt
```

---

## 📚 Documentation

### **Complete Documentation Suite**

- **[README.md](../README.md)** - Main project documentation (updated for persistent containers)
- **[API Documentation](../tech/api_v3_0.md)** - Complete REST API reference
- **[Team Guide](../team/team_guide_v3_0.md)** - Setup guide for team members (persistent workflow)
- **[Troubleshooting Guide](../troubleshooting_v3_0.md)** - Problem resolution (container-specific)
- **[Implementation Plan](../implementation_plan_recode_v3_0.md)** - Development roadmap

### **API Documentation**

- **OpenAPI Specification**: Available at `http://localhost:8884/docs` (always running)
- **Interactive Testing**: Built-in Swagger UI
- **Examples**: Comprehensive usage examples for all endpoints

---

## 🚨 Important Notes

### **Production Considerations**

1. **Security**: Configure CORS appropriately for production
2. **Performance**: Monitor NLP server response times  
3. **Scaling**: Use multiple API instances for high load
4. **Backup**: Regular backup of test results and configuration
5. **Resource Management**: Monitor persistent container resource usage

### **Breaking Changes from v2.x**

- **Complete rewrite**: No compatibility with previous versions
- **New command structure**: `docker compose run` → `docker compose exec`
- **Environment variables**: New configuration format
- **Docker structure**: Persistent container architecture
- **Container lifecycle**: Services remain running by default

### **Upgrade Path**

- **Recommended**: Fresh installation rather than upgrade
- **Configuration**: Manually migrate settings to new format
- **Testing**: Validate all functionality after migration
- **Training**: Team training on new persistent container workflow

---

## 🎯 Next Steps After Installation

### **1. Validate Installation with Persistent Containers**
```bash
docker compose up -d
docker compose ps
docker compose exec ash-thrash python cli.py validate setup
```

### **2. Run Initial Tests**
```bash
docker compose exec ash-thrash python cli.py test quick
docker compose exec ash-thrash python cli.py test comprehensive
```

### **3. Configure Integration**
```bash
# Set up Discord webhooks in .env
# Configure ash-dash to use port 8884
# Validate ash-nlp connectivity from persistent container
docker compose exec ash-thrash python cli.py api health
```

### **4. Production Deployment**
```bash
# Scale persistent services for production load
docker compose up -d --scale ash-thrash-api=3
# Configure monitoring and alerting
# Set up automated testing schedule
```

---

## 🆘 Support & Resources

### **Getting Help**

- **GitHub Issues**: [Report bugs and request features](https://github.com/the-alphabet-cartel/ash-thrash/issues)
- **Discord Community**: [Join our server](https://discord.gg/alphabetcartel)
- **Documentation**: [Complete documentation suite](../README.md)

### **Community Resources**

- **Examples**: [Usage examples repository](https://github.com/the-alphabet-cartel/ash-examples)
- **Best Practices**: [Team guide](../team/team_guide_v3_0.md)
- **Troubleshooting**: [Common issues and solutions](../troubleshooting_v3_0.md)

---

**Ash-Thrash v3.0 represents a quantum leap forward in crisis detection testing capabilities. This release provides enterprise-grade testing infrastructure with persistent container architecture that ensures the safety and accuracy of mental health crisis detection systems while eliminating container management overhead.**

**Key Innovation**: **Persistent Container Architecture** - Zero orphan containers, instant test execution, clean lifecycle management.

**Discord**: [https://discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)  
**Website**: [http://alphabetcartel.org](http://alphabetcartel.org)  
**Repository**: [https://github.com/the-alphabet-cartel/ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash)

*Revolutionizing crisis detection testing with persistent, always-ready infrastructure.* 🧪✨🐳