#!/bin/bash
# Setup script for test environment

set -e

echo "================================================"
echo "Phishing Demo - Test Environment Setup"
echo "================================================"
echo ""

# Check if ChromeDriver is installed
if ! command -v chromedriver &> /dev/null; then
    echo "⚠️  ChromeDriver not found. Installing via Homebrew..."
    if command -v brew &> /dev/null; then
        brew install chromedriver
        echo "✓ ChromeDriver installed"
    else
        echo "❌ Homebrew not found. Please install ChromeDriver manually:"
        echo "   brew install chromedriver"
        echo "   OR download from: https://chromedriver.chromium.org/downloads"
        exit 1
    fi
else
    echo "✓ ChromeDriver found: $(which chromedriver)"
fi

# Check if .env file exists (in parent directory)
if [ ! -f ../.env ]; then
    echo "❌ .env file not found in parent directory. Please create it with required variables."
    exit 1
else
    echo "✓ .env file found"
fi

# Create virtual environment (in parent directory)
if [ ! -d "../venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    cd .. && python3 -m venv venv && cd tests
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo ""
echo "Installing test dependencies..."
source ../venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r test_requirements.txt
echo "✓ Test dependencies installed"

echo ""
echo "================================================"
echo "✓ Setup Complete!"
echo "================================================"
echo ""
echo "To run tests:"
echo "  cd tests"
echo "  source ../venv/bin/activate"
echo "  python test_full_flow.py"
echo ""
echo "Or use the helper script:"
echo "  cd tests && ./run_test.sh"
echo ""
