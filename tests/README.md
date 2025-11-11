# Phishing Demo - Test Suite

Automated end-to-end testing for the phishing awareness training application.

## Quick Start

```bash
# Setup (first time only)
cd tests
./setup_test.sh

# Run tests
./run_test.sh
```

## Test Files

- **test_full_flow.py** - Main automated E2E test suite
- **test_requirements.txt** - Python dependencies for testing
- **setup_test.sh** - Automated test environment setup
- **run_test.sh** - Quick test runner script
- **fix_chromedriver.sh** - macOS ChromeDriver permission fix

## Documentation

- **QUICK_TEST.md** - Quick reference guide
- **TEST_README.md** - Complete testing documentation
- **FIX_CHROMEDRIVER.md** - ChromeDriver troubleshooting (macOS)

## Requirements

- Python 3.13+
- Docker & Docker Compose
- ChromeDriver (installed via Homebrew)
- `.env` file configured in project root

## Configuration

All configuration is in the project root `.env` file. See `.env.example` for required variables.

Test-specific constants are in `test_full_flow.py`:
- Test card number: 4580 1234 1234 1232
- Test OTP code: 666666
- Test SMS: From "TEST" to configured phone number

## Support

For detailed documentation, see [TEST_README.md](TEST_README.md).
