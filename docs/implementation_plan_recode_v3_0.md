# Ash-Thrash v3.0 Implementation Plan and Progress

**Repository**: https://github.com/the-alphabet-cartel/ash-thrash  
**Project**: Ash-Thrash v3.0 Complete Rewrite  
**Document Location**: `ash/ash-thrash/docs/implementation_plan_recode_v3_0.md`  
**Last Updated**: August 2025 - Persistent Container Update

---

## 🎯 Project Overview

**COMPLETE REWRITE** of Ash-Thrash testing suite from bash scripts to a Python-first, Docker Compose-native system with persistent container architecture for testing and tuning the Ash NLP crisis detection system.

### Key Goals Achieved:
- ✅ **Python-First**: No bash scripts, pure Python CLI with standard library
- ✅ **Docker Native**: Full Docker Compose orchestration with persistent containers
- ✅ **350 Test Phrases**: Comprehensive test data across 7 crisis categories
- ✅ **REST API**: Full API server on port 8884 for ash-dash integration
- ✅ **NLP Integration**: Uses same API calls as ash-bot for accurate testing
- ✅ **Automated Building**: GitHub workflow for Docker image builds
- ✅ **FastAPI Modern**: Updated to use lifespan events (no deprecation warnings)
- ✅ **Container Naming**: Simplified ash-thrash container names
- ✅ **Persistent Architecture**: Containers remain running for instant testing

---

## 📋 Implementation Status

### ✅ **COMPLETED COMPONENTS**

#### **1. Core Testing Engine** 
- **File**: `src/ash_thrash_core.py`
- **Status**: ✅ Complete
- **Features**: 
  - 350 phrase testing across 7 categories
  - Multiple test modes (comprehensive, quick, category-specific)
  - NLP API integration using same format as ash-bot
  - Bidirectional testing for "maybe" categories
  - Automated tuning suggestions

#### **2. Test Data Module**
- **File**: `src/test_data.py`
- **Status**: ✅ Complete
- **Features**:
  - 350 phrases distributed across 7 categories:
    - `definite_high` (50 phrases) - 100% target - Suicidal ideation
    - `definite_medium` (50 phrases) - 65% target - Severe episodes
    - `definite_low` (50 phrases) - 65% target - Mild distress
    - `definite_none` (50 phrases) - 95% target - Normal conversation
    - `maybe_high_medium` (50 phrases) - 90% target - Bidirectional
    - `maybe_medium_low` (50 phrases) - 80% target - Bidirectional
    - `maybe_low_none` (50 phrases) - 90% target - Bidirectional
  - Full validation system for phrase counts and structure

#### **3. REST API Server**
- **File**: `src/ash_thrash_api.py`
- **Status**: ✅ Complete - **UPDATED for Persistent Architecture**
- **Recent Changes**:
  - ✅ **Fixed FastAPI deprecation warning**: Replaced `@app.on_event("startup")` with modern `lifespan` event handler
  - ✅ **Updated Discord webhook variable**: Changed from `DISCORD_WEBHOOK_URL` to `THRASH_DISCORD_WEBHOOK_URL`
  - ✅ **Modern FastAPI patterns**: Uses `@asynccontextmanager` and `lifespan=lifespan` parameter
  - ✅ **Persistent container optimized**: Designed for always-running API service
- **Features**:
  - FastAPI-based server on port 8884 (persistent container)
  - Full CRUD operations for test management
  - Background test execution with status tracking
  - Discord webhook integration for notifications (updated env var)
  - JSON response format compatible with ash-dash
  - Health checks and monitoring endpoints
  - No deprecation warnings - fully modern FastAPI implementation

#### **4. Python CLI Interface**
- **File**: `cli.py`
- **Status**: ✅ Complete - **OPTIMIZED for Persistent Containers**
- **Features**:
  - Standard Python argparse (no external dependencies)
  - Terminal-friendly with rich console output
  - All test operations (comprehensive, quick, category-specific)
  - API operations (start server, trigger tests, health checks)
  - Validation commands (setup, data validation)
  - Multiple output formats (console, JSON, file)
  - **Optimized for execution within persistent containers**

#### **5. Docker Compose Management**
- **File**: `main.py` (renamed from manage.py)
- **Status**: ✅ Complete - **UPDATED for Persistent Architecture**
- **Features**:
  - Full Docker Compose lifecycle management for persistent containers
  - Service health monitoring
  - Log management and viewing
  - Build and deployment operations
  - Cleanup and maintenance operations
  - **Container exec command support for persistent workflow**

#### **6. Docker Configuration**
- **Files**: `Dockerfile`, `docker-compose.yml`, `requirements.txt`
- **Status**: ✅ Complete - **MAJOR UPDATE for Persistent Containers**
- **Recent Changes**:
  - ✅ **Persistent container architecture**: Both API and CLI containers remain running
  - ✅ **API container command**: Explicit uvicorn startup for persistent API service
  - ✅ **CLI container command**: `tail -f /dev/null` to keep container alive
  - ✅ **Removed profiles**: No more profile-based container management
  - ✅ **Always-on restart policy**: `restart: unless-stopped` for both containers
  - ✅ **Container renaming**: Changed `ash-thrash-cli` to `ash-thrash` for easier command usage
- **Features**:
  - Multi-service orchestration (API, CLI, health checks)
  - Proper networking and volume management
  - Health checks and dependency management
  - Production-ready container configuration with persistent services
  - Simplified container naming for better UX
  - **Persistent container architecture eliminates orphan containers**

#### **7. GitHub Workflow**
- **File**: `.github/workflows/docker-build.yml`
- **Status**: ✅ Complete
- **Features**:
  - Automatic Docker image builds on main branch pushes
  - AMD64-only builds (optimized for development speed)
  - No security scanning (removed for development speed)
  - Validation of test data and configuration
  - Multi-tag strategy (latest, v3.0, main, commit-specific)
  - GHCR publishing with proper metadata

#### **8. Documentation**
- **Files**: `README.md`, directory structure guide, workflow setup
- **Status**: ✅ Complete - **UPDATED for Persistent Container Workflow**
- **Features**:
  - Comprehensive setup and usage documentation
  - Python-first approach examples
  - Docker Compose integration guide with persistent containers
  - API usage examples
  - Troubleshooting section
  - **Updated all examples to use `docker compose exec` commands**

---

## 🗂️ File Structure (Current)

```
ash-thrash/                           # Individual repository
├── .github/
│   └── workflows/
│       └── docker-build.yml         # ✅ GitHub workflow for Docker builds
├── src/
│   ├── ash_thrash_core.py           # ✅ Core testing engine
│   ├── ash_thrash_api.py            # ✅ REST API server (persistent container)
│   └── test_data.py                 # ✅ 350 test phrases + categories
├── config/
│   └── testing_goals.json           # ✅ Pass/fail criteria (existing)
├── results/                          # Auto-created for test results
├── logs/                             # Auto-created for logs
├── reports/                          # Auto-created for reports
├── cli.py                           # ✅ Python CLI interface (persistent container optimized)
├── main.py                          # ✅ Docker Compose management (persistent container support)
├── docker-compose.yml               # ✅ Docker orchestration (PERSISTENT ARCHITECTURE)
├── Dockerfile                       # ✅ Container build config
├── requirements.txt                 # ✅ Python dependencies
├── .env.template                    # ✅ Environment template (moved to root)
├── .env                             # Created from template during setup
└── README.md                        # ✅ Updated documentation (persistent container workflow)
```

---

## 🔧 Configuration Changes Made

### **Persistent Container Architecture**
- **API Container**: Runs `uvicorn` server continuously on port 8884
- **CLI Container**: Runs `tail -f /dev/null` to stay alive for exec commands
- **No Profiles**: Containers start by default with `docker compose up -d`
- **Always Running**: Both containers remain active until explicitly stopped

### **Updated Command Structure**
- **Old**: `docker compose run --rm ash-thrash test comprehensive` (creates orphan containers)
- **New**: `docker compose exec ash-thrash python cli.py test comprehensive` (uses persistent container)

### **Environment Variables**
- **Location**: `.env.template` moved from `config/` to root directory (per user preference)
- **Management**: `main.py setup` automatically creates `.env` from template
- **Key Variables**:
  - `GLOBAL_NLP_API_URL=http://10.20.30.253:8881`
  - `GLOBAL_THRASH_API_PORT=8884`
  - `THRASH_DISCORD_WEBHOOK_URL` (updated from `DISCORD_WEBHOOK_URL`)
  - Testing and tuning configuration options

### **Container Naming** (Updated in Previous Conversation)
- **Changed**: `ash-thrash-cli` → `ash-thrash` (simplified for easier remembering)
- **Usage**: `docker compose exec ash-thrash python cli.py test comprehensive`
- **Impact**: Updated in docker-compose.yml, main.py, and all documentation

### **Dependencies**
- **Removed**: `click` dependency (replaced with standard `argparse`)
- **Core**: FastAPI, aiohttp, requests for API and NLP communication
- **Development**: No external UI dependencies, terminal-native

### **Workflow Optimizations**
- **Platform**: AMD64-only builds (removed ARM64 for speed)
- **Security**: Removed Trivy and security scanning for development speed
- **Context**: Adjusted for standalone repository (not submodule)

---

## 🚀 Usage Patterns Established

### **Persistent Container Operations** (`docker compose`)
```bash
docker compose up -d                           # Start all persistent services
docker compose exec ash-thrash python cli.py test comprehensive  # Run comprehensive test
docker compose exec ash-thrash python cli.py test quick         # Quick validation
docker compose exec ash-thrash python cli.py validate setup     # System validation
docker compose exec ash-thrash python cli.py api health         # Health check
docker compose logs ash-thrash-api            # View API logs
docker compose down                            # Stop all services
```

### **Management Operations** (`main.py`)
```bash
python main.py setup                 # Initial setup
python main.py start                 # Start persistent Docker services
python main.py status                # Check service health
python main.py test-all comprehensive # Run tests via persistent containers
python main.py logs --follow         # Monitor logs
python main.py stop                  # Stop services
python main.py clean --force         # Cleanup
```

### **Direct Testing** (`cli.py`)
```bash
python cli.py test comprehensive     # Full 350 phrase test
python cli.py test quick --sample-size 30  # Quick validation
python cli.py test category definite_high  # Category-specific
python cli.py api start --port 8884  # Start API server
python cli.py validate setup         # System validation
```

### **API Integration**
- **REST API**: http://localhost:8884 with full OpenAPI documentation
- **Health Endpoint**: `/health` for monitoring
- **Test Triggers**: `/api/test/trigger` for automated testing
- **Results**: `/api/test/results/{test_id}` for result retrieval
- **Persistent availability**: API always running with persistent containers

---

## 🔄 Recent Updates (August 2025 - Persistent Container Architecture)

### **Persistent Container Implementation**
- **Issue**: `docker compose run` commands created orphan containers
- **Solution**: ✅ Implemented persistent container architecture
- **Changes**:
  - API container runs `uvicorn` continuously
  - CLI container runs `tail -f /dev/null` to stay alive
  - Removed `profiles` section to start containers by default
  - Added `restart: unless-stopped` policy
  - Updated all documentation to use `docker compose exec` commands
  - Eliminated orphan containers completely

### **Command Structure Modernization**
- **Old Workflow**: 
  ```bash
  docker compose run --rm ash-thrash test comprehensive  # Creates temporary container
  ```
- **New Workflow**:
  ```bash
  docker compose up -d                                   # Start persistent containers
  docker compose exec ash-thrash python cli.py test comprehensive  # Execute in running container
  docker compose down                                    # Stop when done
  ```

### **Container Lifecycle Optimization**
- **Startup Time**: Eliminated container startup delays for each test
- **Resource Usage**: More efficient with persistent containers
- **User Experience**: Instant test execution without waiting
- **Management**: Clean container lifecycle with Docker Compose

### **Documentation Overhaul**
- **Files Updated**: README.md, team guide, troubleshooting guide, API docs
- **Changes**: All examples now use persistent container commands
- **Status**: Complete documentation consistency with new architecture

## ⚠️ Known Issues and Considerations

### **1. NLP Server Dependency**
- **Issue**: All tests require ash-nlp server to be running
- **Status**: Expected behavior, by design
- **Mitigation**: Health checks validate NLP connectivity from persistent containers

### **2. Test Data Validation** 
- **Issue**: Must maintain exactly 350 phrases (50 per category)
- **Status**: Automated validation in place
- **Mitigation**: `docker compose exec ash-thrash python cli.py validate data` checks structure

### **3. Docker Network Integration**
- **Issue**: Must integrate with existing ash ecosystem networking
- **Status**: Configured for ash-network (172.20.0.0/16)
- **Mitigation**: Uses consistent networking with other ash services

### **4. FastAPI Version Compatibility**
- **Issue**: Deprecation warnings with older FastAPI patterns
- **Status**: ✅ RESOLVED in Previous Updates
- **Resolution**: Updated to modern lifespan event handlers

### **5. Container Resource Management**
- **Issue**: Persistent containers consume resources continuously
- **Status**: By design - trade-off for instant availability
- **Mitigation**: Containers can be stopped when not needed: `docker compose down`

---

## 📈 Performance Expectations

### **Test Execution Times (with Persistent Containers)**
- **Comprehensive Test**: ~3 minutes (350 phrases) - **No container startup delay**
- **Quick Validation**: ~30 seconds (50 phrases) - **Instant execution**
- **Category Test**: ~25 seconds (50 phrases) - **Immediate response**

### **Container Startup Times**
- **Initial Startup**: ~30 seconds (one-time when starting services)
- **Test Execution**: **0 seconds delay** (containers already running)
- **Total Efficiency**: **Significant time savings** for repeated testing

### **System Requirements**
- **Memory**: 2GB RAM for API container, 1GB for CLI (persistent)
- **CPU**: 1-2 cores recommended
- **Storage**: ~100MB for results and logs
- **Network**: Stable connection to ash-nlp server

---

## 🔮 Future Enhancements (Not Yet Implemented)

### **Short Term** (if needed)
- [ ] **Advanced Analytics**: Trending and historical analysis
- [ ] **Custom Categories**: User-defined test phrase categories
- [ ] **Batch Operations**: Multiple test runs with comparison
- [ ] **Export Formats**: CSV, Excel output for results

### **Medium Term** (if requested)
- [ ] **Security Scanning**: Optional workflow for production builds
- [ ] **Multi-Environment**: Development vs production configurations  
- [ ] **Advanced Webhooks**: More Discord integration options
- [ ] **API Authentication**: Token-based API access

### **Long Term** (future consideration)
- [ ] **Machine Learning**: Automated phrase generation
- [ ] **Multi-Language**: Support for non-English testing
- [ ] **Integration Testing**: Automated ash-bot integration tests
- [ ] **Performance Monitoring**: Real-time metrics and alerting

---

## 🎯 Success Criteria (All Met)

- ✅ **No Bash Scripts**: Complete Python implementation
- ✅ **Docker Native**: Full Docker Compose integration
- ✅ **API Compatible**: Works with ash-dash via REST API
- ✅ **NLP Integration**: Uses same endpoints as ash-bot
- ✅ **Automated Building**: GitHub workflow for Docker images
- ✅ **350 Test Phrases**: Comprehensive test coverage
- ✅ **Tuning Suggestions**: Automated NLP threshold recommendations
- ✅ **Fast Development**: Optimized build and test cycles
- ✅ **Persistent Architecture**: Eliminates orphan containers and startup delays

---

## 🚨 Critical Information for Future Conversations

### **Context**
- This is a **COMPLETE REWRITE** of ash-thrash, not an incremental update
- All previous bash scripts and old Python files should be **REMOVED**
- The system is **production-ready** and fully functional
- **Persistent container architecture** is now the standard deployment model

### **Key Decisions Made**
- **No External UI Dependencies**: Uses standard Python argparse, not click
- **Standalone Repository**: Not a submodule, individual repo with own GitHub workflow
- **Development Optimized**: Fast builds, no security scanning during development
- **File Naming**: `main.py` for management, `cli.py` for direct operations
- **Container Naming**: Simplified `ash-thrash` (updated from `ash-thrash-cli`)
- **Modern FastAPI**: Uses lifespan events, no deprecated patterns
- **Persistent Containers**: Both API and CLI containers remain running for instant access

### **Container Architecture**
- **ash-thrash-api**: Persistent API server (`uvicorn` command)
- **ash-thrash**: Persistent CLI container (`tail -f /dev/null` command)
- **No Profiles**: Containers start with default `docker compose up -d`
- **Command Pattern**: Use `docker compose exec` instead of `docker compose run`

### **Integration Points**
- **ash-nlp**: Uses `GLOBAL_NLP_API_URL` environment variable
- **ash-dash**: Provides REST API on port 8884 for dashboard integration
- **Discord**: Webhook notifications via `THRASH_DISCORD_WEBHOOK_URL` (updated variable name)
- **GitHub**: Automated Docker image building and publishing

### **Repository Structure**
- **Location**: `ash/ash-thrash/` (individual repository)
- **Branch**: Working on `v3.0` branch for complete rewrite
- **Configuration**: `.env.template` in root directory (user's preference)
- **Workflow**: `.github/workflows/docker-build.yml` (not in parent repo)

### **Usage Patterns**
- **Start Services**: `docker compose up -d` (containers remain running)
- **Execute Tests**: `docker compose exec ash-thrash python cli.py test comprehensive`
- **Check Health**: `docker compose exec ash-thrash python cli.py api health`
- **Stop Services**: `docker compose down` (only when completely done)

This document serves as a complete reference for the ash-thrash v3.0 implementation state with persistent container architecture and should enable seamless continuation of work in future conversations.