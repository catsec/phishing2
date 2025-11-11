#!/bin/bash
# Simple test runner that activates venv automatically

set -e

# Activate virtual environment (in parent directory)
if [ -d "../venv" ]; then
    source ../venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run setup_test.sh first."
    exit 1
fi

# Run tests
echo ""
python test_full_flow.py

# Capture exit code
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ All tests passed!"
else
    echo "❌ Tests failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE
