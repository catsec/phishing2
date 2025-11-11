# Fix ChromeDriver on macOS

## The Problem

macOS blocks ChromeDriver with an error like:
- "chromedriver cannot be opened because the developer cannot be verified"
- "chromedriver is damaged and can't be opened"

## Solution

### Method 1: Remove Quarantine Attribute (Recommended)

```bash
# Find where ChromeDriver is installed
which chromedriver

# Remove the quarantine attribute
xattr -d com.apple.quarantine $(which chromedriver)
```

### Method 2: Allow in System Preferences

1. Try to run ChromeDriver:
   ```bash
   chromedriver
   ```

2. macOS will show a security warning

3. Go to: **System Preferences → Security & Privacy → General**

4. Click **"Allow Anyway"** next to the ChromeDriver message

5. Try running ChromeDriver again

6. Click **"Open"** in the new dialog

### Method 3: Manual Installation with Permissions

```bash
# Download ChromeDriver manually
# Visit: https://chromedriver.chromium.org/downloads

# After downloading, move to /usr/local/bin
sudo mv ~/Downloads/chromedriver /usr/local/bin/

# Make it executable
sudo chmod +x /usr/local/bin/chromedriver

# Remove quarantine
sudo xattr -d com.apple.quarantine /usr/local/bin/chromedriver

# Verify it works
chromedriver --version
```

### Method 4: Using Homebrew with Auto-Fix

```bash
# Uninstall if already installed
brew uninstall chromedriver

# Reinstall
brew install --cask chromedriver

# Remove quarantine
xattr -d com.apple.quarantine /usr/local/bin/chromedriver

# Or if installed via Homebrew Cask
xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver
```

## Quick Fix Script

Run this to automatically fix ChromeDriver:

```bash
#!/bin/bash
# Fix ChromeDriver permissions on macOS

echo "Locating ChromeDriver..."
CHROMEDRIVER_PATH=$(which chromedriver)

if [ -z "$CHROMEDRIVER_PATH" ]; then
    echo "❌ ChromeDriver not found. Install it first:"
    echo "   brew install chromedriver"
    exit 1
fi

echo "✓ Found at: $CHROMEDRIVER_PATH"
echo ""
echo "Removing quarantine attribute..."

xattr -d com.apple.quarantine "$CHROMEDRIVER_PATH" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Quarantine removed successfully"
else
    echo "⚠ Quarantine attribute not present or already removed"
fi

echo ""
echo "Making executable..."
chmod +x "$CHROMEDRIVER_PATH"

echo ""
echo "Testing ChromeDriver..."
"$CHROMEDRIVER_PATH" --version

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ ChromeDriver is working!"
else
    echo ""
    echo "❌ ChromeDriver test failed"
    echo ""
    echo "Try this manual method:"
    echo "1. Run: chromedriver"
    echo "2. Go to System Preferences → Security & Privacy"
    echo "3. Click 'Allow Anyway'"
    echo "4. Run again and click 'Open'"
fi
```

Save this as `fix_chromedriver.sh` and run:
```bash
chmod +x fix_chromedriver.sh
./fix_chromedriver.sh
```

## Alternative: Use WebDriver Manager (No Manual ChromeDriver Needed)

Instead of installing ChromeDriver manually, use `webdriver-manager`:

### Update test_requirements.txt:
```
selenium>=4.15.0
python-dotenv>=1.0.0
requests>=2.31.0
webdriver-manager>=4.0.0
```

### Update test_full_flow.py:
```python
# Replace the setup_driver function with:

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """Setup Chrome WebDriver with automatic driver management"""
    log_step("Setting up Chrome WebDriver")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')

    # Automatically download and manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    log_success("Chrome WebDriver initialized")
    return driver
```

Then:
```bash
source venv/bin/activate
pip install webdriver-manager
python test_full_flow.py
```

This will automatically download and use the correct ChromeDriver version!

## Verification

Test if ChromeDriver works:

```bash
chromedriver --version
```

Expected output:
```
ChromeDriver 120.0.6099.109 (...)
```

## Still Not Working?

If none of the above work, use the WebDriver Manager approach - it completely bypasses the macOS security issues by managing ChromeDriver programmatically.
