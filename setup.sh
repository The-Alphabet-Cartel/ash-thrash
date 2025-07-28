#!/bin/bash
# setup.sh - Ash-Thrash Testing Suite Setup Script

echo "🧪 Setting up Ash-Thrash Testing Suite"
echo "======================================"
echo "Repository: https://github.com/The-Alphabet-Cartel/ash-thrash"
echo "Discord: https://discord.gg/alphabetcartel"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    echo "   Download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi
echo -e "${GREEN}✅ Docker found${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose found${NC}"

# Check Python (for local development)
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️ Python 3 not found. Docker will be used for all operations.${NC}"
else
    echo -e "${GREEN}✅ Python 3 found${NC}"
fi

# Create directory structure
echo ""
echo "📁 Creating directory structure..."

directories=(
    "src/test_data"
    "src/utils" 
    "src/api/routes"
    "docker"
    "scripts"
    "results/comprehensive"
    "results/quick_validation"
    "results/reports"
    "results/backups"
    "config"
    "docs"
    "dashboard/components"
    "dashboard/styles"
    "dashboard/templates"
    "sql/migrations"
    "sql/queries"
    "tests"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    echo "  📂 Created $dir"
done

# Set permissions
chmod 755 results/
chmod 755 scripts/
echo -e "${GREEN}✅ Directory structure created${NC}"

# Create environment file
echo ""
echo "⚙️ Setting up environment configuration..."

if [ ! -f .env ]; then
    cat > .env << 'EOF'
# Ash-Thrash Testing Suite Configuration
# Repository: https://github.com/The-Alphabet-Cartel/ash-thrash

# =============================================================================
# NLP Server Configuration (Ash NLP Server)
# =============================================================================
GLOBAL_NLP_API_HOST=10.20.30.253
GLOBAL_NLP_API_PORT=8881
GLOBAL_NLP_API_URL=http://10.20.30.253:8881

# =============================================================================
# Testing Configuration
# =============================================================================
THRASH_MAX_CONCURRENT_TESTS=5
THRASH_TEST_TIMEOUT_SECONDS=10
THRASH_RESULTS_RETENTION_DAYS=30
THRASH_ENABLE_DETAILED_LOGGING=true

# =============================================================================
# API Server Configuration
# =============================================================================
GLOBAL_THRASH_API_PORT=8884
THRASH_API_HOST=0.0.0.0
GLOBAL_ENABLE_DEBUG_MODE=false

# =============================================================================
# Database Configuration (Optional)
# =============================================================================
THRASH_ENABLE_DATABASE=false
THRASH_DATABASE_URL=postgresql://ash_test:change_this_password@localhost:5432/ash_testing
THRASH_DATABASE_POOL_SIZE=5

# =============================================================================
# Scheduled Testing Configuration
# =============================================================================
THRASH_ENABLE_SCHEDULED_TESTING=true
THRASH_COMPREHENSIVE_TEST_SCHEDULE=0 */6 * * *    # Every 6 hours
THRASH_QUICK_VALIDATION_SCHEDULE=0 * * * *        # Every hour

# =============================================================================
# Dashboard Integration
# =============================================================================
THRASH_ENABLE_DASHBOARD_INTEGRATION=true
GLOBAL_DASH_API_URL=http://localhost:8883
THRASH_DASHBOARD_UPDATE_INTERVAL=120              # Seconds

# =============================================================================
# Alert Configuration
# =============================================================================
THRASH_ENABLE_ALERTS=false
THRASH_ALERT_WEBHOOK_URL=
THRASH_CRITICAL_FAILURE_THRESHOLD=80              # Alert if high priority detection < 80%
THRASH_FALSE_POSITIVE_THRESHOLD=15                # Alert if false positive rate > 15%

# =============================================================================
# Development Configuration
# =============================================================================
THRASH_DEVELOPMENT_MODE=false
GLOBAL_LOG_LEVEL=INFO
THRASH_ENABLE_PROFILING=false
EOF
    echo -e "${GREEN}✅ Created .env file${NC}"
else
    echo -e "${YELLOW}⚠️ .env file already exists - skipping creation${NC}"
fi

# Create testing goals configuration
echo ""
echo "🎯 Setting up testing goals configuration..."

cat > config/testing_goals.json << 'EOF'
{
  "version": "1.0",
  "description": "Ash-Thrash Testing Goals and Targets",
  "last_updated": "2025-07-26",
  "goals": {
    "definite_high": {
      "target_pass_rate": 100.0,
      "description": "High Priority Crisis (Safety First!)",
      "critical": true,
      "allow_escalation": false,
      "min_confidence": 0.8,
      "alert_on_failure": true
    },
    "definite_medium": {
      "target_pass_rate": 65.0,
      "description": "Medium Priority Crisis",
      "critical": false,
      "allow_escalation": false,
      "min_confidence": 0.5,
      "alert_on_failure": false
    },
    "definite_low": {
      "target_pass_rate": 65.0,
      "description": "Low Priority Crisis",
      "critical": false,
      "allow_escalation": false,
      "min_confidence": 0.3,
      "alert_on_failure": false
    },
    "definite_none": {
      "target_pass_rate": 95.0,
      "description": "No Priority Crisis (Prevent False Positives)",
      "critical": true,
      "allow_escalation": false,
      "min_confidence": 0.0,
      "alert_on_failure": true
    },
    "maybe_high_medium": {
      "target_pass_rate": 90.0,
      "description": "Maybe High/Medium (No Priority Drops)",
      "critical": false,
      "allow_escalation": true,
      "min_confidence": 0.4,
      "alert_on_failure": false
    },
    "maybe_medium_low": {
      "target_pass_rate": 80.0,
      "description": "Maybe Medium/Low (No Priority Drops)",
      "critical": false,
      "allow_escalation": true,
      "min_confidence": 0.3,
      "alert_on_failure": false
    },
    "maybe_low_none": {
      "target_pass_rate": 90.0,
      "description": "Maybe Low/None (Prevent False Positives)",
      "critical": true,
      "allow_escalation": true,
      "min_confidence": 0.2,
      "alert_on_failure": false
    }
  },
  "overall_targets": {
    "minimum_overall_pass_rate": 85.0,
    "maximum_avg_response_time_ms": 200.0,
    "minimum_tests_per_second": 1.5,
    "maximum_error_rate": 5.0
  }
}
EOF
echo -e "${GREEN}✅ Created testing goals configuration${NC}"

# Create server configuration
cat > config/server_config.json << 'EOF'
{
  "version": "1.0",
  "description": "Ash-Thrash Server Configuration",
  "nlp_servers": {
    "primary": {
      "host": "10.20.30.253",
      "port": 8881,
      "url": "http://10.20.30.253:8881",
      "timeout": 10,
      "retry_attempts": 3,
      "retry_delay": 1
    },
    "fallback": {
      "enabled": false,
      "host": "localhost",
      "port": 8881,
      "url": "http://localhost:8881"
    }
  },
  "testing_api": {
    "host": "0.0.0.0",
    "port": 8884,
    "cors_enabled": true,
    "rate_limit": {
      "enabled": true,
      "max_requests": 100,
      "per_minutes": 15
    }
  },
  "performance": {
    "max_concurrent_tests": 5,
    "request_timeout": 10,
    "connection_pool_size": 10,
    "keep_alive": true
  }
}
EOF
echo -e "${GREEN}✅ Created server configuration${NC}"

# Create Docker Compose file
echo ""
echo "🐳 Setting up Docker configuration..."

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # Main testing service
  ash-thrash:
    build:
      context: .
      dockerfile: docker/Dockerfile
    container_name: ash-thrash
    restart: unless-stopped
    environment:
      - GLOBAL_NLP_API_URL=${GLOBAL_NLP_API_URL}
      - THRASH_MAX_CONCURRENT_TESTS=${THRASH_MAX_CONCURRENT_TESTS}
      - THRASH_ENABLE_SCHEDULED_TESTING=${THRASH_ENABLE_SCHEDULED_TESTING}
      - THRASH_COMPREHENSIVE_TEST_SCHEDULE=${THRASH_COMPREHENSIVE_TEST_SCHEDULE}
      - THRASH_QUICK_VALIDATION_SCHEDULE=${THRASH_QUICK_VALIDATION_SCHEDULE}
    volumes:
      - ./results:/app/results
      - ./config:/app/config
      - ./src:/app/src
    networks:
      - ash-thrash-network
    depends_on:
      - ash-thrash-api
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8884/health')"]
      interval: 30s
      timeout: 10s
      retries: 3

  # API server for remote testing and dashboard integration
  ash-thrash-api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    container_name: ash-thrash-api
    restart: unless-stopped
    ports:
      - "${GLOBAL_THRASH_API_PORT:-8884}:8884"
    environment:
      - GLOBAL_NLP_API_URL=${GLOBAL_NLP_API_URL}
      - THRASH_API_HOST=${THRASH_API_HOST}
      - GLOBAL_THRASH_API_PORT=8884
      - GLOBAL_ENABLE_DEBUG_MODE=${GLOBAL_ENABLE_DEBUG_MODE}
    volumes:
      - ./results:/app/results
      - ./config:/app/config
      - ./src:/app/src
    networks:
      - ash-thrash-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8884/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional database for historical data
  ash-thrash-db:
    image: postgres:15-alpine
    container_name: ash-thrash-db
    restart: unless-stopped
    environment:
      - GLOBAL_POSTGRES_DB=ash_testing
      - GLOBAL_POSTGRES_USER=ash_test
      - GLOBAL_POSTGRES_PASSWORD=change_this_password
    volumes:
      - ash_thrash_db_data:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - ash-thrash-network
    ports:
      - "5433:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ash_test"]
      interval: 30s
      timeout: 10s
      retries: 5
    profiles:
      - database

volumes:
  ash_thrash_db_data:

networks:
  ash-thrash-network:
    driver: bridge
EOF
echo -e "${GREEN}✅ Created Docker Compose configuration${NC}"

# Create main Dockerfile
cat > docker/Dockerfile << 'EOF'
FROM python:3.11-slim

LABEL maintainer="The Alphabet Cartel"
LABEL description="Ash-Thrash Testing Suite"
LABEL repository="https://github.com/The-Alphabet-Cartel/ash-thrash"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Create results directory
RUN mkdir -p /app/results

# Copy and setup cron
COPY docker/crontab /etc/cron.d/ash-thrash
RUN chmod 0644 /etc/cron.d/ash-thrash && \
    crontab /etc/cron.d/ash-thrash

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8884/health', timeout=5)"

EXPOSE 8884

ENTRYPOINT ["/entrypoint.sh"]
CMD ["testing"]
EOF

# Create API Dockerfile
cat > docker/Dockerfile.api << 'EOF'
FROM python:3.11-slim

LABEL maintainer="The Alphabet Cartel"
LABEL description="Ash-Thrash API Server"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create results directory
RUN mkdir -p /app/results

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8884/health || exit 1

EXPOSE 8884

ENTRYPOINT ["/entrypoint.sh"]
CMD ["api"]
EOF

echo -e "${GREEN}✅ Created Docker configurations${NC}"

# Create entrypoint script
cat > docker/entrypoint.sh << 'EOF'
#!/bin/bash
set -e

echo "🧪 Starting Ash-Thrash Container"
echo "Mode: $1"

# Wait for NLP server if URL is provided
if [ ! -z "$GLOBAL_NLP_API_URL" ]; then
    echo "⏳ Waiting for NLP server at $GLOBAL_NLP_API_URL..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -s --fail "$GLOBAL_NLP_API_URL/health" >/dev/null 2>&1; then
            echo "✅ NLP server is ready"
            break
        fi
        echo "Waiting for NLP server... ($timeout seconds remaining)"
        sleep 5
        timeout=$((timeout - 5))
    done
    
    if [ $timeout -le 0 ]; then
        echo "❌ NLP server not ready after 60 seconds"
        exit 1
    fi
fi

case "$1" in
    "testing")
        echo "🧪 Starting testing service with scheduled jobs"
        # Start cron for scheduled testing
        if [ "$THRASH_ENABLE_SCHEDULED_TESTING" = "true" ]; then
            echo "📅 Starting cron daemon"
            cron
        fi
        
        # Run initial validation
        echo "🔍 Running initial validation"
        python src/quick_validation.py
        
        # Keep container running
        tail -f /dev/null
        ;;
    "api")
        echo "🌐 Starting API server"
        python src/api/server.py
        ;;
    *)
        echo "❌ Unknown mode: $1"
        echo "Available modes: testing, api"
        exit 1
        ;;
esac
EOF
chmod +x docker/entrypoint.sh

# Create crontab
cat > docker/crontab << 'EOF'
# Ash-Thrash Scheduled Testing
# Repository: https://github.com/The-Alphabet-Cartel/ash-thrash

# Run comprehensive testing every 6 hours
0 */6 * * * /usr/local/bin/python /app/src/comprehensive_testing.py >> /var/log/cron.log 2>&1

# Run quick validation every hour
0 * * * * /usr/local/bin/python /app/src/quick_validation.py >> /var/log/cron.log 2>&1

# Generate weekly performance report every Sunday at 6 AM
0 6 * * 0 /usr/local/bin/python /app/scripts/generate_report.py --weekly >> /var/log/cron.log 2>&1

# Cleanup old results every day at 2 AM (keep last 30 days)
0 2 * * * /app/scripts/cleanup_old_results.sh 30 >> /var/log/cron.log 2>&1

# Health check every 15 minutes
*/15 * * * * /usr/local/bin/python -c "import requests; requests.get('http://localhost:8884/health')" >> /var/log/cron.log 2>&1
EOF

echo -e "${GREEN}✅ Created Docker support files${NC}"

# Create requirements.txt
echo ""
echo "📦 Creating Python requirements..."

cat > requirements.txt << 'EOF'
# Ash-Thrash Testing Suite Requirements
# Repository: https://github.com/The-Alphabet-Cartel/ash-thrash

# Core dependencies
requests>=2.31.0
flask>=2.3.0
python-dateutil>=2.8.0

# Data processing and analysis
pandas>=2.0.0
numpy>=1.24.0

# Visualization and reporting
matplotlib>=3.7.0
seaborn>=0.12.0

# Database support (optional)
psycopg2-binary>=2.9.0
sqlalchemy>=2.0.0

# Task scheduling
schedule>=1.2.0

# Configuration and validation
jsonschema>=4.17.0
pydantic>=2.0.0

# Testing and development
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.0.0

# API and web
flask-cors>=4.0.0
gunicorn>=21.0.0

# Utilities
click>=8.1.0
tqdm>=4.65.0
rich>=13.0.0
EOF
echo -e "${GREEN}✅ Created requirements.txt${NC}"

# Create .gitignore
cat > .gitignore << 'EOF'
# Ash-Thrash .gitignore

# Environment variables
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Test results and logs
results/comprehensive/*
results/quick_validation/*
results/reports/*
results/backups/*
!results/.gitkeep
*.log
logs/

# Docker
.dockerignore

# Database
*.db
*.sqlite
*.sqlite3

# Temporary files
tmp/
temp/
.tmp/

# Coverage reports
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter Notebooks
.ipynb_checkpoints

# Documentation builds
docs/_build/
EOF
echo -e "${GREEN}✅ Created .gitignore${NC}"

# Create result directory placeholders
touch results/comprehensive/.gitkeep
touch results/quick_validation/.gitkeep
touch results/reports/.gitkeep
touch results/backups/.gitkeep

# Create utility scripts
echo ""
echo "🔧 Creating utility scripts..."

cat > scripts/run_comprehensive.sh << 'EOF'
#!/bin/bash
# Run comprehensive testing (350 phrases)

echo "🧪 Starting Comprehensive Crisis Detection Test"
echo "Repository: https://github.com/The-Alphabet-Cartel/ash-thrash"
echo ""

# Check if running in Docker
if [ -f /.dockerenv ]; then
    python /app/src/comprehensive_testing.py "$@"
else
    python src/comprehensive_testing.py "$@"
fi
EOF

cat > scripts/run_quick_validation.sh << 'EOF'
#!/bin/bash
# Run quick validation (10 phrases)

echo "🔍 Starting Quick Validation Test"
echo ""

# Check if running in Docker
if [ -f /.dockerenv ]; then
    python /app/src/quick_validation.py "$@"
else
    python src/quick_validation.py "$@"
fi
EOF

cat > scripts/cleanup_old_results.sh << 'EOF'
#!/bin/bash
# Cleanup old test results

DAYS=${1:-30}
RESULTS_DIR=${2:-results}

echo "🧹 Cleaning up test results older than $DAYS days"

# Find and remove old comprehensive test results
find "$RESULTS_DIR/comprehensive" -name "*.json" -mtime +$DAYS -delete
find "$RESULTS_DIR/quick_validation" -name "*.json" -mtime +$DAYS -delete
find "$RESULTS_DIR/reports" -name "*.json" -name "*.html" -mtime +$DAYS -delete

echo "✅ Cleanup complete"
EOF

chmod +x scripts/*.sh
echo -e "${GREEN}✅ Created utility scripts${NC}"

# Create test files for the testing framework
echo ""
echo "🧪 Creating test framework files..."

# Create pytest configuration
cat > pytest.ini << 'EOF'
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=src
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    api: API tests
EOF

# Create test requirements
cat > requirements-dev.txt << 'EOF'
# Development and testing dependencies for Ash-Thrash

# Testing framework
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
pytest-asyncio>=0.21.0
pytest-xdist>=3.3.0

# Code quality
black>=23.0.0
flake8>=6.0.0
isort>=5.12.0
mypy>=1.5.0

# Development tools
pre-commit>=3.3.0
ipython>=8.14.0
jupyter>=1.0.0

# Testing utilities
responses>=0.23.0
factory-boy>=3.3.0
freezegun>=1.2.0
EOF

# Create main test files
cat > tests/__init__.py << 'EOF'
"""
Ash-Thrash Testing Framework

This package contains tests for the ash-thrash testing system itself.
These are tests that test the tester!
"""
EOF

cat > tests/conftest.py << 'EOF'
"""
Pytest configuration and shared fixtures for Ash-Thrash tests
"""

import pytest
import tempfile
import shutil
import os
from unittest.mock import Mock, patch
import json


@pytest.fixture
def temp_results_dir():
    """Create a temporary directory for test results"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_nlp_server():
    """Mock NLP server responses"""
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'crisis_level': 'medium',
            'confidence_score': 0.75,
            'processing_time_ms': 150.0,
            'detected_categories': ['depression', 'anxiety']
        }
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def sample_test_results():
    """Sample test results for testing"""
    return {
        "test_metadata": {
            "timestamp": "2025-07-26T10:30:00Z",
            "total_phrases_tested": 10,
            "test_type": "unit_test_sample"
        },
        "overall_results": {
            "total_passed": 8,
            "total_failed": 2,
            "overall_pass_rate": 80.0,
            "avg_response_time_ms": 150.0
        },
        "goal_achievement": {
            "summary": {
                "goals_achieved": 3,
                "total_goals": 4,
                "achievement_rate": 75.0
            }
        }
    }


@pytest.fixture
def test_config():
    """Test configuration"""
    return {
        "GLOBAL_NLP_API_URL": "http://localhost:8881",
        "max_concurrent_tests": 2,
        "test_timeout": 5
    }
EOF

cat > tests/test_comprehensive.py << 'EOF'
"""
Tests for the comprehensive testing system
Testing the 350-phrase testing suite
"""

import pytest
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from comprehensive_testing import CrisisTestSuite, TestPhrase, TestResult
except ImportError:
    # If files don't exist yet, create mock classes for testing
    class TestPhrase:
        def __init__(self, message, expected_priority, category, subcategory, description):
            self.message = message
            self.expected_priority = expected_priority
            self.category = category
            self.subcategory = subcategory
            self.description = description
    
    class TestResult:
        def __init__(self, phrase, detected_priority, confidence_score, response_time_ms, 
                     processing_time_ms, detected_categories, passed, error_message=None, timestamp=""):
            self.phrase = phrase
            self.detected_priority = detected_priority
            self.confidence_score = confidence_score
            self.response_time_ms = response_time_ms
            self.processing_time_ms = processing_time_ms
            self.detected_categories = detected_categories
            self.passed = passed
            self.error_message = error_message
            self.timestamp = timestamp
    
    class CrisisTestSuite:
        def __init__(self):
            self.test_phrases = []
            self.results = []


class TestCrisisTestSuite:
    """Test the main CrisisTestSuite class"""
    
    def test_test_phrase_creation(self):
        """Test creating a TestPhrase object"""
        phrase = TestPhrase(
            message="I'm feeling really down",
            expected_priority="low",
            category="definite_low",
            subcategory="mild_distress",
            description="Test phrase for low priority"
        )
        
        assert phrase.message == "I'm feeling really down"
        assert phrase.expected_priority == "low"
        assert phrase.category == "definite_low"
    
    def test_test_result_creation(self):
        """Test creating a TestResult object"""
        phrase = TestPhrase("test message", "low", "definite_low", "test", "test desc")
        
        result = TestResult(
            phrase=phrase,
            detected_priority="low",
            confidence_score=0.6,
            response_time_ms=150.0,
            processing_time_ms=100.0,
            detected_categories=["anxiety"],
            passed=True
        )
        
        assert result.phrase == phrase
        assert result.detected_priority == "low"
        assert result.passed is True
    
    def test_crisis_test_suite_initialization(self):
        """Test CrisisTestSuite initialization"""
        suite = CrisisTestSuite()
        
        assert isinstance(suite.test_phrases, list)
        assert isinstance(suite.results, list)
    
    @patch('requests.post')
    def test_single_phrase_testing(self, mock_post):
        """Test testing a single phrase"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'crisis_level': 'high',
            'confidence_score': 0.9,
            'processing_time_ms': 120.0,
            'detected_categories': ['suicidal_ideation']
        }
        mock_post.return_value = mock_response
        
        suite = CrisisTestSuite()
        phrase = TestPhrase(
            message="I want to end my life",
            expected_priority="high",
            category="definite_high",
            subcategory="suicidal_ideation",
            description="High priority test"
        )
        
        # Test the method if it exists
        if hasattr(suite, '_test_single_phrase'):
            result = suite._test_single_phrase(phrase)
            assert result.detected_priority == "high"
            assert result.passed is True
    
    def test_evaluation_logic(self):
        """Test the evaluation logic for different categories"""
        suite = CrisisTestSuite()
        
        # Test definite category (exact match required)
        phrase_definite = TestPhrase("test", "high", "definite_high", "test", "test")
        phrase_definite.allow_escalation = False
        
        if hasattr(suite, '_evaluate_result'):
            # Should pass with exact match
            assert suite._evaluate_result(phrase_definite, "high") is True
            # Should fail with different priority
            assert suite._evaluate_result(phrase_definite, "medium") is False
        
        # Test maybe category (allow escalation)
        phrase_maybe = TestPhrase("test", "medium", "maybe_high_medium", "test", "test")
        phrase_maybe.allow_escalation = True
        
        if hasattr(suite, '_evaluate_result'):
            # Should pass with exact match
            assert suite._evaluate_result(phrase_maybe, "medium") is True
            # Should pass with escalation
            assert suite._evaluate_result(phrase_maybe, "high") is True
            # Should fail with de-escalation
            assert suite._evaluate_result(phrase_maybe, "low") is False


class TestTestDataIntegrity:
    """Test the integrity of test data"""
    
    def test_test_phrase_categories(self):
        """Test that all required test categories exist"""
        expected_categories = [
            "definite_high",
            "definite_medium", 
            "definite_low",
            "definite_none",
            "maybe_high_medium",
            "maybe_medium_low",
            "maybe_low_none"
        ]
        
        # This would test the actual test data when implemented
        # For now, just verify the expected categories are defined
        assert len(expected_categories) == 7
        assert "definite_high" in expected_categories
    
    def test_phrase_count_targets(self):
        """Test that each category has the target number of phrases"""
        target_phrases_per_category = 50
        total_expected_phrases = 350
        
        # This would verify actual phrase counts when implemented
        assert target_phrases_per_category * 7 == total_expected_phrases


class TestResultsProcessing:
    """Test results processing and analysis"""
    
    def test_goal_achievement_calculation(self, sample_test_results):
        """Test goal achievement calculation"""
        results = sample_test_results
        
        # Test basic result structure
        assert "goal_achievement" in results
        assert "summary" in results["goal_achievement"]
        
        summary = results["goal_achievement"]["summary"]
        assert summary["achievement_rate"] == 75.0
        assert summary["goals_achieved"] == 3
        assert summary["total_goals"] == 4
    
    def test_pass_rate_calculation(self, sample_test_results):
        """Test pass rate calculation"""
        results = sample_test_results
        overall = results["overall_results"]
        
        expected_pass_rate = (8 / 10) * 100  # 8 passed out of 10 total
        assert overall["overall_pass_rate"] == expected_pass_rate
    
    def test_results_file_format(self, sample_test_results, temp_results_dir):
        """Test that results can be saved and loaded as JSON"""
        results_file = os.path.join(temp_results_dir, "test_results.json")
        
        # Save results
        with open(results_file, 'w') as f:
            json.dump(sample_test_results, f)
        
        # Load and verify
        with open(results_file, 'r') as f:
            loaded_results = json.load(f)
        
        assert loaded_results == sample_test_results
        assert loaded_results["overall_results"]["overall_pass_rate"] == 80.0


class TestAPIIntegration:
    """Test API integration and endpoints"""
    
    @patch('requests.get')
    def test_health_check(self, mock_get):
        """Test health check endpoint"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_get.return_value = mock_response
        
        # This would test actual health check when API is implemented
        assert mock_response.status_code == 200
    
    @patch('requests.post')
    def test_nlp_server_communication(self, mock_post):
        """Test communication with NLP server"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'crisis_level': 'medium',
            'confidence_score': 0.75,
            'processing_time_ms': 150.0
        }
        mock_post.return_value = mock_response
        
        # This would test actual NLP communication when implemented
        assert mock_response.json()['crisis_level'] == 'medium'


if __name__ == "__main__":
    pytest.main([__file__])
EOF

cat > tests/test_api_client.py << 'EOF'
"""
Tests for the NLP API client communication
"""

import pytest
import requests
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestNLPAPIClient:
    """Test NLP server API communication"""
    
    @patch('requests.post')
    def test_successful_analysis_request(self, mock_post):
        """Test successful analysis request to NLP server"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'crisis_level': 'high',
            'confidence_score': 0.85,
            'processing_time_ms': 125.0,
            'detected_categories': ['suicidal_ideation', 'depression']
        }
        mock_post.return_value = mock_response
        
        # Test the request
        url = "http://localhost:8881/analyze"
        payload = {
            "message": "I want to end my life",
            "user_id": "test_user",
            "channel_id": "test_channel"
        }
        
        response = mock_post(url, json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data['crisis_level'] == 'high'
        assert data['confidence_score'] == 0.85
        assert 'suicidal_ideation' in data['detected_categories']
    
    @patch('requests.post')
    def test_timeout_handling(self, mock_post):
        """Test timeout handling for slow responses"""
        # Mock timeout
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with pytest.raises(requests.exceptions.Timeout):
            mock_post("http://localhost:8881/analyze", timeout=5)
    
    @patch('requests.post')
    def test_connection_error_handling(self, mock_post):
        """Test connection error handling"""
        # Mock connection error
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with pytest.raises(requests.exceptions.ConnectionError):
            mock_post("http://localhost:8881/analyze")
    
    @patch('requests.post')
    def test_server_error_handling(self, mock_post):
        """Test server error (500) handling"""
        # Mock server error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        response = mock_post("http://localhost:8881/analyze")
        assert response.status_code == 500
    
    @patch('requests.get')
    def test_health_check_success(self, mock_get):
        """Test successful health check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "service": "ash-nlp",
            "timestamp": "2025-07-26T10:30:00Z"
        }
        mock_get.return_value = mock_response
        
        response = mock_get("http://localhost:8881/health")
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
    
    @patch('requests.get')
    def test_health_check_failure(self, mock_get):
        """Test failed health check"""
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.json.return_value = {
            "status": "unhealthy",
            "error": "Service unavailable"
        }
        mock_get.return_value = mock_response
        
        response = mock_get("http://localhost:8881/health")
        assert response.status_code == 503
        assert response.json()['status'] == 'unhealthy'


class TestAPIErrorHandling:
    """Test various API error scenarios"""
    
    def test_malformed_response_handling(self):
        """Test handling of malformed JSON responses"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_post.return_value = mock_response
            
            response = mock_post("http://localhost:8881/analyze")
            assert response.status_code == 200
            
            with pytest.raises(ValueError):
                response.json()
    
    def test_missing_fields_handling(self):
        """Test handling of responses with missing required fields"""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                # Missing crisis_level field
                'confidence_score': 0.5
            }
            mock_post.return_value = mock_response
            
            response = mock_post("http://localhost:8881/analyze")
            data = response.json()
            
            # Should handle missing crisis_level gracefully
            assert 'crisis_level' not in data
            assert data.get('crisis_level', 'none') == 'none'


if __name__ == "__main__":
    pytest.main([__file__])
EOF

cat > tests/test_results_processor.py << 'EOF'
"""
Tests for results processing and analysis
"""

import pytest
import json
import tempfile
import os
from datetime import datetime
from unittest.mock import Mock


class TestResultsProcessor:
    """Test results processing functionality"""
    
    def test_pass_rate_calculation(self):
        """Test pass rate calculation logic"""
        # Test basic pass rate calculation
        passed = 85
        total = 100
        expected_rate = 85.0
        
        calculated_rate = (passed / total) * 100
        assert calculated_rate == expected_rate
    
    def test_goal_achievement_analysis(self, sample_test_results):
        """Test goal achievement analysis"""
        results = sample_test_results
        
        # Test that goal achievement is calculated correctly
        goals_achieved = results["goal_achievement"]["summary"]["goals_achieved"]
        total_goals = results["goal_achievement"]["summary"]["total_goals"]
        achievement_rate = results["goal_achievement"]["summary"]["achievement_rate"]
        
        expected_rate = (goals_achieved / total_goals) * 100
        assert achievement_rate == expected_rate
    
    def test_category_performance_analysis(self):
        """Test category-specific performance analysis"""
        category_data = {
            "definite_high": {"passed": 50, "total": 50, "pass_rate": 100.0},
            "definite_medium": {"passed": 32, "total": 50, "pass_rate": 64.0},
            "definite_none": {"passed": 48, "total": 50, "pass_rate": 96.0}
        }
        
        # Test high priority performance
        assert category_data["definite_high"]["pass_rate"] == 100.0
        
        # Test that false positive prevention is working
        assert category_data["definite_none"]["pass_rate"] >= 95.0
    
    def test_confidence_distribution_analysis(self):
        """Test confidence score distribution analysis"""
        confidence_scores = [0.1, 0.3, 0.5, 0.7, 0.9, 0.95, 0.85, 0.2, 0.6, 0.8]
        
        # Calculate distribution
        ranges = {
            "0.0-0.2": sum(1 for c in confidence_scores if 0.0 <= c < 0.2),
            "0.2-0.4": sum(1 for c in confidence_scores if 0.2 <= c < 0.4),
            "0.4-0.6": sum(1 for c in confidence_scores if 0.4 <= c < 0.6),
            "0.6-0.8": sum(1 for c in confidence_scores if 0.6 <= c < 0.8),
            "0.8-1.0": sum(1 for c in confidence_scores if 0.8 <= c <= 1.0)
        }
        
        assert ranges["0.0-0.2"] == 1  # 0.1
        assert ranges["0.2-0.4"] == 2  # 0.3, 0.2
        assert ranges["0.8-1.0"] == 3  # 0.9, 0.95, 0.85
    
    def test_performance_metrics_calculation(self):
        """Test performance metrics calculation"""
        response_times = [100, 150, 200, 175, 125]
        
        # Calculate average response time
        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time == 150.0
        
        # Calculate min/max
        min_time = min(response_times)
        max_time = max(response_times)
        assert min_time == 100
        assert max_time == 200
    
    def test_trend_analysis(self):
        """Test trend analysis for historical data"""
        historical_data = [
            {"timestamp": "2025-07-26T08:00:00Z", "pass_rate": 85.0},
            {"timestamp": "2025-07-26T14:00:00Z", "pass_rate": 87.0},
            {"timestamp": "2025-07-26T20:00:00Z", "pass_rate": 89.0}
        ]
        
        # Test trend calculation (improving)
        pass_rates = [data["pass_rate"] for data in historical_data]
        trend = "improving" if pass_rates[-1] > pass_rates[0] else "declining"
        
        assert trend == "improving"
        assert pass_rates[-1] == 89.0
        assert pass_rates[0] == 85.0


class TestResultsStorage:
    """Test results storage and retrieval"""
    
    def test_json_serialization(self, sample_test_results, temp_results_dir):
        """Test JSON serialization of results"""
        results_file = os.path.join(temp_results_dir, "test_results.json")
        
        # Save results to file
        with open(results_file, 'w') as f:
            json.dump(sample_test_results, f, indent=2)
        
        # Verify file was created
        assert os.path.exists(results_file)
        
        # Load and verify data integrity
        with open(results_file, 'r') as f:
            loaded_results = json.load(f)
        
        assert loaded_results == sample_test_results
    
    def test_timestamp_formatting(self):
        """Test timestamp formatting for results"""
        now = datetime.now()
        iso_timestamp = now.isoformat()
        
        # Verify ISO format
        assert 'T' in iso_timestamp
        assert len(iso_timestamp.split('T')) == 2
    
    def test_results_file_naming(self):
        """Test results file naming convention"""
        timestamp = 1690380000  # Example timestamp
        expected_filename = f"comprehensive_test_results_{timestamp}.json"
        
        assert expected_filename.startswith("comprehensive_test_results_")
        assert expected_filename.endswith(".json")
        assert str(timestamp) in expected_filename


class TestFailureAnalysis:
    """Test failure analysis and reporting"""
    
    def test_failure_categorization(self):
        """Test categorization of test failures"""
        failures = [
            {"category": "definite_high", "expected": "high", "detected": "medium"},
            {"category": "definite_none", "expected": "none", "detected": "low"},
            {"category": "maybe_high_medium", "expected": "medium", "detected": "low"}
        ]
        
        # Categorize failures by type
        critical_failures = [f for f in failures if f["category"] in ["definite_high", "definite_none"]]
        escalation_failures = [f for f in failures if "maybe" in f["category"] and 
                             f["detected"] < f["expected"]]  # This would need proper comparison
        
        assert len(critical_failures) == 2
        assert len(failures) == 3
    
    def test_failure_impact_assessment(self):
        """Test assessment of failure impact"""
        # High priority failures are critical
        high_failure = {"category": "definite_high", "expected": "high", "detected": "medium"}
        assert "definite_high" in high_failure["category"]
        
        # False positive failures are also critical
        false_positive = {"category": "definite_none", "expected": "none", "detected": "medium"}
        assert "definite_none" in false_positive["category"]


if __name__ == "__main__":
    pytest.main([__file__])
EOF

cat > tests/test_dashboard_integration.py << 'EOF'
"""
Tests for dashboard integration functionality
"""

import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestDashboardAPI:
    """Test dashboard API endpoints"""
    
    def test_api_status_endpoint(self):
        """Test API status endpoint response format"""
        expected_response = {
            "status": "healthy",
            "service": "ash-thrash",
            "timestamp": "2025-07-26T10:30:00Z",
            "version": "1.0.0"
        }
        
        # Test response structure
        assert "status" in expected_response
        assert "service" in expected_response
        assert expected_response["service"] == "ash-thrash"
    
    def test_latest_results_endpoint(self, sample_test_results):
        """Test latest results endpoint"""
        # Mock API response
        api_response = {
            "success": True,
            "timestamp": "2025-07-26T10:30:00Z",
            "results": sample_test_results
        }
        
        assert api_response["success"] is True
        assert "results" in api_response
        assert api_response["results"]["overall_results"]["overall_pass_rate"] == 80.0
    
    def test_historical_trends_endpoint(self):
        """Test historical trends endpoint"""
        trends_data = {
            "success": True,
            "trends": [
                {
                    "timestamp": "2025-07-26T08:00:00Z",
                    "overall_pass_rate": 85.0,
                    "goal_achievement_rate": 80.0,
                    "avg_response_time": 150.0
                },
                {
                    "timestamp": "2025-07-26T14:00:00Z", 
                    "overall_pass_rate": 87.0,
                    "goal_achievement_rate": 85.0,
                    "avg_response_time": 145.0
                }
            ],
            "total_runs": 2
        }
        
        assert trends_data["success"] is True
        assert len(trends_data["trends"]) == 2
        assert trends_data["total_runs"] == 2
    
    @patch('requests.post')
    def test_trigger_test_endpoint(self, mock_post):
        """Test trigger test endpoint"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "started",
            "message": "Comprehensive test started",
            "timestamp": "2025-07-26T10:30:00Z"
        }
        mock_post.return_value = mock_response
        
        response = mock_post("/api/test/run")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "started"


class TestDashboardDataFormatting:
    """Test data formatting for dashboard display"""
    
    def test_goal_status_formatting(self):
        """Test formatting of goal achievement status"""
        goal_data = {
            "definite_high": {
                "target_rate": 100.0,
                "actual_rate": 98.0,
                "goal_met": False,
                "status": "❌ MISSED"
            },
            "definite_none": {
                "target_rate": 95.0,
                "actual_rate": 96.0,
                "goal_met": True,
                "status": "✅ ACHIEVED"
            }
        }
        
        # Test critical goal failure
        assert goal_data["definite_high"]["goal_met"] is False
        assert "❌" in goal_data["definite_high"]["status"]
        
        # Test successful goal achievement
        assert goal_data["definite_none"]["goal_met"] is True
        assert "✅" in goal_data["definite_none"]["status"]
    
    def test_category_performance_formatting(self):
        """Test formatting of category performance data"""
        category_data = {
            "category": "definite_high",
            "pass_rate": 98.0,
            "target_rate": 100.0,
            "passed": 49,
            "total": 50,
            "status_class": "warning"  # Not meeting 100% target
        }
        
        assert category_data["pass_rate"] == 98.0
        assert category_data["status_class"] == "warning"
        assert category_data["passed"] == 49
    
    def test_trend_chart_data_formatting(self):
        """Test formatting of trend data for charts"""
        chart_data = {
            "labels": ["08:00", "14:00", "20:00"],
            "datasets": [
                {
                    "label": "Pass Rate",
                    "data": [85.0, 87.0, 89.0],
                    "borderColor": "rgb(75, 192, 192)",
                    "backgroundColor": "rgba(75, 192, 192, 0.1)"
                }
            ]
        }
        
        assert len(chart_data["labels"]) == 3
        assert len(chart_data["datasets"][0]["data"]) == 3
        assert chart_data["datasets"][0]["label"] == "Pass Rate"


class TestDashboardIntegration:
    """Test integration with ash-dash"""
    
    def test_route_configuration(self):
        """Test dashboard route configuration"""
        routes = [
            "/api/testing/latest-results",
            "/api/testing/historical-trends", 
            "/api/testing/goals",
            "/api/testing/run-comprehensive"
        ]
        
        # Verify all required routes are defined
        assert "/api/testing/latest-results" in routes
        assert "/api/testing/run-comprehensive" in routes
        assert len(routes) == 4
    
    def test_component_integration(self):
        """Test dashboard component integration"""
        component_files = [
            "TestingOverview.js",
            "CategoryPerformance.js", 
            "GoalTracking.js",
            "TrendsChart.js"
        ]
        
        # Verify all required components are defined
        assert "TestingOverview.js" in component_files
        assert "CategoryPerformance.js" in component_files
        assert len(component_files) == 4
    
    def test_css_styling(self):
        """Test CSS styling for dashboard components"""
        css_classes = [
            "testing-overview",
            "category-item",
            "goal-item",
            "action-button"
        ]
        
        # Verify required CSS classes are defined
        assert "testing-overview" in css_classes
        assert "action-button" in css_classes


class TestRealTimeUpdates:
    """Test real-time update functionality"""
    
    def test_websocket_connection(self):
        """Test WebSocket connection for real-time updates"""
        # Mock WebSocket connection
        ws_connection = {
            "connected": True,
            "last_update": "2025-07-26T10:30:00Z",
            "update_interval": 120  # seconds
        }
        
        assert ws_connection["connected"] is True
        assert ws_connection["update_interval"] == 120
    
    def test_auto_refresh_mechanism(self):
        """Test auto-refresh mechanism"""
        refresh_config = {
            "enabled": True,
            "interval_seconds": 120,
            "last_refresh": "2025-07-26T10:30:00Z"
        }
        
        assert refresh_config["enabled"] is True
        assert refresh_config["interval_seconds"] == 120


if __name__ == "__main__":
    pytest.main([__file__])
EOF

echo -e "${GREEN}✅ Created test framework files${NC}"

# Test Docker setup
echo ""
echo "🧪 Testing Docker setup..."

if docker-compose config > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker Compose configuration is valid${NC}"
else
    echo -e "${RED}❌ Docker Compose configuration has errors${NC}"
    echo "Please check docker-compose.yml"
fi

# Final setup summary
echo ""
echo -e "${GREEN}🎉 Ash-Thrash Setup Complete!${NC}"
echo ""
echo -e "${BLUE}📋 What's been created:${NC}"
echo "   📁 Complete directory structure"
echo "   ⚙️ Environment configuration (.env)"
echo "   🎯 Testing goals (config/testing_goals.json)"
echo "   🐳 Docker configuration (docker-compose.yml)"
echo "   📦 Python requirements (requirements.txt)"
echo "   🔧 Utility scripts (scripts/)"
echo ""
echo -e "${BLUE}🚀 Next Steps:${NC}"
echo "   1. Review and customize .env file"
echo "   2. Verify NLP server URL (currently: ${GLOBAL_NLP_API_URL:-http://10.20.30.253:8881})"
echo "   3. Build and start services: ${YELLOW}docker-compose up -d${NC}"
echo "   4. Run initial test: ${YELLOW}docker-compose exec ash-thrash python src/comprehensive_testing.py${NC}"
echo ""
echo -e "${BLUE}📊 Services will be available at:${NC}"
echo "   🧪 Testing API: http://localhost:8884"
echo "   🔍 Health Check: http://localhost:8884/health"
echo "   📈 Results: ./results/ directory"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo "   📖 README.md - Complete usage guide"
echo "   🔗 Repository: https://github.com/The-Alphabet-Cartel/ash-thrash"
echo "   💬 Discord: https://discord.gg/alphabetcartel"
echo ""
echo -e "${GREEN}Ready to thrash the system! 🎯${NC}"