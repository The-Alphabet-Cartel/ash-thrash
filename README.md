# Ash-Thrash v3.0 - Comprehensive Crisis Detection Testing Suite

**Advanced testing system for tuning Ash NLP crisis detection accuracy**

[![Discord](https://img.shields.io/badge/Discord-Join%20Server-7289da)](https://discord.gg/alphabetcartel)
[![Website](https://img.shields.io/badge/Website-alphabetcartel.org-blue)](http://alphabetcartel.org)
[![GitHub](https://img.shields.io/badge/Version-v3.0-green)](https://github.com/the-alphabet-cartel/ash-thrash)
[![Docker](https://img.shields.io/badge/Docker-ghcr.io-blue)](https://github.com/orgs/the-alphabet-cartel/packages/container/package/ash-thrash)

## 🚀 What is Ash-Thrash v3.0?

Ash-Thrash v3.0 is a **comprehensive testing suite** designed to validate and tune the Ash NLP crisis detection system. Built with **pure Python** and **Docker Compose**, it provides enterprise-grade testing capabilities for mental health crisis detection systems.

### Key Features

- **🧪 350 Test Phrases**: Carefully curated phrases across 7 crisis categories
- **⚡ Multiple Test Modes**: Comprehensive, quick validation, and category-specific testing
- **🔧 NLP Tuning Suggestions**: Automated recommendations for improving detection accuracy
- **📊 REST API**: Full API on port 8884 for integration with ash-dash and external systems
- **🎯 Goal-Based Testing**: Pass/fail criteria based on safety-first principles
- **📱 Discord Integration**: Automated result notifications via webhooks
- **🐍 Python-First**: Standard Python CLI with no external UI dependencies
- **🐳 Docker Native**: Full Docker Compose orchestration and deployment with persistent containers
- **🔄 Modern FastAPI**: Latest patterns with lifespan event handlers

## 🎯 Testing Categories & Goals

### Definite Categories (Exact Match Required)
- **🚨 Definite High Crisis** (50 phrases) - **100% target** - Safety critical suicidal ideation
- **⚠️ Definite Medium Crisis** (50 phrases) - **65% target** - Severe mental health episodes  
- **ℹ️ Definite Low Crisis** (50 phrases) - **65% target** - Mild to moderate distress
- **✅ Definite None** (50 phrases) - **95% target** - Normal conversation (prevent false positives)

### Maybe Categories (Bidirectional Acceptable)
- **🔄 Maybe High/Medium** (50 phrases) - **90% target** - Either high OR medium acceptable
- **🔄 Maybe Medium/Low** (50 phrases) - **80% target** - Either medium OR low acceptable  
- **🔄 Maybe Low/None** (50 phrases) - **90% target** - Either low OR none acceptable

## 🏗️ Architecture Overview

### System Integration
```
Discord Messages → Ash-Bot → Ash-NLP → Crisis Detection
                                ↑
                          Ash-Thrash Testing
```

### Core Components
- **Testing Engine**: 350 phrase validation with bidirectional category support
- **REST API Server**: Persistent API container on port 8884 for integration and automation
- **CLI Container**: Persistent container for executing tests and validation commands
- **Docker Services**: Orchestrated deployment with health monitoring
- **GitHub Workflow**: Automated Docker image builds

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)

```bash
# 1. Clone and setup
git clone https://github.com/the-alphabet-cartel/ash-thrash.git
cd ash-thrash

# 2. Initial setup (creates .env file and directories)
python main.py setup

# 3. Configure environment
# Edit .env file with your NLP server URL and settings

# 4. Start all services (persistent containers)
docker compose up -d

# 5. Verify health
docker compose ps
docker compose exec ash-thrash python cli.py validate setup
```

### Option 2: Local Development

```bash
# 1. Clone and setup
git clone https://github.com/the-alphabet-cartel/ash-thrash.git
cd ash-thrash

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.template .env
# Edit .env with your settings
export $(cat .env | grep -v '^#' | xargs)

# 4. Validate setup
python cli.py validate setup

# 5. Run tests
python cli.py test comprehensive
```

## 🧪 Running Tests

### Docker Compose Testing (Recommended - Persistent Containers)

```bash
# Start all services (containers remain running)
docker compose up -d

# Full comprehensive test (350 phrases)
docker compose exec ash-thrash python cli.py test comprehensive

# Quick validation test (subset)
docker compose exec ash-thrash python cli.py test quick --sample-size 30

# Category-specific tests
docker compose exec ash-thrash python cli.py test category definite_high
docker compose exec ash-thrash python cli.py test category maybe_high_medium

# Output options
docker compose exec ash-thrash python cli.py test comprehensive --output json
docker compose exec ash-thrash python cli.py test comprehensive --output file

# System validation
docker compose exec ash-thrash python cli.py validate setup
docker compose exec ash-thrash python cli.py validate data

# API health check
docker compose exec ash-thrash python cli.py api health

# Stop all services when done
docker compose down
```

### Local Python CLI Testing

```bash
# Full comprehensive test (350 phrases)
python cli.py test comprehensive

# Quick validation test (subset)
python cli.py test quick --sample-size 30

# Category-specific test
python cli.py test category definite_high
python cli.py test category maybe_high_medium

# Output options
python cli.py test comprehensive --output json
python cli.py test comprehensive --output file

# Available categories:
# definite_high, definite_medium, definite_low, definite_none
# maybe_high_medium, maybe_medium_low, maybe_low_none
```

### API-Based Testing

```bash
# Start API server (automatically starts with docker compose up -d)
docker compose up -d

# Trigger tests via API (Python CLI)
docker compose exec ash-thrash python cli.py api trigger comprehensive --wait
docker compose exec ash-thrash python cli.py api health

# Trigger tests via API (direct HTTP)
curl -X POST http://localhost:8884/api/test/trigger \
  -H "Content-Type: application/json" \
  -d '{"test_type": "comprehensive", "triggered_by": "user"}'

# Check test status
curl http://localhost:8884/api/test/status/{test_id}

# Get results
curl http://localhost:8884/api/test/results/{test_id}
```

## 📊 REST API Endpoints

### Core Testing Endpoints
- `POST /api/test/trigger` - Trigger new test run
- `GET /api/test/status/{test_id}` - Get test status
- `GET /api/test/results/{test_id}` - Get test results
- `GET /api/test/latest` - Get most recent results
- `GET /api/test/history` - Get test history

### Information Endpoints  
- `GET /health` - Service health check
- `GET /api/test/data` - Test data information
- `GET /api/test/goals` - Testing goals and achievements

### Example API Usage

```python
import requests
import time

# Trigger comprehensive test
response = requests.post('http://localhost:8884/api/test/trigger', json={
    'test_type': 'comprehensive',
    'triggered_by': 'python_script'
})
test_info = response.json()
test_id = test_info['test_id']

# Monitor progress
while True:
    status = requests.get(f'http://localhost:8884/api/test/status/{test_id}').json()
    if status['status'] == 'completed':
        break
    print(f"Progress: {status['status']}")
    time.sleep(10)

# Get results
results = requests.get(f'http://localhost:8884/api/test/results/{test_id}').json()
print(f"Overall pass rate: {results['overall_pass_rate']:.1f}%")
```

## 🐍 Container Management Commands

### Docker Compose Operations

```bash
# Start all services (persistent containers)
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs ash-thrash-api
docker compose logs ash-thrash
docker compose logs -f  # Follow all logs

# Stop all services
docker compose down

# Restart specific services
docker compose restart ash-thrash-api
docker compose restart ash-thrash

# Rebuild and restart
docker compose down
docker compose build
docker compose up -d
```

### Management Script (`main.py`)

```bash
# Project lifecycle
python main.py setup                    # Initial setup and validation
python main.py start                    # Start all services
python main.py stop                     # Stop all services
python main.py status                   # Check service status
python main.py logs --follow            # View logs (follow mode)

# Testing (via persistent containers)
python main.py test-all comprehensive   # Run comprehensive tests
python main.py test-all quick           # Run quick tests

# Maintenance
python main.py build                    # Build Docker images
python main.py clean --force            # Clean up containers/images
python main.py validate                 # Validate configuration

# Advanced usage
python main.py cli test comprehensive   # Run CLI command in container
python main.py logs --service ash-thrash-api  # Service-specific logs
```

### CLI Script (`cli.py`)

```bash
# Direct testing (no Docker required)
python cli.py test comprehensive          # Full test suite
python cli.py test quick --sample-size 50 # Quick validation
python cli.py test category definite_high # Category-specific

# API operations
python cli.py api start --port 8884       # Start API server
python cli.py api trigger comprehensive --wait  # Trigger and wait
python cli.py api health                  # Health check

# Validation and setup
python cli.py validate setup             # Full system validation
python cli.py validate data              # Test data validation

# Output options
python cli.py test comprehensive --output json    # JSON output
python cli.py test comprehensive --output file    # Save to file
```

## 🔧 NLP Tuning Integration

Ash-Thrash automatically generates tuning suggestions based on test results:

### Example Tuning Output
```
🔧 TUNING SUGGESTIONS:
🚨 HIGH PRIORITY: definite_high only 85.0% (need 100.0%). 
   Consider lowering NLP_HIGH_CRISIS_THRESHOLD from 0.8 to 0.7

⚠️ FALSE POSITIVE ISSUE: definite_none only 88.0% (need 95.0%). 
   Consider raising NLP_NONE_THRESHOLD from 0.3 to 0.4

📈 TUNING NEEDED: maybe_high_medium only 75.0% (need 90.0%). 
   Review threshold settings
```

### Applying Suggestions

1. **Manual Tuning**: Update ash-nlp's `.env` file with suggested threshold values
2. **Iterative Testing**: Re-run tests after adjustments to validate improvements
3. **Performance Tracking**: Use historical data to track tuning effectiveness

## 🔌 Integration with Ash Ecosystem

### Ash-Bot Integration
Ash-Thrash uses the **exact same API calls** that ash-bot makes to ash-nlp, ensuring test results reflect real-world Discord behavior.

### Ash-Dash Integration  
Test results are automatically available to ash-dash via the REST API for dashboard visualization and monitoring.

### Ash-NLP Integration
Direct communication with ash-nlp using identical message preprocessing and analysis pipeline.

## 📱 Discord Notifications

Configure Discord webhooks for automated test notifications:

```bash
# In .env file
THRASH_DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your/webhook/url
DISCORD_NOTIFICATIONS_ENABLED=true
NOTIFY_ON_COMPREHENSIVE_TESTS=true
```

### Example Discord Notification
```
🧪 Ash-Thrash Test Completed: Comprehensive
Test ID: comprehensive_1693526400

📊 Overall Results
Pass Rate: 87.4%
Goal Achievement: 71.4%
Duration: 142.3s

🎯 Test Details
Total Tests: 350
Passed: 306
Failed: 44

📋 Category Results
✅ definite_high: 100.0%
❌ definite_medium: 62.0%
✅ definite_low: 68.0%
❌ definite_none: 88.0%
✅ maybe_high_medium: 92.0%
❌ maybe_medium_low: 76.0%
✅ maybe_low_none: 94.0%

🔧 Tuning Suggestions
🚨 HIGH PRIORITY: definite_none only 88.0% (need 95.0%)
📈 TUNING NEEDED: definite_medium only 62.0% (need 65.0%)
🔧 MINOR TUNING: maybe_medium_low at 76.0% (need 80.0%)
```

## ⚙️ Configuration

### Key Environment Variables

```bash
# NLP Server
GLOBAL_NLP_API_URL=http://10.20.30.253:8881

# API Server
GLOBAL_THRASH_API_PORT=8884

# Discord Integration
THRASH_DISCORD_WEBHOOK_URL=your_webhook_url
DISCORD_NOTIFICATIONS_ENABLED=true

# Testing Configuration
THRASH_MAX_CONCURRENT_TESTS=3
THRASH_QUICK_TEST_SAMPLE_SIZE=50

# Tuning Suggestions
THRASH_GENERATE_SUGGESTIONS=true
THRASH_SUGGESTION_THRESHOLD=10.0
```

## 📈 Performance Expectations

### Test Duration Estimates
- **Comprehensive Test**: ~3 minutes (350 phrases)
- **Quick Validation**: ~30 seconds (50 phrases)  
- **Category Test**: ~25 seconds (50 phrases)

### System Requirements
- **Memory**: 2GB RAM for API container, 1GB for CLI
- **CPU**: 1-2 cores recommended for concurrent testing
- **Network**: Stable connection to ash-nlp server
- **Storage**: ~100MB for results and logs

## 🐳 Docker Deployment

### Using Pre-built Images

```bash
# Pull latest image
docker pull ghcr.io/the-alphabet-cartel/ash-thrash:latest

# Run with persistent containers
docker compose up -d

# Execute tests in running container
docker compose exec ash-thrash python cli.py test comprehensive
```

### Docker Compose (Recommended)

```bash
# Start all services as persistent containers
docker compose up -d

# Check service status
docker compose ps

# Execute commands in running containers
docker compose exec ash-thrash python cli.py test comprehensive
docker compose exec ash-thrash python cli.py validate setup

# View service logs
docker compose logs -f ash-thrash-api
```

## 🔍 Troubleshooting

### Common Issues

**NLP Server Unreachable**
```bash
# Check connectivity from within container
docker compose exec ash-thrash python cli.py api health

# Test direct connection
curl http://10.20.30.253:8881/health

# Verify environment variable
docker compose exec ash-thrash printenv GLOBAL_NLP_API_URL
```

**Test Data Validation Errors**
```bash
# Validate test data from container
docker compose exec ash-thrash python cli.py validate data

# Should show: "🎉 Test data validation PASSED!"
```

**API Server Won't Start**
```bash
# Check port availability
netstat -tulpn | grep 8884

# Check service status
docker compose ps

# View detailed logs
docker compose logs ash-thrash-api
```

**Containers Won't Stay Running**
```bash
# Check container status
docker compose ps

# View container logs for exit reasons
docker compose logs ash-thrash
docker compose logs ash-thrash-api

# Restart services
docker compose restart

# Rebuild if needed
docker compose down
docker compose build
docker compose up -d
```

## 📚 Documentation

- **[API Documentation](docs/tech/api_v3_0.md)** - Complete REST API reference
- **[Team Guide](docs/team/team_guide_v3_0.md)** - Setup and usage for team members
- **[Troubleshooting](docs/troubleshooting_v3_0.md)** - Detailed problem resolution
- **[GitHub Release](docs/git/github_release_v3_0.md)** - Release notes and deployment guide

## 🤝 Contributing

We welcome contributions to improve Ash-Thrash! Here's how to help:

### Development Setup
```bash
git clone https://github.com/the-alphabet-cartel/ash-thrash.git
cd ash-thrash
pip install -r requirements.txt
python main.py setup
```

### Adding Test Phrases
1. Edit `src/test_data.py`
2. Add phrases to appropriate category
3. Run validation: `docker compose exec ash-thrash python cli.py validate data`
4. Test locally before submitting PR

### API Improvements
1. Modify `src/ash_thrash_api.py`
2. Update API documentation
3. Test with ash-dash integration

### Development Workflow
```bash
# Make changes to code
# ...

# Validate changes with persistent containers
docker compose up -d
docker compose exec ash-thrash python cli.py validate setup

# Test changes
docker compose exec ash-thrash python cli.py test quick

# Build and test with Docker
docker compose down
docker compose build
docker compose up -d
docker compose exec ash-thrash python cli.py test comprehensive
```

## 📞 Support & Community

### Getting Help
- **Technical Issues**: [GitHub Issues](https://github.com/the-alphabet-cartel/ash-thrash/issues)
- **Community Support**: [Discord Server](https://discord.gg/alphabetcartel)
- **Documentation**: [Project Wiki](https://github.com/the-alphabet-cartel/ash-thrash/wiki)

### Community Guidelines
- **Safety First**: Crisis detection accuracy is paramount
- **Inclusive Language**: LGBTQIA+ friendly community
- **Collaborative**: Help others and share knowledge
- **Respectful**: Treat everyone with dignity

## 📋 Roadmap

### v3.1 (Planned)
- [ ] Advanced analytics and trending
- [ ] Machine learning model comparison
- [ ] Automated threshold optimization
- [ ] Enhanced Discord bot integration

### v3.2 (Future)
- [ ] Multi-language testing support
- [ ] Custom phrase categories
- [ ] Integration with external ML platforms
- [ ] Advanced reporting dashboard

## 📄 License

This project is part of The Alphabet Cartel's open-source Ash Bot ecosystem. Licensed under MIT License.

## 🙏 Acknowledgments

**Built with ❤️ for chosen family by The Alphabet Cartel**

- **Community**: Our LGBTQIA+ Discord members who help test and improve the system
- **Contributors**: Developers who contribute code, documentation, and feedback  
- **Mental Health Advocates**: Professionals who guide our safety-first approach
- **Open Source**: The amazing Python and FastAPI communities

---

**Discord**: [https://discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)  
**Website**: [http://alphabetcartel.org](http://alphabetcartel.org)  
**Repository**: [https://github.com/the-alphabet-cartel/ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash)

*Crisis detection testing, one phrase at a time.* 🧪✨