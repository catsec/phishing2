# Automated End-to-End Testing

This directory contains automated tests for the Phishing Demo application.

## Prerequisites

### 1. Install Chrome WebDriver

**macOS (using Homebrew):**
```bash
brew install chromedriver
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install chromium-chromedriver
```

**Or download manually:**
- Visit: https://chromedriver.chromium.org/downloads
- Download the version matching your Chrome browser
- Add to PATH

### 2. Install Python Dependencies

**Option A: Using Setup Script (Recommended)**
```bash
cd tests
./setup_test.sh
```

**Option B: Manual Setup**
```bash
# From project root, create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install test dependencies
pip install -r tests/test_requirements.txt
```

### 3. Configure Environment Variables

Ensure your `.env` file (in project root) has all required variables:

```bash
# Required for tests
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD=your_admin_password
PORT=9999

# Other required variables (can be test values)
TWILIO_ACCOUNT_SID=test
TWILIO_AUTH_TOKEN=test
DEFAULT_FROM_NUMBER=test
DEFAULT_SMS_MESSAGE=test message
COMPANY_HEBREW=בנק
FLASK_DEBUG=false
```

## Running the Tests

### Run Full Test Suite

**Option 1: Using helper script (recommended):**
```bash
cd tests
./run_test.sh
```

**Option 2: Manual execution:**
```bash
cd tests
source ../venv/bin/activate
python test_full_flow.py
```

## What the Test Does

The automated test performs the following steps:

1. ✓ **Build Docker image** - `docker-compose build`
2. ✓ **Start Docker container** - `docker-compose up -d`
3. ✓ **Wait for container ready** - Health check on port
4. ✓ **Login to hacker dashboard** - Navigate to `/hacker`, enter credentials
5. ✓ **Send test SMS** - Fill and submit SMS form (expects Twilio error with test credentials)
6. ✓ **Victim enters card data** - Fill phishing form with test card
7. ✓ **Check hacker receives data** - Verify card data appears on dashboard
8. ✓ **Hacker clicks continue** - Advance victim to transaction alert
9. ✓ **Victim chooses "not me"** - Navigate to OTP page
10. ✓ **Victim enters OTP** - Submit 6-digit code (666666)
11. ✓ **Check hacker receives OTP** - Verify OTP appears on dashboard
12. ✓ **Shutdown Docker** - `docker-compose down`

## Test Data Used

```python
Card Name:    "first last"
Card Number:  "4580 1234 1234 1232"
Expiry:       "12/50"
CVV:          "123"
OTP:          "666666"
SMS To:       "test"
SMS Message:  "testing"
```

## Expected Output

```
============================================================
Phishing Demo - Automated End-to-End Test
============================================================

▶ Configuration:
  - Port: 9999
  - Base URL: http://127.0.0.1:9999
  - Admin User: admin

▶ Building Docker image
✓ Building Docker image - Completed

▶ Starting Docker container
✓ Starting Docker container - Completed

▶ Waiting for Docker container to be ready (timeout: 60s)
✓ Docker container is ready and responding

▶ Setting up Chrome WebDriver
✓ Chrome WebDriver initialized

▶ Testing hacker login
✓ Successfully logged in to hacker dashboard

▶ Testing SMS sending
⚠ SMS sending failed (expected with test credentials): ERROR: ...

▶ Testing victim card entry
✓ Victim card details submitted successfully

▶ Checking if hacker received card data
✓ Hacker dashboard shows captured card data

▶ Testing hacker continue to transaction alert
✓ Hacker clicked continue button

▶ Testing victim transaction alert
✓ Victim proceeded to OTP page

▶ Testing victim OTP entry
✓ Victim OTP submitted successfully

▶ Checking if hacker received OTP
✓ Hacker dashboard shows captured OTP: 666666

============================================================
✓ ALL TESTS PASSED SUCCESSFULLY!
============================================================

▶ Shutting down Docker container
✓ Shutting down Docker container - Completed

Test execution completed
```

## Troubleshooting

### ChromeDriver Not Found

```bash
# Install ChromeDriver
brew install chromedriver

# Or add to PATH
export PATH=$PATH:/path/to/chromedriver
```

### Docker Not Running

```bash
# Start Docker Desktop (macOS/Windows)
# Or start Docker service (Linux)
sudo systemctl start docker
```

### Port Already in Use

```bash
# Check what's using the port
lsof -i :9999

# Kill the process or change PORT in .env
```

### Test Fails at Specific Step

- Check Docker logs: `docker-compose logs`
- Run with visible browser (remove `--headless` in script)
- Increase timeout values in the script

## Running Tests in Visible Browser Mode

To see what the test is doing, edit `test_full_flow.py`:

```python
def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # Comment this line
    chrome_options.add_argument('--no-sandbox')
    ...
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install -r test_requirements.txt
          sudo apt-get install chromium-chromedriver
      - name: Run tests
        run: python test_full_flow.py
        env:
          ADMIN_USERNAME: ${{ secrets.ADMIN_USERNAME }}
          ADMIN_PASSWORD: ${{ secrets.ADMIN_PASSWORD }}
```

## Notes

- The SMS test will show a warning with test Twilio credentials (this is expected)
- All tests run in headless mode by default (no visible browser windows)
- The test automatically cleans up Docker containers after completion
- Exit code 0 = all tests passed, exit code 1 = test failed

## Support

For issues with the test suite, check:
1. All environment variables are set in `.env`
2. Docker Desktop is running
3. Port 9999 is available
4. ChromeDriver is installed and in PATH
