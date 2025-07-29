# Ash-Thrash: Comprehensive Crisis Detection Testing Suite

[![GitHub Issues](https://img.shields.io/github/issues/The-Alphabet-Cartel/ash-thrash)](https://github.com/The-Alphabet-Cartel/ash-thrash/issues)
[![GitHub License](https://img.shields.io/github/license/The-Alphabet-Cartel/ash-thrash)](https://github.com/The-Alphabet-Cartel/ash-thrash/blob/main/LICENSE)
[![Discord](https://img.shields.io/discord/your-discord-id?color=7289da&logo=discord&logoColor=white)](https://discord.gg/alphabetcartel)

**Ash-Thrash** is the comprehensive testing suite for the Ash crisis detection ecosystem, featuring 350 carefully crafted test phrases designed to validate crisis detection accuracy in LGBTQIA+ community contexts. Part of The Alphabet Cartel's commitment to building safe, inclusive gaming communities through technology.

---

## 🎯 Project Overview

### Core Mission
Ash-Thrash ensures the reliability and accuracy of crisis detection across the Ash ecosystem by providing comprehensive testing capabilities that validate real-world performance while maintaining community safety standards.

### Key Features
- **350 Test Phrases** across 7 carefully designed crisis categories
- **REST API** with complete endpoint coverage (port 8884)
- **Docker-Based Deployment** optimized for dedicated server infrastructure
- **Automated Scheduling** with configurable test intervals
- **Dashboard Integration** components for ash-dash
- **Real-time Monitoring** with health checks and alerting
- **Historical Analytics** with detailed failure analysis

---

## 🏗️ Architecture Overview

### System Components
- **Testing Engine**: Core 350-phrase validation system
- **REST API Server**: Comprehensive API with monitoring endpoints
- **Results Storage**: Persistent storage with backup capabilities
- **Dashboard Integration**: Components for seamless ash-dash embedding
- **Health Monitoring**: Real-time system status and alerting

### Integration Points
- **Ash-NLP Server** (10.20.30.253:8881): Primary NLP processing
- **Ash-Dashboard** (10.20.30.253:8883): Results visualization
- **Ash-Bot** (10.20.30.253:8882): Production system validation

---

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** installed
- **Network Access** to Ash NLP server (10.20.30.253:8881)
- **Python 3.11+** for local development
- **Git** for repository management

### One-Command Deployment

```bash
# Clone repository
git clone https://github.com/the-alphabet-cartel/ash-thrash.git
cd ash-thrash

# Configure environment
cp .env.template .env
# Edit .env with your server details (default: 10.20.30.253:8881)

# Deploy with Docker
docker-compose up -d

# Run initial validation
docker-compose exec ash-thrash python src/quick_validation.py

# Check system status
curl http://localhost:8884/api/health
```

### Environment Configuration

**Required .env Variables:**
```bash
# NLP Server Configuration
GLOBAL_NLP_API_URL=http://10.20.30.253:8881
NLP_API_TIMEOUT=30

# API Configuration
THRASH_API_HOST=0.0.0.0
GLOBAL_THRASH_API_PORT=8884
GLOBAL_ENABLE_DEBUG_MODE=false

# Testing Configuration
THRASH_ENABLE_SCHEDULED_TESTS=true
THRASH_COMPREHENSIVE_TEST_INTERVAL=daily
THRASH_QUICK_TEST_INTERVAL=hourly
```

---

## 🧪 Testing Capabilities

### Test Categories

**Crisis Detection Framework:**
1. **Immediate Crisis (Priority 1)** - Active suicidal ideation
2. **High Risk (Priority 2)** - Severe depression with concerning indicators
3. **Medium Risk (Priority 3)** - Notable emotional distress
4. **Low Risk (Priority 4)** - Minor concerns requiring gentle check-in
5. **General Support (Priority 5)** - Everyday community support needs
6. **False Positives** - Phrases that should NOT trigger alerts
7. **Community Specific** - LGBTQIA+ terminology and context

### Test Execution Options

**Quick Validation (10 phrases, ~30 seconds):**
```bash
# Docker execution
docker-compose exec ash-thrash python src/quick_validation.py

# Local execution
python src/quick_validation.py

# API execution
curl -X POST http://localhost:8884/api/test/quick
```

**Comprehensive Testing (350 phrases, ~5-10 minutes):**
```bash
# Docker execution
docker-compose exec ash-thrash python src/comprehensive_testing.py

# Local execution
python src/comprehensive_testing.py

# API execution
curl -X POST http://localhost:8884/api/test/comprehensive
```

**Category-Specific Testing:**
```bash
# Test specific category
curl -X POST http://localhost:8884/api/test/category \
  -H "Content-Type: application/json" \
  -d '{"category": "immediate_crisis", "phrases": 50}'
```

---

## 🔌 API Reference

### Health & Status Endpoints

**System Health:**
```bash
GET /health
GET /api/health
GET /api/status
```

**Service Dependencies:**
```bash
GET /api/health/nlp          # NLP server connectivity
GET /api/health/database     # Database status
GET /api/health/storage      # File system status
```

### Test Execution Endpoints

**Run Tests:**
```bash
POST /api/test/quick                    # Quick validation
POST /api/test/comprehensive            # Full test suite
POST /api/test/category                 # Category-specific testing
GET  /api/test/status                   # Current test status
```

**Test Management:**
```bash
GET  /api/test/results/latest           # Latest test results
GET  /api/test/results/{test_id}        # Specific test results
GET  /api/test/history                  # Test execution history
POST /api/test/schedule                 # Schedule recurring tests
```

### Analytics & Reporting

**Results Analysis:**
```bash
GET /api/analytics/summary              # Performance summary
GET /api/analytics/trends               # Historical trends
GET /api/analytics/categories           # Category performance
GET /api/analytics/failures             # Detailed failure analysis
```

**Data Export:**
```bash
GET /api/export/results/{format}        # Export results (json, csv, xlsx)
GET /api/export/report/{test_id}        # Generate detailed report
```

---

## 📊 Dashboard Integration

### Ash-Dashboard Components

**Real-time Widgets:**
- **System Status Widget**: Live health monitoring
- **Test Progress Widget**: Current test execution status
- **Performance Metrics**: Success rates and response times
- **Alert Dashboard**: Failed test notifications

**Historical Analytics:**
- **Trend Charts**: Performance over time
- **Category Analysis**: Success rates by crisis category
- **Comparative Analysis**: Performance comparisons
- **Detailed Reports**: Comprehensive test analysis

### Integration Setup

**Dashboard Routes (auto-configured):**
```javascript
// Dashboard integration endpoints
/dashboard/ash-thrash/status           // Real-time status
/dashboard/ash-thrash/results          // Latest results
/dashboard/ash-thrash/analytics        // Performance analytics
/dashboard/ash-thrash/alerts           // System alerts
```

---

## 🐳 Docker Deployment

### Production Configuration

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  ash-thrash:
    build: .
    container_name: ash-thrash
    ports:
      - "8884:8884"
    environment:
      - GLOBAL_NLP_API_URL=http://10.20.30.253:8881
      - GLOBAL_THRASH_API_PORT=8884
      - THRASH_ENABLE_SCHEDULED_TESTS=true
    volumes:
      - ./results:/app/results
      - ./config:/app/config
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8884/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    depends_on:
      - ash-database
    networks:
      - ash-network

  ash-database:
    image: postgres:15
    container_name: ash-thrash-db
    environment:
      - GLOBAL_POSTGRES_DB=ash_thrash
      - GLOBAL_POSTGRES_USER=ash
      - GLOBAL_POSTGRES_PASSWORD=${DATABASE_PASSWORD}
    volumes:
      - ash_thrash_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - ash-network

volumes:
  ash_thrash_data:

networks:
  ash-network:
    external: true
```

### Server Specifications

**Dedicated Server (10.20.30.253):**
- **OS**: Debian 12 Linux
- **CPU**: AMD Ryzen 7 5800X
- **RAM**: 64GB
- **GPU**: NVIDIA RTX 3060
- **Storage**: High-performance SSD
- **Network**: Internal network (10.20.30.0/24)

### Service Architecture

**Port Allocation:**
- **Ash-Thrash API**: 8884
- **Ash-NLP Server**: 8881
- **Ash-Dashboard**: 8883
- **Ash-Bot**: 8882

---

## 📈 Performance & Monitoring

### Success Rate Targets

**Category Performance Goals:**
- **Immediate Crisis**: 95%+ detection rate
- **High Risk**: 90%+ detection rate
- **Medium Risk**: 85%+ detection rate
- **Low Risk**: 80%+ detection rate
- **False Positives**: <5% false positive rate
- **Community Specific**: 90%+ contextual accuracy

### Monitoring Capabilities

**Real-time Metrics:**
- Test execution performance
- NLP server response times
- Memory and CPU utilization
- Error rates and failure patterns

**Alerting System:**
- Failed test notifications
- Performance degradation alerts
- System health warnings
- Scheduled test failures

### Performance Optimization

**Caching Strategy:**
- Results caching for dashboard queries
- Phrase preprocessing optimization
- Database query optimization
- API response caching

**Resource Management:**
- Automatic cleanup of old results
- Memory usage optimization
- Concurrent test execution limits
- Database connection pooling

---

## 🔧 Development Setup

### Local Development

**Prerequisites:**
```bash
# Install Python 3.11+
python --version

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup environment
cp .env.template .env
# Configure your local settings
```

**Development Workflow:**
```bash
# Run tests locally
python src/quick_validation.py

# Start development API server
python src/api/server.py --debug

# Run test suite
pytest tests/ -v

# Code formatting
black src/
flake8 src/
```

### Testing Framework

**Unit Tests:**
```bash
# Run unit tests
pytest tests/unit/ -v

# Test with coverage
pytest tests/ --cov=src --cov-report=html
```

**Integration Tests:**
```bash
# Test NLP integration
pytest tests/integration/test_nlp_integration.py

# Test API endpoints
pytest tests/integration/test_api.py

# Test database operations
pytest tests/integration/test_database.py
```

### Contribution Guidelines

**Development Process:**
1. **Fork** repository and create feature branch
2. **Implement** changes with comprehensive tests
3. **Validate** changes with full test suite
4. **Update** documentation as needed
5. **Submit** pull request with detailed description

**Code Standards:**
- **Python**: PEP 8 compliance with Black formatting
- **Documentation**: Comprehensive docstrings and comments
- **Testing**: 90%+ test coverage for new features
- **Security**: No hardcoded credentials or sensitive data

---

## 📚 Documentation Suite

### User Documentation
- **[Team Guide](docs/team/team_guide_v2_1.md)** - Crisis response team procedures
- **[Implementation Guide](docs/tech/implementation_v2_1.md)** - Technical setup and configuration
- **[API Documentation](docs/tech/API_v2_1.md)** - Complete API reference
- **[Troubleshooting Guide](docs/tech/troubleshooting_v2_1.md)** - Problem diagnosis and resolution

### Technical Documentation
- **[Deployment Guide](docs/deployment_v2_1.md)** - Production deployment procedures
- **[Development Guide](docs/tech/development_v2_1.md)** - Development environment setup
- **[Architecture Guide](docs/tech/architecture_v2_1.md)** - System design and components
- **[Security Guide](docs/tech/security_v2_1.md)** - Security configuration and best practices

### Release Documentation
- **[GitHub Release Guide](docs/github_release_v2_1.md)** - Release procedures and changelog
- **[Migration Guide](docs/migration_v2_1.md)** - Version migration procedures
- **[Ecosystem Setup](docs/tech/ecosystem_setup_v2_1.md)** - Complete ecosystem deployment

---

## 🛠️ Advanced Configuration

### Scheduled Testing

**Cron Configuration:**
```bash
# Daily comprehensive testing at 2 AM
0 2 * * * docker-compose exec ash-thrash python src/comprehensive_testing.py

# Hourly quick validation
0 * * * * docker-compose exec ash-thrash python src/quick_validation.py

# Weekly performance report
0 8 * * 1 docker-compose exec ash-thrash python src/generate_weekly_report.py
```

### Custom Test Categories

**Configuration File (config/custom_categories.json):**
```json
{
  "custom_categories": {
    "gaming_specific": {
      "description": "Gaming community crisis indicators",
      "target_success_rate": 0.85,
      "priority_level": 3
    },
    "identity_crisis": {
      "description": "Identity-related distress in LGBTQIA+ contexts",
      "target_success_rate": 0.90,
      "priority_level": 2
    }
  }
}
```

### Integration Extensions

**Webhook Notifications:**
```bash
# Configure webhook URLs in .env
WEBHOOK_URL_FAILURES=https://your-webhook.com/failures
WEBHOOK_URL_SUCCESS=https://your-webhook.com/success
ENABLE_WEBHOOK_NOTIFICATIONS=true
```

**External Analytics:**
```bash
# Integration with external monitoring
DATADOG_API_KEY=your-datadog-key
PROMETHEUS_ENABLED=true
GRAFANA_INTEGRATION=true
```

---

## 🔐 Security & Privacy

### Data Protection

**Privacy Principles:**
- **No Personal Data**: Test phrases contain no personal information
- **Local Storage**: All data stored on dedicated server
- **Secure Transmission**: HTTPS for all external communications
- **Access Control**: Network-level access restrictions

**Security Configuration:**
```bash
# Network security
iptables -A INPUT -p tcp --dport 8884 -s 10.20.30.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 8884 -j DROP

# File permissions
chmod 600 .env
chmod 700 results/
chmod 700 logs/
```

### Audit and Compliance

**Logging Strategy:**
- **Access Logs**: All API access logged
- **Error Logs**: Comprehensive error tracking
- **Audit Trail**: Test execution history
- **Security Events**: Failed authentication attempts

**Data Retention:**
- **Test Results**: 90 days (configurable)
- **Logs**: 30 days (configurable)
- **Backups**: 1 year (automated rotation)
- **Analytics**: Indefinite (anonymized)

---

## 📞 Support & Community

### Support Channels

**Primary Support:**
- **Discord**: [#tech-support](https://discord.gg/alphabetcartel) - Community support
- **GitHub Issues**: [ash-thrash/issues](https://github.com/the-alphabet-cartel/ash-thrash/issues) - Bug reports and feature requests
- **Documentation**: Comprehensive guides and references

**Community Resources:**
- **The Alphabet Cartel Discord**: https://discord.gg/alphabetcartel
- **Website**: https://alphabetcartel.org
- **GitHub Organization**: https://github.com/the-alphabet-cartel

### Emergency Procedures

**Critical System Failures:**
1. **Immediate**: Check system health endpoints
2. **Escalation**: Post in Discord #crisis-response
3. **Documentation**: Use troubleshooting guide
4. **Recovery**: Follow emergency recovery procedures

**Crisis Response Integration:**
- Ash-Thrash validates the systems that protect our community
- Failed tests may indicate compromised crisis detection
- Immediate notification procedures for critical failures

---

## 🗓️ Roadmap & Future Development

### Version 2.2 (Q3 2025)
- **Enhanced Analytics**: Machine learning-powered trend analysis
- **Multi-language Support**: Testing for non-English crisis detection
- **Advanced Scheduling**: Dynamic test scheduling based on system load
- **Performance Optimization**: Sub-second response times for all tests

### Version 3.0 (Q1 2026)
- **Distributed Testing**: Multi-server test execution
- **Real-time Streaming**: Live test result streaming
- **Advanced ML Integration**: Automated test phrase generation
- **Federation Support**: Cross-community testing capabilities

### Long-term Vision
- **Industry Standard**: Become the standard for crisis detection testing
- **Research Platform**: Support academic research on crisis intervention
- **Open Source Ecosystem**: Contribute to broader mental health technology

---

## 📜 License & Attribution

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Attribution
- **The Alphabet Cartel** - Project development and community support
- **Contributors** - Individual contributors listed in CONTRIBUTORS.md
- **Dependencies** - Third-party libraries listed in requirements.txt

### Acknowledgments
- **LGBTQIA+ Community** - Feedback and real-world validation
- **Crisis Response Volunteers** - Testing and improvement suggestions
- **Open Source Community** - Tools and libraries that make this possible

---

## 📊 Project Statistics

### Current Metrics
- **Test Phrases**: 350 across 7 categories
- **API Endpoints**: 25+ comprehensive endpoints
- **Response Time**: <500ms average for quick tests
- **Uptime Target**: 99.9% availability
- **Test Coverage**: 95%+ code coverage

### Community Impact
- **Communities Served**: The Alphabet Cartel and growing
- **Tests Executed**: Thousands of validation runs
- **Crisis Situations Validated**: Comprehensive coverage of crisis scenarios
- **Response Accuracy**: Continuously improving detection rates

---

**Built with 🖤 for chosen family everywhere.**

**The Alphabet Cartel** - Building inclusive gaming communities through technology.

**Discord:** https://discord.gg/alphabetcartel | **Website:** https://alphabetcartel.org | **GitHub:** https://github.com/the-alphabet-cartel