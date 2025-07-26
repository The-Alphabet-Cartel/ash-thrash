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
