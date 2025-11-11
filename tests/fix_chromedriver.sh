#!/bin/bash
# Automatically fix ChromeDriver permissions on macOS

set -e

echo "================================================"
echo "ChromeDriver macOS Permission Fix"
echo "================================================"
echo ""

# Locate ChromeDriver
echo "🔍 Locating ChromeDriver..."
CHROMEDRIVER_PATH=$(which chromedriver 2>/dev/null || echo "")

if [ -z "$CHROMEDRIVER_PATH" ]; then
    echo "❌ ChromeDriver not found in PATH"
    echo ""
    echo "Installing via Homebrew..."
    if command -v brew &> /dev/null; then
        brew install chromedriver
        CHROMEDRIVER_PATH=$(which chromedriver)
        echo "✓ ChromeDriver installed at: $CHROMEDRIVER_PATH"
    else
        echo "❌ Homebrew not found. Please install ChromeDriver manually:"
        echo "   1. Download from: https://chromedriver.chromium.org/downloads"
        echo "   2. Move to /usr/local/bin/chromedriver"
        echo "   3. Run this script again"
        exit 1
    fi
else
    echo "✓ Found at: $CHROMEDRIVER_PATH"
fi

echo ""
echo "🔧 Removing quarantine attribute..."
xattr -d com.apple.quarantine "$CHROMEDRIVER_PATH" 2>/dev/null && echo "✓ Quarantine removed" || echo "⚠  Quarantine not present (may already be fixed)"

echo ""
echo "🔧 Setting executable permissions..."
chmod +x "$CHROMEDRIVER_PATH"
echo "✓ Executable permission set"

echo ""
echo "🧪 Testing ChromeDriver..."
if "$CHROMEDRIVER_PATH" --version 2>&1 | head -1; then
    echo ""
    echo "================================================"
    echo "✅ SUCCESS! ChromeDriver is working!"
    echo "================================================"
    echo ""
    echo "You can now run: ./run_test.sh"
    exit 0
else
    echo ""
    echo "================================================"
    echo "⚠️  Manual Step Required"
    echo "================================================"
    echo ""
    echo "Please do the following:"
    echo "1. Run: chromedriver"
    echo "2. Click OK when macOS shows security warning"
    echo "3. Go to: System Preferences → Security & Privacy → General"
    echo "4. Click 'Allow Anyway' next to ChromeDriver"
    echo "5. Run: chromedriver again"
    echo "6. Click 'Open' in the dialog"
    echo "7. Run this script again to verify"
    echo ""
    exit 1
fi
