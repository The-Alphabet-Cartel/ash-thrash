# Ash-Thrash v3.0 GitHub Release Guide

**Repository**: https://github.com/the-alphabet-cartel/ash-thrash  
**Release**: v3.0.0 - Complete System Rewrite  
**Document Location**: `docs/git/github_release_v3_0.md`  
**Release Date**: August 2025

---

## 🎉 Release Overview

Ash-Thrash v3.0 represents a **complete ground-up rewrite** of the crisis detection testing suite, transforming it from a bash-script-based system to a modern, enterprise-grade Python and Docker solution.

### Release Highlights

- **🔄 Complete Rewrite**: No legacy code carried over - built from scratch
- **🐍 Python-First**: Pure Python implementation with no external UI dependencies
- **🐳 Docker Native**: Full Docker Compose orchestration and deployment
- **📊 REST API**: Comprehensive API on port 8884 for integration
- **🧪 350 Test Phrases**: Curated across 7 crisis detection categories
- **🚀 Modern Stack**: FastAPI with lifespan events, no deprecation warnings
- **⚡ Development Optimized**: Fast builds, streamlined development workflow

---

## 📋 What's New in v3.0

### **Revolutionary Architecture Changes**

#### **1. Python-First Approach**
- **Before**: Bash scripts with limited functionality
- **After**: Pure Python CLI using standard library (argparse)
- **Benefit**: Better error handling, cross-platform compatibility, maintainable code

#### **2. Docker Compose Integration**
- **Before**: Manual container management
- **After**: Full orchestration with `python main.py start/stop/status`
- **Benefit**: Production-ready deployment, health monitoring, service discovery

#### **3. REST API Server**
- **Before**: No API capabilities
- **After**: Full FastAPI server on port 8884 with OpenAPI documentation
- **Benefit**: Integration with ash-dash, automation, remote testing

#### **4. Comprehensive Testing Framework**
- **Before**: Basic keyword testing
- **After**: 350 phrases across 7 categories with bidirectional testing
- **Benefit**: Accurate NLP tuning, comprehensive coverage, goal-based validation

### **Major Feature Additions**

#### **🧪 Advanced Testing System**
```python
# Multiple test modes available
python cli.py test comprehensive          # Full 350 phrase test
python cli.py test quick --sample-size 30 # Quick validation  
python cli.py test category definite_high # Category-specific
```

#### **📊 REST API Integration**
```bash
# Full API for automation and integration
POST /api/test/trigger     # Start tests
GET /api/test/results/{id} # Get results
GET /health               # Health monitoring
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
python main.py setup      # Initial setup
python main.py start      # Start services  
python main.py status     # Check health

# Direct testing
python cli.py test comprehensive
python cli.py validate setup
```

#### **🐳 Container Simplification**
```bash
# Easy to remember container names
docker-compose run --rm ash-thrash test comprehensive
docker-compose run --rm ash-thrash validate setup
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
⚠️ **Docker Structure**: New container names and orchestration
⚠️ **Testing Categories**: New 7-category system with bidirectional testing

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

#### **3. Fresh Setup**
```bash
# Follow new installation process
python main.py setup
# Edit .env file with your configuration
python main.py start
```

#### **4. Configuration Mapping**

| **Old Configuration** | **New Configuration** |
|----------------------|----------------------|
| `NLP_SERVER_URL` | `GLOBAL_NLP_API_URL` |
| `DISCORD_WEBHOOK` | `THRASH_DISCORD_WEBHOOK_URL` |
| `LOG_LEVEL` | `GLOBAL_LOG_LEVEL` |
| Bash script parameters | Environment variables in `.env` |

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

# 4. Start services
python main.py start

# 5. Verify installation
python main.py status
python cli.py test quick
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

#### **Using Pre-built Images**
```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/the-alphabet-cartel/ash-thrash:v3.0

# Deploy with Docker Compose
version: '3.8'
services:
  ash-thrash-api:
    image: ghcr.io/the-alphabet-cartel/ash-thrash:v3.0
    ports:
      - "8884:8884"
    environment:
      - GLOBAL_NLP_API_URL=http://your-nlp-server:8881
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

The included `docker-compose.yml` provides:
- **ash-thrash-api**: Main API server (port 8884)
- **ash-thrash**: CLI container for on-demand testing
- **Health checks**: Automatic dependency validation
- **Networking**: Integration with ash ecosystem (172.20.0.0/16)

---

## 📊 Performance & Scaling

### **Performance Benchmarks**

| **Test Type** | **Duration** | **Memory** | **CPU** |
|---------------|-------------|------------|---------|
| Comprehensive (350 phrases) | ~3 minutes | 2GB | 1-2 cores |
| Quick Validation (50 phrases) | ~30 seconds | 1GB | 1 core |
| Category Test (50 phrases) | ~25 seconds | 1GB | 1 core |

### **Scaling Recommendations**

#### **Development Environment**
```bash
# Single instance sufficient
python main.py start
```

#### **Production Environment**
```bash
# Scale API for high load
docker-compose up -d --scale ash-thrash-api=3

# Load balancer configuration
# Configure nginx/traefik to distribute load
```

### **Resource Requirements**

- **Minimum**: 2GB RAM, 1 CPU core
- **Recommended**: 4GB RAM, 2 CPU cores
- **High Load**: 8GB RAM, 4 CPU cores, multiple API instances

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

### **Testing Modes**

```bash
# Comprehensive testing (all 350 phrases)
python cli.py test comprehensive

# Quick validation (subset)
python cli.py test quick --sample-size 30

# Category-specific testing
python cli.py test category definite_high

# API-triggered testing
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

#### **Ash-Dash Integration**
- REST API provides data for dashboard visualization
- Real-time test status and results
- Historical performance tracking

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

### **Health Monitoring**

```bash
# Service health checks
python main.py status

# API health endpoint
curl http://localhost:8884/health

# Individual service logs
python main.py logs --service ash-thrash-api --follow
```

### **Performance Monitoring**

```bash
# Test execution metrics
GET /api/test/history         # Historical performance
GET /api/test/goals          # Goal achievement tracking
GET /api/test/data           # Test data validation
```

### **Alerting**

- Discord webhook notifications for test completions
- Health check failures logged with details
- API response time monitoring built-in

---

## 🛠️ Development & Debugging

### **Development Workflow**

```bash
# 1. Make code changes
# Edit src/ash_thrash_core.py or other files

# 2. Validate changes
python cli.py validate setup

# 3. Test changes locally
python cli.py test quick

# 4. Test with Docker
python main.py build
python main.py start
python main.py test-all

# 5. Push changes (auto-builds via GitHub Actions)
git add .
git commit -m "feat: your changes"
git push origin main
```

### **Debugging Tools**

```bash
# Validate test data structure
python cli.py validate data

# Check NLP server connectivity
python cli.py api health --api-url http://your-nlp-server:8881

# Debug API responses
curl -X POST http://localhost:8884/api/test/trigger \
  -H "Content-Type: application/json" \
  -d '{"test_type": "quick"}' | jq '.'
```

### **Log Analysis**

```bash
# View detailed application logs
python main.py logs --follow

# Filter logs by level
python main.py logs | grep ERROR

# Export logs for analysis
python main.py logs > ash-thrash-logs.txt
```

---

## 📚 Documentation

### **Complete Documentation Suite**

- **[README.md](../README.md)** - Main project documentation
- **[API Documentation](../tech/api_v3_0.md)** - Complete REST API reference
- **[Team Guide](../team/team_guide_v3_0.md)** - Setup guide for team members
- **[Troubleshooting Guide](../troubleshooting_v3_0.md)** - Problem resolution
- **[Implementation Plan](../implementation_plan_recode.md)** - Development roadmap

### **API Documentation**

- **OpenAPI Specification**: Available at `http://localhost:8884/docs`
- **Interactive Testing**: Built-in Swagger UI
- **Examples**: Comprehensive usage examples for all endpoints

---

## 🚨 Important Notes

### **Production Considerations**

1. **Security**: Configure CORS appropriately for production
2. **Performance**: Monitor NLP server response times
3. **Scaling**: Use multiple API instances for high load
4. **Backup**: Regular backup of test results and configuration

### **Breaking Changes from v2.x**

- **Complete rewrite**: No compatibility with previous versions
- **New command structure**: All bash scripts replaced with Python
- **Environment variables**: New configuration format
- **Docker structure**: New container names and orchestration

### **Upgrade Path**

- **Recommended**: Fresh installation rather than upgrade
- **Configuration**: Manually migrate settings to new format
- **Testing**: Validate all functionality after migration

---

## 🎯 Next Steps After Installation

### **1. Validate Installation**
```bash
python cli.py validate setup
python main.py status
```

### **2. Run Initial Tests**
```bash
python cli.py test quick
python cli.py test comprehensive
```

### **3. Configure Integration**
```bash
# Set up Discord webhooks in .env
# Configure ash-dash to use port 8884
# Validate ash-nlp connectivity
```

### **4. Production Deployment**
```bash
# Scale for production load
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

**Ash-Thrash v3.0 represents a quantum leap forward in crisis detection testing capabilities. This release provides enterprise-grade testing infrastructure that ensures the safety and accuracy of mental health crisis detection systems.**

**Discord**: [https://discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)  
**Website**: [http://alphabetcartel.org](http://alphabetcartel.org)  
**Repository**: [https://github.com/the-alphabet-cartel/ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash)

*Revolutionizing crisis detection testing for safer communities.* 🧪✨