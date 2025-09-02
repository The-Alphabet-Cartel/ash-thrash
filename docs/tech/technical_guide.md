<!-- ash-thrash/docs/tech/technical_guide.md -->
<!--
Technical Guide for Ash-Thrash Service
FILE VERSION: v3.1-3a-1
LAST MODIFIED: 2025-09-01
CLEAN ARCHITECTURE: v3.1
-->
# Ash-Thrash v3.1 Technical Guide

**Repository**: https://github.com/the-alphabet-cartel/ash-thrash  
**Project**: Ash-Thrash v3.1  
**Community**: The Alphabet Cartel - [Discord](https://discord.gg/alphabetcartel) | [Website](http://alphabetcartel.org)  
**FILE VERSION**: v3.1-3a-1  
**LAST UPDATED**: 2025-09-01  
**CLEAN ARCHITECTURE**: v3.1

---

## 🎯 Technical Overview

Ash-Thrash v3.1 is a comprehensive testing and tuning system for the Ash NLP crisis detection service. Built with Clean Architecture v3.1 principles, it provides production-ready testing capabilities with advanced AI-driven tuning intelligence.

## 🏗️ System Architecture

### Core Design Principles

#### Clean Architecture v3.1 Compliance
- **Factory Function Pattern**: All managers use factory functions for initialization
- **Dependency Injection**: Clean separation of concerns with proper dependency management  
- **Phase-Additive Development**: New features add functionality without removing existing capabilities
- **JSON Configuration + Environment Overrides**: Externalized configuration with runtime flexibility
- **Production Resilience**: Graceful error handling with operational continuity
- **File Versioning**: Comprehensive version tracking for maintainability

#### Safety-First Architecture
- **False Negative Weighting**: 3x penalty for missing real crises
- **Early Termination**: Configurable halt on performance degradation
- **Community Focus**: LGBTQIA+ specific safety considerations
- **Comprehensive Logging**: Detailed tracking for debugging and monitoring

### 🏛️ Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Ash-Thrash v3.1 Architecture             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌──────────────────┐                │
│  │   main.py       │◄──►│   analyze.py     │                │
│  │ (Entry Points)  │    │ (Standalone)     │                │
│  └─────────────────┘    └──────────────────┘                │
│           │                       │                         │
│           ▼                       ▼                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                Manager Layer (Clean v3.1)              │ │
│  │                                                        │ │
│  │ ┌─────────────────┐  ┌─────────────────┐               │ │
│  │ │UnifiedConfig    │  │LoggingConfig    │               │ │
│  │ │Manager          │  │Manager          │               │ │
│  │ └─────────────────┘  └─────────────────┘               │ │
│  │                                                        │ │
│  │ ┌─────────────────┐  ┌─────────────────┐               │ │
│  │ │TestEngine       │  │NLPClient        │               │ │
│  │ │Manager          │  │Manager          │               │ │
│  │ └─────────────────┘  └─────────────────┘               │ │
│  │                                                        │ │
│  │ ┌─────────────────┐  ┌─────────────────┐               │ │
│  │ │Results          │  │AnalyzeResults   │               │ │
│  │ │Manager          │  │Manager          │               │ │
│  │ └─────────────────┘  └─────────────────┘               │ │
│  │                                                        │ │
│  │ ┌─────────────────┐                                    │ │
│  │ │TuningSuggestions│  (Phase 3a - Advanced Intelligence)│ │
│  │ │Manager          │                                    │ │
│  │ └─────────────────┘                                    │ │
│  └────────────────────────────────────────────────────────┘ │
│           │                                                 │
│           ▼                                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Configuration Layer                       │ │
│  │                                                        │ │
│  │ ┌─────────────────┐  ┌─────────────────┐               │ │
│  │ │JSON Config      │  │Environment      │               │ │
│  │ │Files            │  │Variables        │               │ │
│  │ └─────────────────┘  └─────────────────┘               │ │
│  └────────────────────────────────────────────────────────┘ │
│           │                                                 │
│           ▼                                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │               Data & Integration Layer                 │ │
│  │                                                        │ │
│  │ ┌─────────────────┐  ┌─────────────────┐               │ │
│  │ │Test Phrases     │  │NLP Server       │               │ │
│  │ │(7 Categories)   │  │(172.20.0.11)    │               │ │
│  │ └─────────────────┘  └─────────────────┘               │ │
│  │                                                        │ │
│  │ ┌─────────────────┐  ┌─────────────────┐               │ │
│  │ │Results/Reports  │  │Docker Network   │               │ │
│  │ │(Persistent)     │  │(Internal)       │               │ │
│  │ └─────────────────┘  └─────────────────┘               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 📁 File Structure Deep Dive

```
ash-thrash/
├── main.py                                    # Primary execution entry point
├── analyze.py                                 # Standalone analysis capabilities
├── startup.py                                 # Container initialization
├── managers/                                  # Clean Architecture v3.1 managers
│   ├── unified_config.py                      # Centralized configuration management
│   ├── logging_config.py                      # Logging system configuration
│   ├── test_engine.py                         # Core testing logic and execution
│   ├── nlp_client.py                          # NLP server communication layer
│   ├── results_manager.py                     # Test result processing and storage
│   ├── analyze_results.py                     # Results analysis and reporting
│   └── tuning_suggestions.py                  # Advanced AI tuning intelligence
├── config/                                    # JSON configuration files
│   ├── test_settings.json                     # Test execution configuration
│   ├── logging_settings.json                  # Logging system settings
│   ├── category_config.json                   # Test category definitions
│   └── threshold_mappings.json                # NLP threshold variable mappings
├── test_phrases/                              # Test phrase datasets (345 total)
│   ├── definite_high_crisis.json              # High crisis test phrases (50)
│   ├── definite_medium_crisis.json            # Medium crisis test phrases (50)
│   ├── definite_low_crisis.json               # Low crisis test phrases (50)
│   ├── definite_none.json                     # No crisis test phrases (50)
│   ├── maybe_high_medium.json                 # High/Medium bidirectional (50)
│   ├── maybe_medium_low.json                  # Medium/Low bidirectional (50)
│   └── maybe_low_none.json                    # Low/None bidirectional (45)
├── results/                                   # Test execution results
│   ├── latest/                                # Most recent test results
│   ├── tuning_analysis/                       # Advanced tuning analysis files
│   └── historical/                            # Historical test data
├── reports/                                   # Generated markdown reports
│   ├── latest_run_summary.md                  # Comprehensive test results
│   ├── threshold_recommendations.md           # Tuning implementation guide
│   ├── historical_performance.md              # Performance trend analysis
│   └── recommended_thresholds_*.env           # Generated configuration files
├── logs/                                      # System and execution logs
├── docs/                                      # Documentation
│   ├── clean_architecture_charter.md          # Architecture requirements
│   ├── implementation_plan.md                 # Development roadmap
│   ├── team/
│   │   └── team_guide.md                      # Team usage guide
│   └── tech/
│       └── technical_guide.md                 # This file
├── docker-compose.yml                         # Container orchestration
├── Dockerfile                                 # Container definition
├── .env.template                              # Environment variable template
└── requirements.txt                           # Python dependencies
```

## 🔧 Technical Implementation

### Manager Pattern Implementation

#### Factory Function Pattern (Clean Architecture v3.1)
All managers must use factory functions for initialization:

```python
def create_test_engine_manager(config_manager, nlp_client) -> TestEngineManager:
    """Factory function for TestEngineManager - MANDATORY pattern"""
    return TestEngineManager(config_manager, nlp_client)

# Usage in main.py
test_engine = create_test_engine_manager(unified_config, nlp_client)
```

#### Dependency Injection
Managers receive dependencies through constructor parameters:

```python
class TestEngineManager:
    def __init__(self, config_manager: UnifiedConfigManager, nlp_client: NLPClientManager):
        """Clean dependency injection pattern"""
        self.config = config_manager
        self.nlp_client = nlp_client
        self.logger = logging.getLogger(__name__)
```

#### Configuration Management
JSON files provide defaults, environment variables provide overrides:

```json
{
  "test_execution": {
    "max_concurrent_tests": "${THRASH_MAX_CONCURRENT_TESTS}",
    "defaults": {
      "max_concurrent_tests": 3
    }
  }
}
```

### 🧪 Testing Engine Architecture

#### Core Testing Flow
```python
# Simplified testing flow
def run_test_suite(categories=None):
    1. Initialize managers via factory functions
    2. Verify NLP server connectivity
    3. Load test phrases from JSON files
    4. Execute tests with configurable concurrency
    5. Analyze results with safety-first weighting
    6. Generate comprehensive reports
    7. Provide tuning recommendations
```

#### Test Categories & Logic

**Definite Categories** (Exact Match Required):
```python
def validate_definite_result(expected, actual):
    """Exact match validation for definite categories"""
    return expected.lower() == actual.lower()
```

**Maybe Categories** (Bidirectional Acceptance):
```python
def validate_maybe_result(expected_list, actual):
    """Bidirectional validation for maybe categories"""
    return actual.lower() in [exp.lower() for exp in expected_list]
```

#### Safety-First Scoring
```python
def calculate_weighted_score(results):
    """False negatives weighted 3x more heavily than false positives"""
    false_negative_penalty = 3.0
    false_positive_penalty = 1.0
    
    for result in results:
        if result.is_false_negative:
            penalty = false_negative_penalty
        elif result.is_false_positive:
            penalty = false_positive_penalty
        else:
            penalty = 0.0
```

### 🧠 Advanced Tuning Intelligence (Phase 3a)

#### Threshold Mapping System
Maps test failures to specific NLP environment variables:

```json
{
  "majority_ensemble": {
    "definite_high_failures": {
      "primary_threshold": "NLP_THRESHOLD_MAJORITY_ENSEMBLE_CRITICAL",
      "secondary_threshold": "NLP_THRESHOLD_MAJORITY_CRISIS_TO_HIGH"
    }
  }
}
```

#### Confidence Assessment Algorithm
```python
def calculate_confidence_level(failure_count, total_tests, historical_data):
    """Determine confidence level for tuning recommendations"""
    consistency_score = analyze_historical_consistency(historical_data)
    failure_rate = failure_count / total_tests
    
    if consistency_score > 0.8 and failure_rate > 0.3:
        return "HIGH"
    elif consistency_score > 0.6 and failure_rate > 0.2:
        return "MEDIUM"
    else:
        return "LOW"
```

#### Risk Assessment Framework
```python
def assess_risk_level(category, failure_type, community_impact):
    """Assess risk level for tuning recommendations"""
    if category == "definite_high" and failure_type == "false_negative":
        return "CRITICAL"  # Missing real crises
    elif failure_type == "false_negative":
        return "MODERATE"  # Missing any crisis
    else:
        return "LOW"  # False positives less critical
```

### 🔄 Integration Architecture

#### NLP Server Communication
```python
class NLPClientManager:
    def analyze_message(self, message, user_id, channel_id):
        """Direct integration with Ash-NLP analysis endpoint"""
        payload = {
            "message": message,
            "user_id": user_id,
            "channel_id": channel_id
        }
        response = requests.post(f"{self.base_url}/analyze", json=payload)
        return self.process_response(response)
```

#### Docker Network Configuration
```yaml
# docker-compose.yml network setup
networks:
  ash_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

services:
  ash-thrash:
    networks:
      ash_network:
        ipv4_address: 172.20.0.12
```

## ⚡ Performance Optimization

### 🚀 Concurrency Management

#### Configurable Concurrent Testing
```python
async def run_concurrent_tests(test_phrases, max_concurrent=3):
    """Execute tests with controlled concurrency to prevent server overload"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def test_with_semaphore(phrase):
        async with semaphore:
            return await self.test_single_phrase(phrase)
    
    tasks = [test_with_semaphore(phrase) for phrase in test_phrases]
    return await asyncio.gather(*tasks)
```

#### Rate Limiting & Retry Logic
```python
def execute_with_retry(self, test_func, max_retries=3, delay_ms=1000):
    """Resilient test execution with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return test_func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep((delay_ms * (2 ** attempt)) / 1000)
```

### 📊 Memory & Resource Management

#### Efficient Result Storage
```python
@dataclass
class PhraseTestResult:
    """Memory-efficient result storage with optional analysis data"""
    phrase_id: str
    message: str
    expected_priorities: List[str]
    actual_priority: str
    confidence_score: float
    result: TestResult
    
    # Optional detailed analysis (only stored when needed)
    analysis_data: Optional[Dict[str, Any]] = None
```

## 🔐 Security & Resilience

### 🛡️ Production Resilience Features

#### Graceful Error Handling
```python
def resilient_configuration_loading(self):
    """Load configuration with graceful fallbacks"""
    try:
        config = self.load_json_config()
        return self.validate_and_override(config)
    except Exception as e:
        self.logger.warning(f"Configuration issue: {e}")
        return self.get_safe_defaults()
```

#### Health Check Integration
```python
def verify_system_health(self):
    """Comprehensive system health validation"""
    checks = {
        'nlp_server': self.check_nlp_server_connectivity(),
        'configuration': self.validate_configuration(),
        'test_phrases': self.verify_test_phrase_integrity(),
        'file_system': self.check_file_system_permissions()
    }
    return all(checks.values()), checks
```

### 🔒 Data Security

#### No Sensitive Data Storage
- Test phrases contain no real user data
- Results include no personal information
- Server communications use internal Docker network
- No authentication tokens stored in repository

#### Secure Communication
```python
def secure_nlp_communication(self):
    """Secure communication with NLP server"""
    # Internal Docker network communication
    # No external network exposure
    # Request/response validation
    # Timeout and retry protection
```

## 🔍 Debugging & Monitoring

### 📝 Comprehensive Logging

#### Structured Logging Implementation
```python
class LoggingConfigManager:
    def setup_logging(self):
        """Configure comprehensive logging system"""
        logging.basicConfig(
            level=self.get_log_level(),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.get_log_file()),
                logging.StreamHandler()
            ]
        )
```

#### Debug Information Tracking
```python
def log_test_execution_details(self, test_result):
    """Comprehensive test execution logging"""
    self.logger.debug(f"Test: {test_result.phrase_id}")
    self.logger.debug(f"Expected: {test_result.expected_priorities}")
    self.logger.debug(f"Actual: {test_result.actual_priority}")
    self.logger.debug(f"Processing Time: {test_result.processing_time_ms}ms")
    
    if test_result.result == TestResult.FAIL:
        self.logger.warning(f"Test failure: {test_result.failure_severity}")
```

### 🔧 Performance Monitoring

#### Execution Time Tracking
```python
def track_performance_metrics(self):
    """Track detailed performance metrics"""
    metrics = {
        'total_execution_time': self.calculate_total_time(),
        'average_test_time': self.calculate_average_test_time(),
        'server_response_times': self.get_server_response_metrics(),
        'concurrent_test_efficiency': self.analyze_concurrency_performance()
    }
    return metrics
```

## 🚀 Deployment & Operations

### 🐳 Docker Configuration

#### Multi-Stage Build Optimization
```dockerfile
# Dockerfile optimization for production deployment
FROM python:3.11-slim as builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim as production
COPY --from=builder /root/.local /root/.local
COPY . /app
WORKDIR /app
CMD ["python", "startup.py"]
```

#### Environment Configuration
```yaml
# docker-compose.yml production configuration
version: '3.8'
services:
  ash-thrash:
    build: .
    environment:
      - GLOBAL_LOG_LEVEL=${GLOBAL_LOG_LEVEL:-INFO}
      - THRASH_MAX_CONCURRENT_TESTS=${THRASH_MAX_CONCURRENT_TESTS:-3}
      - GLOBAL_LEARNING_SYSTEM_ENABLED=false
    volumes:
      - ./results:/app/results
      - ./reports:/app/reports
      - ./logs:/app/logs
    networks:
      - ash_network
```

### 📊 Monitoring & Alerting

#### Health Check Endpoints
```python
def health_check_endpoint(self):
    """Provide health check information for monitoring"""
    return {
        'status': 'healthy',
        'last_test_run': self.get_last_test_timestamp(),
        'system_performance': self.get_recent_performance_metrics(),
        'configuration_status': self.validate_current_configuration()
    }
```

#### Performance Alerting
```python
def check_performance_alerts(self, results):
    """Generate alerts for performance issues"""
    alerts = []
    
    if results.overall_pass_rate < 0.70:
        alerts.append({
            'level': 'WARNING',
            'message': f'Overall pass rate {results.overall_pass_rate:.1%} below 70%'
        })
    
    for category in results.category_results:
        if category.category_name == 'definite_high' and category.pass_rate < 0.95:
            alerts.append({
                'level': 'CRITICAL',
                'message': f'High crisis detection at {category.pass_rate:.1%}'
            })
    
    return alerts
```

## 🔄 Continuous Integration

### 🧪 Automated Testing Pipeline

#### CI/CD Integration Points
```yaml
# .github/workflows/ci.yml (example)
name: Ash-Thrash CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker container
        run: docker build -t ash-thrash .
      - name: Run comprehensive tests
        run: docker run ash-thrash python main.py
      - name: Validate results
        run: docker run ash-thrash python analyze.py --validate
```

---

## 🤝 Contributing to Ash-Thrash

### 🏗️ Development Standards

#### Clean Architecture v3.1 Compliance
All contributions must adhere to the Clean Architecture Charter requirements:
- Factory function patterns
- Dependency injection
- JSON configuration + environment overrides
- Production resilience
- File versioning
- Comprehensive logging

#### Testing Requirements
```python
def test_new_feature():
    """All new features must include comprehensive tests"""
    # Use real methods, not mocks (Rule #8)
    # Test with actual LoggingConfigManager
    # Validate against production scenarios
    # Include error condition testing
```

#### Documentation Standards
- Include version headers in all files
- Update relevant documentation files
- Provide clear implementation examples
- Document any new environment variables

---

**Discord**: [https://discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)  
**Website**: [http://alphabetcartel.org](http://alphabetcartel.org)  
**Repository**: [https://github.com/the-alphabet-cartel/ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash)

*Technical excellence in service of chosen family.* 🏗️🧠✨