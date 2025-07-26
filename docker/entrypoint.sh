#!/bin/bash
set -e

echo "🧪 Starting Ash-Thrash Container"
echo "Mode: $1"

# Wait for NLP server if URL is provided
if [ ! -z "$NLP_SERVER_URL" ]; then
    echo "⏳ Waiting for NLP server at $NLP_SERVER_URL..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -s --fail "$NLP_SERVER_URL/health" >/dev/null 2>&1; then
            echo "✅ NLP server is ready"
            break
        fi
        echo "Waiting for NLP server... ($timeout seconds remaining)"
        sleep 5
        timeout=$((timeout - 5))
    done
    
    if [ $timeout -le 0 ]; then
        echo "❌ NLP server not ready after 60 seconds"
        echo "🔍 Attempting to continue anyway for debugging..."
        # Don't exit, continue for debugging
    fi
fi

# Check if required Python files exist
if [ ! -f "/app/src/quick_validation.py" ]; then
    echo "❌ Missing required file: /app/src/quick_validation.py"
    echo "📝 Please ensure source files are properly mounted or copied"
    exit 1
fi

if [ ! -f "/app/src/comprehensive_testing.py" ]; then
    echo "❌ Missing required file: /app/src/comprehensive_testing.py"  
    echo "📝 Please ensure source files are properly mounted or copied"
    exit 1
fi

# Ensure results directory exists
mkdir -p /app/results/comprehensive
mkdir -p /app/results/quick_validation

case "$1" in
    "testing")
        echo "🧪 Starting testing service with scheduled jobs"
        # Start cron for scheduled testing
        if [ "$ENABLE_SCHEDULED_TESTING" = "true" ]; then
            echo "📅 Starting cron daemon"
            cron
        fi
        
        # Run initial validation
        echo "🔍 Running initial validation"
        python /app/src/quick_validation.py
        
        # Keep container running
        tail -f /dev/null
        ;;
    "api")
        echo "🌐 Starting API server"
        python /app/src/api/server.py
        ;;
    "comprehensive")
        echo "🧪 Running comprehensive test"
        python /app/src/comprehensive_testing.py
        ;;
    "quick")
        echo "🔍 Running quick validation"
        python /app/src/quick_validation.py
        ;;
    "bash")
        echo "🐚 Starting interactive bash shell"
        exec /bin/bash
        ;;
    *)
        echo "❌ Unknown mode: $1"
        echo "Available modes: testing, api, comprehensive, quick, bash"
        exit 1
        ;;
esac