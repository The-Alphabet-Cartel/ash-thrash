# Ash-Thrash - Testing Suite

**Part of the Ash Ecosystem** | **Main Repository:** https://github.com/the-alphabet-cartel/ash

This repository contains **only the testing suite component** of the Ash crisis detection system. For the complete ecosystem including Discord bot, NLP server, and dashboard, see the [main Ash repository](https://github.com/the-alphabet-cartel/ash).

**Discord Community:** https://discord.gg/alphabetcartel  
**Website:** http://alphabetcartel.org  
**Organization:** https://github.com/the-alphabet-cartel

## 🧪 About Ash-Thrash

Ash-Thrash is the comprehensive testing and quality assurance system for The Alphabet Cartel's crisis detection ecosystem. It validates crisis detection accuracy through a 350-phrase test suite, ensuring the reliability and effectiveness of the hybrid keyword-NLP detection system.

### 🏗️ Architecture Position

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Discord Bot   │◄──►│   NLP Server    │◄──►│   Dashboard     │
│   (ash-bot)     │    │   (ash-nlp)     │    │   (ash-dash)    │
│                 │    │                 │    │                 │
│ 10.20.30.253    │    │ 10.20.30.16     │    │ 10.20.30.16     │
│ Port: 8882      │    │ Port: 8881      │    │ Port: 8883      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                 ▲
                                 │
                       ┌─────────────────┐
                       │  Testing Suite  │
                       │   (THIS REPO)   │
                       │                 │
                       │ 10.20.30.16     │
                       │ Port: 8884      │
                       └─────────────────┘
```

## 🚀 Quick Start

### For Testing Development
If you're working on the testing suite specifically:

```bash
# Clone this repository
git clone https://github.com/the-alphabet-cartel/ash-thrash.git
cd ash-thrash

# Setup development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

# Configure environment
cp .env.template .env
# Edit .env with NLP server details

# Run quick validation test
python src/quick_validation.py

# Run comprehensive test suite
python src/comprehensive_testing.py
```

### For Complete Ecosystem
If you need the full Ash system (recommended):

```bash
# Clone the main ecosystem repository
git clone --recursive https://github.com/the-alphabet-cartel/ash.git
cd ash

# Follow setup instructions in main repository
# This includes ash-thrash as a submodule along with all other components
```

## 🔧 Core Features

### Comprehensive Testing
- **350-Phrase Test Suite**: Extensive validation across all crisis categories
- **Quick Validation**: 10-phrase subset for rapid development testing
- **Automated Scheduling**: Configurable test execution at regular intervals
- **Regression Testing**: Continuous validation that changes don't break existing functionality

### Quality Assurance
- **Goal Achievement Tracking**: Visual progress toward accuracy targets
- **Detailed Failure Analysis**: Granular reporting on detection failures
- **Performance Benchmarking**: Response time and throughput measurements
- **Historical Trend Analysis**: Long-term accuracy and performance tracking

### Integration Testing
- **Multi-Component Validation**: Tests entire crisis detection pipeline
- **API Stress Testing**: Load testing for production reliability
- **Keyword Synchronization**: Ensures keyword consistency with ash-bot
- **Dashboard Integration**: Real-time test results in ash-dash

## 📦 Repository Structure

```
ash-thrash/                       # THIS REPOSITORY
├── src/                          # Main application source
│   ├── comprehensive_testing.py  # 350-phrase comprehensive test
│   ├── quick_validation.py       # 10-phrase quick validation
│   ├── api/                      # FastAPI server for test management
│   │   ├── main.py              # API server entry point
│   │   ├── routes/              # API endpoint definitions
│   │   └── models/              # API data models
│   ├── test_data/               # Test phrase definitions and categories
│   │   ├── categories/          # Crisis category definitions
│   │   ├── phrases/             # Test phrase collections
│   │   └── goals/               # Target accuracy goals
│   ├── keywords/                # Mirror of ash-bot keyword structure
│   │   ├── high_crisis.py       # High-priority crisis keywords
│   │   ├── medium_crisis.py     # Medium-priority crisis keywords
│   │   └── low_crisis.py        # Low-priority crisis keywords
│   ├── utils/                   # Utility functions
│   │   ├── nlp_client.py        # NLP server communication
│   │   ├── test_runner.py       # Test execution engine
│   │   ├── report_generator.py  # Result reporting
│   │   └── validators.py        # Test data validation
│   └── analytics/               # Performance analysis tools
├── results/                     # Test result storage
│   ├── comprehensive/           # Full test suite results
│   ├── quick_validation/        # Quick test results
│   ├── reports/                 # Generated analysis reports
│   └── backups/                 # Historical result archives
├── config/                      # Configuration files
│   ├── testing_goals.json       # Accuracy targets by category
│   ├── categories.json          # Test category definitions
│   └── scheduling.json          # Automated test scheduling
├── dashboard/                   # Ash-dash integration components
│   ├── routes.js                # Dashboard API routes
│   ├── styles/                  # CSS styling for dashboard
│   └── templates/               # HTML templates for results
├── scripts/                     # Utility and automation scripts
├── tests/                       # Unit tests for testing suite
├── docs/                        # Testing-specific documentation
├── docker/                      # Docker configuration
├── .env.template                # Environment configuration template
├── docker-compose.yml           # Docker deployment configuration
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
└── README.md                    # This file
```

## 🛠️ Development

### Prerequisites
- Python 3.9+
- Access to ash-nlp server (for testing)
- Docker (for containerized deployment)
- FastAPI knowledge for API development

### Environment Configuration

Create `.env` file from template:
```bash
cp .env.template .env
```

Required environment variables:
```bash
# NLP Server Configuration
NLP_SERVER_HOST=10.20.30.16
NLP_SERVER_PORT=8881
NLP_SERVER_URL=http://10.20.30.16:8881
NLP_CONNECTION_TIMEOUT=30

# Testing Configuration
MAX_CONCURRENT_TESTS=8
TEST_TIMEOUT_SECONDS=15
RESULTS_RETENTION_DAYS=180
ENABLE_DETAILED_LOGGING=true

# API Server Configuration
API_PORT=8884
API_HOST=0.0.0.0
ENVIRONMENT=development

# Dashboard Integration
DASH_API_URL=http://10.20.30.16:8883
ENABLE_DASHBOARD_SYNC=true

# Performance Settings (Optimized for Ryzen 7 7700X)
ENABLE_PARALLEL_TESTING=true
WORKER_POOL_SIZE=8
BATCH_SIZE=50
```

### Testing Suite Goals

**Accuracy Targets:**
```json
{
  "comprehensive_test": {
    "overall_accuracy": 95.0,
    "high_crisis_detection": 98.0,
    "medium_crisis_detection": 95.0,
    "low_crisis_detection": 90.0,
    "false_positive_rate": 2.0
  },
  "performance_targets": {
    "average_response_time_ms": 500,
    "max_response_time_ms": 2000,
    "throughput_requests_per_second": 20
  }
}
```

### Running Tests

**Quick Validation (10 phrases):**
```bash
# Basic quick test
python src/quick_validation.py

# Quick test with detailed output
python src/quick_validation.py --verbose

# Quick test for specific category
python src/quick_validation.py --category high_crisis
```

**Comprehensive Testing (350 phrases):**
```bash
# Full comprehensive test
python src/comprehensive_testing.py

# Comprehensive test with performance analysis
python src/comprehensive_testing.py --include-performance

# Comprehensive test with custom concurrency
MAX_CONCURRENT_TESTS=12 python src/comprehensive_testing.py
```

**API Server:**
```bash
# Start testing API server
python src/api/main.py

# Access API documentation
# http://localhost:8884/docs
```

### Docker Deployment

```bash
# Build and run locally
docker-compose up --build

# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Run tests in container
docker-compose exec ash-thrash python src/comprehensive_testing.py
```

## 🔗 Integration with Ash Ecosystem

### NLP Server Testing
- **Analysis Validation**: Validates NLP server crisis detection accuracy
- **Performance Testing**: Measures response times and throughput
- **Stress Testing**: Tests NLP server under high load conditions
- **Error Handling**: Validates graceful failure modes

### Dashboard Integration
- **Real-time Results**: Live test results displayed in ash-dash
- **Historical Analytics**: Long-term trend analysis and reporting
- **Alert Integration**: Notifications when test accuracy drops below thresholds
- **One-click Testing**: Trigger tests directly from dashboard interface

### Bot Keyword Synchronization
- **Keyword Mirroring**: Maintains exact copy of ash-bot keyword structure
- **Consistency Validation**: Ensures keyword detection matches bot behavior
- **Update Synchronization**: Automated sync when keywords are modified
- **Hybrid Testing**: Validates both keyword and NLP detection paths

## 📊 Test Categories & Phrases

### Crisis Categories

**High Crisis (Immediate Intervention):**
- Suicidal ideation and self-harm indicators
- Immediate danger statements
- Crisis escalation language
- Emergency intervention triggers

**Medium Crisis (Close Monitoring):**
- Depression and anxiety indicators
- Relationship and social difficulties
- Identity and acceptance struggles
- Support-seeking behaviors

**Low Crisis (Wellness Check):**
- General emotional distress
- Mild anxiety or worry
- Social connection needs
- Resource and guidance requests

### Test Phrase Management

**Phrase Development:**
```python
# Example test phrase structure
{
    "phrase": "Example crisis-indicating text",
    "category": "high_crisis",
    "expected_detection": True,
    "confidence_threshold": 0.8,
    "context_requirements": [],
    "tags": ["depression", "urgent"]
}
```

**Quality Assurance:**
- **Community Validation**: Test phrases reviewed by crisis response teams
- **Ethical Review**: Ensures test phrases don't perpetuate harmful stereotypes
- **Diversity Coverage**: Represents diverse LGBTQIA+ experiences and language
- **Regular Updates**: Phrases updated based on community feedback and trends

## 🧪 Testing Features

### Automated Testing
```bash
# Schedule comprehensive tests every 6 hours
COMPREHENSIVE_TEST_SCHEDULE="0 */6 * * *"

# Schedule quick validation every hour
QUICK_VALIDATION_SCHEDULE="0 * * * *"

# Run scheduled tests
python scripts/run_scheduled_tests.py
```

### Performance Analysis
```bash
# Generate performance report
python src/analytics/performance_analysis.py

# Benchmark NLP server performance
python scripts/benchmark_nlp_server.py

# Analyze response time trends
python src/analytics/response_time_analysis.py
```

### Result Management
```bash
# Export test results to CSV
python scripts/export_results.py --format csv

# Generate detailed failure report
python src/analytics/failure_analysis.py

# Archive old results
python scripts/archive_results.py --days 180
```

## 📈 Performance & Monitoring

### Performance Specifications
- **Server**: Windows 11 (10.20.30.16)
- **Resources**: 4GB RAM, 2 CPU cores
- **Concurrent Tests**: 8 parallel test executions
- **Test Execution Time**: ~15 minutes for comprehensive suite
- **API Response Time**: <100ms for test status queries

### Monitoring
- **Health Endpoint**: `http://10.20.30.16:8884/health`
- **Test Status API**: Real-time test execution monitoring
- **Performance Metrics**: Detailed timing and accuracy statistics
- **Error Tracking**: Comprehensive error logging and analysis

## 🤝 Contributing

### Development Process
1. **Fork this repository** (ash-thrash specifically)
2. **Create feature branch** for your changes
3. **Add comprehensive tests** for new functionality
4. **Validate test phrases** with crisis response teams
5. **Test integration** with ash-nlp and ash-dash
6. **Update documentation** as needed
7. **Submit pull request** to this repository

### Test Development
- **Phrase Validation**: Work with community members to validate test phrases
- **Ethical Review**: Ensure test phrases are appropriate and respectful
- **Accuracy Testing**: Validate that new tests improve overall detection accuracy
- **Performance Impact**: Ensure changes don't significantly impact test execution time

### Main Ecosystem
For changes affecting multiple components, coordinate with the [main ash repository](https://github.com/the-alphabet-cartel/ash) which includes this repository as a submodule.

## 📞 Support

### Testing-Specific Issues
- **GitHub Issues**: [ash-thrash/issues](https://github.com/the-alphabet-cartel/ash-thrash/issues)
- **Discord Support**: #ash-thrash-support in https://discord.gg/alphabetcartel

### Ecosystem-Wide Issues
- **Main Repository**: [ash/issues](https://github.com/the-alphabet-cartel/ash/issues)
- **General Discussion**: #tech-help in https://discord.gg/alphabetcartel

### Test Results Issues
- **Accuracy Problems**: Include test results and NLP server logs
- **Performance Issues**: Include timing data and system specifications
- **Integration Issues**: Include API response details and error logs

## 📜 License

This project is part of The Alphabet Cartel's open-source initiatives. See [LICENSE](LICENSE) file for details.

---

## ⚠️ Important Notes

### Repository Scope
This repository contains **ONLY the testing suite component**. For:
- **Discord Bot**: See [ash-bot](https://github.com/the-alphabet-cartel/ash-bot)
- **NLP Server**: See [ash-nlp](https://github.com/the-alphabet-cartel/ash-nlp)
- **Analytics Dashboard**: See [ash-dash](https://github.com/the-alphabet-cartel/ash-dash)
- **Complete System**: See [main ash repository](https://github.com/the-alphabet-cartel/ash)

### Development Recommendations
- **New Contributors**: Start with the [main ash repository](https://github.com/the-alphabet-cartel/ash) for complete system overview
- **Testing-Specific Work**: Use this repository for test development and quality assurance
- **System Integration**: Validate changes against the full ecosystem

### Sensitivity & Ethics
This testing suite deals with crisis-related content and mental health scenarios. All test phrase development and validation must be conducted with appropriate sensitivity and ethical consideration for LGBTQIA+ community members.

### Production Testing
Production testing should be conducted during low-traffic periods and with appropriate monitoring to ensure it doesn't impact live crisis detection capabilities.

---

**Built with 🖤 for LGBTQIA+ gaming communities by [The Alphabet Cartel](https://discord.gg/alphabetcartel)**