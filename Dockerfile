# Ash-Thrash Testing Suite Dockerfile
# Repository: https://github.com/the-alphabet-cartel/ash-thrash
# Discord: https://discord.gg/alphabetcartel
# Website: http://alphabetcartel.org

FROM python:3.11-slim

LABEL maintainer="The Alphabet Cartel"
LABEL description="Ash-Thrash Testing Suite"
LABEL repository="https://github.com/The-Alphabet-Cartel/ash-thrash"

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Create non-root user with /app as home directory (no separate home dir)
RUN groupadd -g 1001 thrash && \
    useradd -g 1001 -u 1001 -d /app -M thrash

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=thrash:thrash . .

# Add this after the COPY command for debugging
RUN ls -la /app/config/ && echo "Config directory contents above"

# Create directories for results and logs
RUN mkdir -p ./results ./logs ./reports && \
    chown -R thrash:thrash /app  && \
    chmod 755 /app

# Create non-root user for security
USER thrash

# Set working directory
WORKDIR /app

# Environmental Variables
ENV PYTHONUNBUFFERED="1"
ENV PYTHONDONTWRITEBYTECODE="1"
ENV PYTHONPATH="/app"

ENV TZ="America/Los_Angeles"

# API Settings
ENV THRASH_API_HOST="0.0.0.0"

# Security & Authentication  
ENV THRASH_API_RATE_LIMIT="100"
ENV THRASH_ENABLE_API_AUTHENTICATION="false"

# Test Execution Settings
ENV THRASH_MAX_CONCURRENT_TESTS="3"

# Quick Test Settings
ENV THRASH_QUICK_TEST_SAMPLE_SIZE="50"

# Test Results Storage
ENV THRASH_RESULTS_RETENTION_DAYS="30"
ENV THRASH_AUTO_CLEANUP_RESULTS="true"

# Discord Webhook for Test Results (optional)
ENV THRASH_DISCORD_WEBHOOK_URL=""
ENV THRASH_DISCORD_WEBHOOK_USERNAME="Ash-Thrash"
ENV THRASH_DISCORD_NOTIFICATIONS_ENABLED="true"

# Notification Settings
ENV THRASH_NOTIFY_ON_COMPREHENSIVE_TESTS="true"
ENV THRASH_NOTIFY_ON_QUICK_TESTS="false"
ENV THRASH_NOTIFY_ON_CATEGORY_TESTS="false"
ENV THRASH_NOTIFY_ON_FAILURES_ONLY="false"

# Logging Configuration
ENV THRASH_LOG_FILE="ash-thrash.log"
ENV THRASH_ENABLE_DEBUG_LOGGING="false"

# Performance Settings
ENV THRASH_REQUEST_TIMEOUT="30"
ENV THRASH_CONNECTION_POOL_SIZE="10"

# When to generate tuning suggestions
ENV THRASH_GENERATE_SUGGESTIONS="true"
ENV THRASH_SUGGESTION_THRESHOLD="10.0"
ENV THRASH_CRITICAL_THRESHOLD="20.0"

# Test Execution
ENV THRASH_RETRY_FAILED_TESTS="true"
ENV THRASH_MAX_RETRIES="3"
ENV THRASH_RETRY_DELAY_SECONDS="5"

# API Response Caching
ENV THRASH_ENABLE_RESULT_CACHING="true"
ENV THRASH_CACHE_TTL_SECONDS="300"

# Health Check Settings
ENV THRASH_HEALTH_CHECK_INTERVAL="30"
ENV THRASH_NLP_HEALTH_CHECK_TIMEOUT="5"

# Development Mode
ENV THRASH_DEVELOPMENT_MODE="false"
ENV THRASH_ENABLE_API_DOCS="true"

# Test Data Validation
ENV THRASH_VALIDATE_DATA_ON_STARTUP="true"
ENV THRASH_STRICT_VALIDATION="true"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8884/health || exit 1

# Expose API port
EXPOSE 8884

# Default command - runs the API server
CMD ["python", "src/ash_thrash_api.py"]