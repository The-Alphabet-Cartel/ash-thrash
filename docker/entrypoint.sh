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
        exit 1
    fi
fi

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
