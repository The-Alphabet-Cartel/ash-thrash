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
