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
        echo "🔍 Continuing anyway for debugging..."
    fi
fi

# Check if required Python files exist
if [ ! -f "/app/src/quick_validation.py" ]; then
    echo "❌ Missing required file: /app/src/quick_validation.py"
    echo "📝 Please ensure source files are properly mounted or copied"
fi

if [ ! -f "/app/src/comprehensive_testing.py" ]; then
    echo "❌ Missing required file: /app/src/comprehensive_testing.py"  
    echo "📝 Please ensure source files are properly mounted or copied"
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
        
        # Run initial validation but don't exit if it fails
        echo "🔍 Running initial validation"
        if python /app/src/quick_validation.py; then
            echo "✅ Initial validation completed successfully"
        else
            echo "⚠️  Initial validation had issues, but continuing to run"
            echo "   You can debug with: docker-compose exec ash-thrash python src/quick_validation.py"
        fi
        
        echo "🏃 Container staying alive for on-demand testing..."
        echo "📝 Available commands:"
        echo "   - docker-compose exec ash-thrash python src/quick_validation.py"
        echo "   - docker-compose exec ash-thrash python src/comprehensive_testing.py"
        echo "   - docker-compose exec ash-thrash bash"
        
        # Keep container running
        tail -f /dev/null
        ;;
    "api")
        echo "🌐 Starting API server"
        cd /app
        
        # Check if we should use development or production server
        if [ "$API_DEBUG" = "true" ]; then
            echo "🔧 Running in development mode with Flask dev server"
            python -m src.api.server
        else
            echo "🚀 Running in production mode with Gunicorn"
            # Use Gunicorn for production
            gunicorn --bind 0.0.0.0:8884 \
                     --workers 4 \
                     --worker-class sync \
                     --timeout 120 \
                     --keepalive 2 \
                     --max-requests 1000 \
                     --max-requests-jitter 100 \
                     --access-logfile - \
                     --error-logfile - \
                     --log-level info \
                     "src.api.server:create_app()"
        fi
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
        echo "🏃 Defaulting to testing mode..."
        exec "$0" "testing"
        ;;
esac