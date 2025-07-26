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
