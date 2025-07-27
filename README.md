# 🧪 Ash-Thrash: Comprehensive Crisis Detection Testing Suite

> *Thrashing the system to find failures before they find you*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![Windows 11](https://img.shields.io/badge/Windows-11-blue.svg)](https://www.microsoft.com/windows)
[![API](https://img.shields.io/badge/API-REST-green.svg)](http://localhost:8884/api/docs)

## What is Ash-Thrash?

Ash-Thrash is a comprehensive testing framework designed specifically for **The Alphabet Cartel's** [Ash Discord Bot](https://github.com/The-Alphabet-Cartel/ash) NLP crisis detection system. It systematically tests crisis detection accuracy and speed using **350 carefully crafted test phrases** across **7 priority categories**.

**🎯 Why This Matters:** Crisis detection systems save lives, but they need to be **thoroughly tested** to ensure they work when it matters most. Ash-Thrash provides continuous automated validation to maintain system reliability.

---

**🔗 Ecosystem Links:**
- **Main Bot:** [github.com/The-Alphabet-Cartel/ash](https://github.com/The-Alphabet-Cartel/ash)
- **NLP Server:** [github.com/The-Alphabet-Cartel/ash-nlp](https://github.com/The-Alphabet-Cartel/ash-nlp)  
- **Dashboard:** [github.com/The-Alphabet-Cartel/ash-dash](https://github.com/The-Alphabet-Cartel/ash-dash)
- **Testing Suite:** [github.com/The-Alphabet-Cartel/ash-thrash](https://github.com/The-Alphabet-Cartel/ash-thrash) *(You are here)*
- **Community:** [discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)

---

## 🎯 Testing Goals & Targets

Ash-Thrash tests **350 unique phrases** designed to stress-test every aspect of crisis detection:

| Priority Level | Test Phrases | Target Catch Rate | Critical? | Safety Impact |
|----------------|--------------|-------------------|-----------|---------------|
| **🚨 Definite High** | 50 phrases | **100%** | ✅ CRITICAL | Lives depend on this |
| **⚠️ Definite Medium** | 50 phrases | **65%** | - | Important for support |
| **🔍 Definite Low** | 50 phrases | **65%** | - | General wellness |
| **✅ Definite None** | 50 phrases | **95%** | ✅ CRITICAL | Prevent alert fatigue |
| **📈 Maybe High/Medium** | 50 phrases | **90%** | - | Allow escalation only |
| **📊 Maybe Medium/Low** | 50 phrases | **80%** | - | Allow escalation only |
| **📉 Maybe Low/None** | 50 phrases | **90%** | ✅ CRITICAL | Prevent false positives |

### 🔍 What Makes This Special?

- **"Maybe" Categories** test edge cases where escalation is OK but de-escalation is dangerous
- **Definite Categories** require exact priority matching
- **Safety-First Design** prioritizes catching real crises over avoiding false positives
- **Real-World Phrases** based on actual community language patterns

---

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** (for containerized deployment)
- **Python 3.11+** (for local development)
- **Access to Ash NLP Server** (default: `10.20.30.16:8881`)
- **Windows 11 compatible** (developed for your environment)

### One-Command Setup

```bash
# Clone and setup everything
git clone https://github.com/The-Alphabet-Cartel/ash-thrash.git
cd ash-thrash
bash setup.sh
```

### Manual Setup

```bash
# Clone the repository
git clone https://github.com/The-Alphabet-Cartel/ash-thrash.git
cd ash-thrash

# Copy and configure environment
cp .env.template .env
# Edit .env with your NLP server details (default works for most setups)

# Start with Docker (recommended)
docker-compose up -d

# OR install locally
pip install -r requirements.txt
```

### Run Your First Test

```bash
# Comprehensive test (350 phrases) - Docker
docker-compose exec ash-thrash python src/comprehensive_testing.py

# Comprehensive test (350 phrases) - Local
python src/comprehensive_testing.py

# Quick validation (10 phrases) - Docker  
docker-compose exec ash-thrash python src/quick_validation.py

# Quick validation (10 phrases) - Local
python src/quick_validation.py
```

### Check Results

- **View Results:** `./results/comprehensive/` directory
- **API Access:** http://localhost:8884/api/test/status
- **Health Check:** http://localhost:8884/health

---

## 📋 Usage Examples

### Basic Testing Commands

```bash
# Full comprehensive test (350 phrases)
python src/comprehensive_testing.py

# Quick health check (10 phrases)  
python src/quick_validation.py

# Test specific category only
python src/comprehensive_testing.py --category definite_high

# Generate performance report
python scripts/generate_report.py --days 7 --format html
```

### Docker Operations

```bash
# Start all services
docker-compose up -d

# Run comprehensive test in container
docker-compose exec ash-thrash python src/comprehensive_testing.py

# Run quick validation
docker-compose exec ash-thrash python src/quick_validation.py

# View real-time logs
docker-compose logs -f ash-thrash

# Restart services
docker-compose restart

# Stop all services
docker-compose down
```

### API Testing & Integration

```bash
# Check system health
curl http://localhost:8884/health

# Get current testing status
curl http://localhost:8884/api/test/status

# Trigger new comprehensive test
curl -X POST http://localhost:8884/api/test/run \
  -H "Content-Type: application/json" \
  -d '{"priority": "comprehensive"}'

# Get latest test results
curl http://localhost:8884/api/test/results/latest | jq '.'
```

### Advanced Usage

**Custom Test Configuration:**
```bash
# Test with custom concurrency
MAX_CONCURRENT_TESTS=10 python src/comprehensive_testing.py

# Test with detailed logging
ENABLE_DETAILED_LOGGING=true python src/comprehensive_testing.py

# Test specific server
NLP_SERVER_URL=http://dev-server:8881 python src/comprehensive_testing.py
```

---

## 📊 Dashboard Integration

### Integration with Ash-Dash

Ash-Thrash integrates seamlessly with [ash-dash](https://github.com/The-Alphabet-Cartel/ash-dash) to provide real-time testing metrics:

```bash
# Copy integration components to your ash-dash repository
cp dashboard/routes.js ../ash-dash/routes/testing.js
cp dashboard/styles/testing-dashboard.css ../ash-dash/public/css/
cp dashboard/templates/testing-section.html ../ash-dash/views/partials/
```

**Add to ash-dash server.js:**
```javascript
const testingRoutes = require('./routes/testing');
app.use('/api/testing', testingRoutes);
```

**Dashboard Features:**
- 📊 **Real-time Test Results** - Latest pass rates and performance
- 🎯 **Goal Achievement Tracking** - Visual progress toward targets
- 📈 **Performance Trends** - Historical testing data over time
- 🔍 **Detailed Failure Analysis** - See exactly which phrases failed
- ⚡ **One-Click Testing** - Trigger tests directly from dashboard

### Standalone Dashboard

Don't want to modify ash-dash? Ash-Thrash includes its own dashboard:

- **Testing Dashboard:** http://localhost:8884
- **API Documentation:** http://localhost:8884/api/docs
- **Real-time Status:** http://localhost:8884/api/test/status
- **Historical Data:** http://localhost:8884/api/test/history

### API Endpoints

```bash
# Get current testing status
curl http://localhost:8884/api/test/status

# Trigger comprehensive test
curl -X POST http://localhost:8884/api/test/run

# Get latest results
curl http://localhost:8884/api/test/results/latest

# Get performance trends (last 30 days)
curl http://localhost:8884/api/test/history?days=30

# Download detailed results
curl http://localhost:8884/api/test/results/download/comprehensive_test_results_1690380000.json
```

---

## 🔧 Configuration

### Environment Configuration (.env)

```bash
# Core NLP Server Settings
NLP_SERVER_HOST=10.20.30.16        # Your NLP server IP
NLP_SERVER_PORT=8881                # Your NLP server port
NLP_SERVER_URL=http://10.20.30.16:8881

# Performance Settings  
MAX_CONCURRENT_TESTS=5              # Parallel test execution
TEST_TIMEOUT_SECONDS=10             # Per-test timeout
RESULTS_RETENTION_DAYS=30           # How long to keep results

# API Configuration
API_PORT=8884                       # Testing API port
API_HOST=0.0.0.0                   # API host binding

# Scheduling (when running with Docker)
ENABLE_SCHEDULED_TESTING=true
COMPREHENSIVE_TEST_SCHEDULE="0 */6 * * *"    # Every 6 hours
QUICK_VALIDATION_SCHEDULE="0 * * * *"        # Every hour

# Optional Database
ENABLE_DATABASE=false               # Set to true for PostgreSQL storage
DATABASE_URL=postgresql://user:pass@localhost:5432/ash_testing
```

### Testing Goals (config/testing_goals.json)

Customize your testing targets:

```json
{
  "definite_high": {
    "target_pass_rate": 100.0,
    "description": "High Priority Crisis (Safety First!)",
    "critical": true
  },
  "definite_none": {
    "target_pass_rate": 95.0,
    "description": "False Positive Prevention",
    "critical": true
  }
}
```

---

## 📈 Results & Analytics

### Understanding Test Results

**Sample API Response:**
```json
{
  "test_id": "test_20250726_090000",
  "summary": {
    "total_phrases": 350,
    "passed": 298,
    "failed": 52,
    "pass_rate": 85.1,
    "avg_response_time": 1.34
  },
  "goals_assessment": {
    "goals_met": 6,
    "total_goals": 7,
    "achievement_rate": 85.7,
    "overall_status": "⚠️ 6/7 GOALS MET"
  },
  "definite_high": {
    "target_rate": 100.0,
    "actual_rate": 98.0,
    "goal_met": false,
    "status": "❌ MISSED"
  },
  "category_results": {
    "definite_high": {
      "passed": 49,
      "total": 50,
      "pass_rate": 98.0,
      "avg_confidence": 0.847,
      "failures": [
        {
          "message": "I can't handle this anymore",
          "expected": "high",
          "detected": "medium", 
          "confidence": 0.623
        }
      ]
    }
  }
}
```

### Data Retention & Cleanup

```bash
# Automatic cleanup (runs daily at 2 AM)
# Keeps last 30 days by default

# Manual cleanup
bash scripts/cleanup_old_results.sh 30    # Keep last 30 days
bash scripts/cleanup_old_results.sh 7     # Keep last 7 days

# Backup before cleanup
bash scripts/backup_results.sh

# Restore from backup
tar -xzf results/backups/backup_2025-07-26.tar.gz
```

### Exporting & Analysis

```bash
# Export results to CSV for analysis
python scripts/export_to_csv.py --days 30 --output analysis.csv

# Generate comprehensive report
python scripts/generate_report.py --days 30 --format html --include-charts

# Export for external tools
python scripts/export_for_external.py --format elasticsearch
python scripts/export_for_external.py --format prometheus
```

---

## 🔗 Integration with Ash Ecosystem

### Connecting to Your Ash Setup

Ash-Thrash works with your existing Ash deployment without any modifications:

```bash
# Default connection (works with standard Ash setup)
NLP_SERVER_URL=http://10.20.30.16:8881

# Custom NLP server location
NLP_SERVER_URL=http://192.168.1.100:8881

# Testing different environments
NLP_SERVER_URL=http://ash-nlp-dev:8881     # Development
NLP_SERVER_URL=http://ash-nlp-prod:8881    # Production
```

### Multi-Environment Testing

```bash
# Test multiple NLP servers
docker-compose up -d
docker-compose exec ash-thrash python src/comprehensive_testing.py --server dev
docker-compose exec ash-thrash python src/comprehensive_testing.py --server staging  
docker-compose exec ash-thrash python src/comprehensive_testing.py --server prod

# Compare performance across environments
python scripts/compare_environments.py --environments dev,staging,prod
```

### CI/CD Integration

**GitHub Actions Example:**
```yaml
name: Ash Crisis Detection Testing
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:      # Manual trigger

jobs:
  crisis-detection-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          repository: The-Alphabet-Cartel/ash-thrash
      
      - name: Run comprehensive test
        run: |
          docker-compose up -d
          docker-compose exec ash-thrash python src/comprehensive_testing.py
          
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: results/comprehensive/
```

---

## 📚 Documentation & Resources

### Complete Documentation

- **[👥 Team Member Guide](docs/TEAM_GUIDE.md)** - Operations guide for Crisis Response teams
- **[🔧 Implementation Guide](docs/IMPLEMENTATION_GUIDE.md)** - Technical setup and deployment
- **[🔌 API Documentation](docs/API.md)** - Complete REST API reference
- **[🐛 Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### Quick Reference

**Essential Commands:**
```bash
# Setup and start
bash setup.sh && docker-compose up -d

# Run comprehensive test  
docker-compose exec ash-thrash python src/comprehensive_testing.py

# Check status
curl http://localhost:8884/api/test/status

# View results
ls -la results/comprehensive/
```

**Key Configuration Files:**
- `.env` - Environment variables and server settings
- `config/testing_goals.json` - Testing targets and thresholds
- `config/server_config.json` - NLP server connection settings
- `docker-compose.yml` - Service orchestration

**Important Directories:**
- `src/test_data/` - Test phrase collections (350 phrases total)
- `results/comprehensive/` - Full test results storage
- `dashboard/` - ash-dash integration components
- `scripts/` - Utility and maintenance scripts

### Architecture Overview

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│                     │    │                     │    │                     │
│   Ash-Thrash        │───▶│   Ash NLP Server    │◀───│   Ash Discord Bot   │
│   Testing Suite     │    │   (10.20.30.16)    │    │   (Crisis Detection)│
│                     │    │                     │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
           │                                                        │
           │                                                        │
           ▼                                                        ▼
┌─────────────────────┐                              ┌─────────────────────┐
│                     │                              │                     │
│   Ash-Dash          │◀─────────────────────────────│   Discord Server    │
│   Analytics         │      Real Crisis Detection   │   (Live Community)  │
│   Dashboard         │                              │                     │
└─────────────────────┘                              └─────────────────────┘
```

**Data Flow:**
1. **Ash-Thrash** sends test phrases to **Ash NLP Server**
2. **NLP Server** analyzes phrases and returns crisis levels
3. **Ash-Thrash** compares results against expected outcomes
4. **Results** are stored and made available to **Ash-Dash**
5. **Dashboard** displays real-time testing metrics and trends

---

## 🧪 Testing Framework Details

### Automated Test Suite

```bash
# Run comprehensive detection tests
python tests/crisis_detection_test.py

# Test API endpoints
python tests/api_integration_test.py

# Verify dashboard integration
python tests/dashboard_integration_test.py

# Test performance under load
python tests/performance_test.py
```

### Manual Testing Scenarios

- **High Crisis**: Test with actual crisis language patterns
- **Context Detection**: Verify humor/movie/game context filtering
- **Edge Cases**: Borderline phrases that test detection boundaries
- **Performance**: Load testing with concurrent requests
- **Integration**: Verify communication with NLP server and dashboard

---

## 🔄 Deployment & Updates

### Production Deployment

```bash
# Production deployment with Docker
git clone https://github.com/The-Alphabet-Cartel/ash-thrash.git
cd ash-thrash
cp .env.template .env
# Configure production settings
docker-compose -f docker-compose.prod.yml up -d
```

### Update Process

1. **Backup Current State**
   ```bash
   docker-compose exec ash-thrash tar -czf backup.tar.gz /app/results/
   ```

2. **Pull Updates**
   ```bash
   git pull origin main
   docker-compose pull
   ```

3. **Deploy**
   ```bash
   docker-compose up -d
   ```

4. **Verify**
   ```bash
   curl http://localhost:8884/health
   docker-compose exec ash-thrash python src/quick_validation.py
   ```

### Rollback Procedure

```bash
# Rollback to previous version
docker-compose down
docker image tag ghcr.io/the-alphabet-cartel/ash-thrash:v1.0 ghcr.io/the-alphabet-cartel/ash-thrash:latest
docker-compose up -d

# Restore results if needed
docker-compose exec ash-thrash tar -xzf backup.tar.gz -C /app/
```

---

## 🤝 Contributing

### Development Setup

```bash
# Fork and clone
git clone https://github.com/YourUsername/ash-thrash.git
cd ash-thrash

# Set up development environment
bash setup.sh
pip install -r requirements-dev.txt
pre-commit install

# Make your changes
git checkout -b feature/your-amazing-feature

# Test your changes
pytest tests/
docker-compose up -d && docker-compose exec ash-thrash python src/comprehensive_testing.py

# Submit for review
git push origin feature/your-amazing-feature
# Create pull request on GitHub
```

### Code Standards

- Follow PEP 8 style guidelines
- Include comprehensive tests for new features
- Update documentation for any API changes
- Ensure Docker compatibility
- Add logging for debugging purposes

### Testing Your Changes

```bash
# Test your changes don't break existing functionality
python src/comprehensive_testing.py --quick-test

# Test specific components
pytest tests/test_your_feature.py

# Integration test
docker-compose up -d
docker-compose exec ash-thrash python src/comprehensive_testing.py
```

### Contributing Areas

**🔧 Code Contributions:**
- Bug fixes and performance improvements
- New testing categories and edge cases
- Dashboard enhancements and visualizations
- API improvements and new endpoints
- Docker optimization and deployment tools

**📝 Documentation Contributions:**
- Improve setup and usage guides
- Add troubleshooting scenarios
- Create video tutorials and walkthroughs
- Translate documentation for international users
- Write best practices and optimization guides

**🧪 Testing & Validation:**
- Add community-specific test phrases
- Test on different environments and configurations
- Report edge cases and unusual scenarios
- Validate integration with different Ash setups
- Performance testing and benchmarking

**🎨 Design & UX:**
- Dashboard component improvements
- Visual design enhancements
- User experience optimization
- Accessibility improvements
- Mobile-responsive design

---

## 🛣️ Roadmap

### Current Version (v1.0)
- ✅ 350-phrase comprehensive testing suite
- ✅ 7 priority categories with safety-first design
- ✅ Docker-based deployment
- ✅ REST API with real-time status
- ✅ Ash-dash dashboard integration
- ✅ Automated scheduling and cleanup

### Upcoming Features (v1.1)
- 🔄 **Enhanced Analytics** - Advanced failure pattern analysis
- 🔄 **Multi-Language Support** - Testing in multiple languages
- 🔄 **Performance Benchmarking** - Historical performance comparisons
- 🔄 **Advanced Reporting** - PDF and Excel report generation

### Future Vision (v2.0)
- 🚀 **Machine Learning Integration** - AI-powered test phrase generation
- 🚀 **Real-time Monitoring** - Live community phrase analysis
- 🚀 **Advanced Integrations** - Slack, Teams, and webhook notifications
- 🚀 **Distributed Testing** - Multi-server testing coordination

---

## 📞 Support & Community

### Getting Help & Support

**Primary Support Channels:**
- 🐛 **[GitHub Issues](https://github.com/The-Alphabet-Cartel/ash-thrash/issues)** - Bug reports, feature requests, and technical questions
- 💬 **[The Alphabet Cartel Discord](https://discord.gg/alphabetcartel)** - Community support, real-time help, and development discussions
- 📖 **[Documentation](docs/)** - Comprehensive guides, tutorials, and references
- 📧 **Direct Contact** - For urgent issues or private concerns

**Community Resources:**
- 🎥 **Video Tutorials** - Setup walkthroughs and usage demonstrations
- 📝 **Best Practices Guide** - Community-tested optimization strategies  
- 🛠️ **Community Tools** - User-contributed utilities and extensions
- 📊 **Benchmark Results** - Performance comparisons and testing outcomes

### Community & Support

**Getting Help:**
- 🐛 **GitHub Issues** - Bug reports and feature requests
- 💬 **Discord Community** - Real-time help and discussions: https://discord.gg/alphabetcartel
- 📧 **Email Support** - Direct contact for urgent issues
- 📖 **Documentation** - Comprehensive guides and references

**Community Resources:**
- 🎥 **Video Tutorials** - Setup and usage walkthroughs  
- 📝 **Blog Posts** - Best practices and case studies
- 🛠️ **Community Tools** - User-contributed utilities and extensions
- 📊 **Performance Benchmarks** - Community testing results

**Contributing:**
- 🤝 **Code Contributions** - Features, bug fixes, improvements
- 📚 **Documentation** - Help improve guides and references
- 🧪 **Test Phrase Contributions** - Add more community-specific phrases
- 🎨 **Dashboard Components** - UI/UX improvements
- 🐛 **Bug Reports** - Help identify and fix issues

---

## 🙏 Acknowledgments

### Technical Contributors
- **Anthropic** - Claude 4 Sonnet API and exceptional documentation
- **Discord.py Community** - Excellent library and slash command guidance
- **Open Source Community** - Libraries and tools that make this possible

### Community Contributors
- **The Alphabet Cartel Crisis Response Team** - Extensive testing, feedback, and validation
- **Community Members** - Language pattern identification and real-world testing
- **Beta Testers** - Early adopters who refined the testing framework

### Research Partners
- **AI/ML Research Community** - Foundational work in depression detection and natural language processing
- **Crisis Intervention Specialists** - Insights into effective mental health crisis response
- **LGBTQIA+ Advocacy Groups** - Guidance on community-specific language and cultural sensitivity

---

## 📄 License & Legal

This project is part of **The Alphabet Cartel's** Ash ecosystem and is available under the MIT License. See the [LICENSE](LICENSE) file for complete details.

**Usage Rights:**
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use

**Limitations:**
- ❌ Liability
- ❌ Warranty

---

**💡 Quick Start Summary:**
1. Clone repository: `git clone https://github.com/The-Alphabet-Cartel/ash-thrash.git`
2. Setup environment: `bash setup.sh`
3. Start services: `docker-compose up -d`
4. Run first test: `docker-compose exec ash-thrash python src/comprehensive_testing.py`
5. Check results: `curl http://localhost:8884/api/test/status`

*"Thrashing the system so it never fails when it matters most."*

---

*Built with 🖤 for chosen family support*

**The Alphabet Cartel** - Crisis Detection Testing Team  
**Repository:** https://github.com/The-Alphabet-Cartel/ash-thrash  
**Community:** https://discord.gg/alphabetcartel