# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Phishing Awareness Training Demonstration Application** - a Flask-based web application that simulates a phishing attack flow for authorized security training purposes only. The application demonstrates how attackers capture sensitive data (credit cards, OTP codes) through a multi-stage phishing scenario.

**⚠️ WARNING:** This application contains code that simulates malicious phishing techniques. It is intended ONLY for authorized security awareness training and should never be used for actual phishing attacks or unauthorized access.

## Test Data

For manual testing of the phishing flow:
- **Name:** test test
- **Card Number:** 4580123412341232
- **Expiry Date:** 12/35
- **CVV:** 123
- **Admin Username:** cat
- **Admin Password:** meowmeow

## Common Development Commands

### Running the Application

**Using Docker Compose (recommended):**
```bash
docker-compose up
```
The application will be available at `http://localhost:9999`

**Using Docker directly:**
```bash
docker build -t phishing-demo .
docker run -p 9999:9999 -e TWILIO_ACCOUNT_SID=your_sid -e TWILIO_AUTH_TOKEN=your_token phishing-demo
```

**Running Python directly (for development):**
```bash
# Create virtual environment (first time only)
python3.13 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies (first time only)
pip install flask twilio flask-wtf

# Run the application
python phishing_demo.py
```

**Setting environment variables for local development:**
```bash
export SECRET_KEY="your-secret-key"
export TWILIO_ACCOUNT_SID="your-twilio-sid"
export TWILIO_AUTH_TOKEN="your-twilio-token"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="password"
```

### Building & Deployment

**Build Docker image:**
```bash
docker build -t phishing-demo .
```

**Rebuild Docker image after code changes:**
```bash
docker-compose build
docker-compose up
```

### Testing & Validation

**Note:** No automated test framework is currently configured. Manual testing is required:
- Access the phishing form at `http://localhost:9999/`
- Submit test credit card data
- Access the attacker control panel at `http://localhost:9999/hacker`
- Verify SMS functionality if Twilio credentials are configured

## Architecture & Code Structure

### Flask Application Structure

The entire application is contained in `phishing_demo.py` (1,267 lines) with the following key components:

#### Data Flow - Victim Journey
1. **Initial Form** (`/`) - Hebrew-language phishing page that mimics a banking interface, captures credit card details
2. **Card Submission** (`/submit`) - Validates card data using Luhn algorithm, stores in memory
3. **Loading/Status Check** (`/check_ready`) - Polls for attacker interaction
4. **Transaction Alert** (`/transaction_alert`) - Fake suspicious transaction notification
5. **OTP Page** (`/otp`) - Fake OTP verification page
6. **OTP Submission** (`/verify`) - Captures OTP code, completes data collection

#### Control Panel - Attacker Interface
- **Login** (`/login`) - Authentication page for accessing restricted areas
- **Dashboard** (`/hacker`) - HTML dashboard displaying captured data (requires authentication)
- **Data API** (`/hacker/data`) - JSON endpoint returning captured card and OTP data
- **Continue Control** (`/hacker/continue`) - Allows attacker to advance victim through phishing flow
- **Clear Data** (`/hacker/clear`) - Clears captured data and resets for new demo
- **Logout** (`/logout`) - Clears user session and redirects to login

#### Additional Endpoints
- **SMS Interface** (`/sms`) - Web interface for sending SMS messages via Twilio (requires authentication)
- **SMS API** (`/send`) - Backend endpoint for SMS submission (requires authentication)
- **Logo** (`/logo.png`) - Serves static image asset

### Data Capture & Storage

Captured data is stored in memory with this structure:
```python
captured_data = {
    'card': {
        'timestamp': 'YYYY-MM-DD HH:MM:SS',
        'cardholder_name': 'string',
        'card_number': 'string',
        'expiry_date': 'string',
        'cvv': 'string'
    },
    'otp': {
        'timestamp': 'YYYY-MM-DD HH:MM:SS',
        'code': 'string'
    }
}
```

### Key Libraries & Dependencies

- **Flask 3.1+** - Web framework for routing and request handling
- **Flask-WTF** - CSRF protection for forms
- **Twilio** (`twilio.rest`) - SMS delivery integration
- **Standard Library** - `datetime`, `os`, `typing`, `html`
- **Python 3.13+** - Current version used in development and Docker

### Configuration

**Environment Variables (ALL REQUIRED):**
- `TWILIO_ACCOUNT_SID` - Twilio account identifier (required, no default)
- `TWILIO_AUTH_TOKEN` - Twilio authentication token (required, no default)
- `ADMIN_USERNAME` - Username for admin login (required, no default)
- `ADMIN_PASSWORD` - Password for admin login (required, no default)
- `SECRET_KEY` - Flask session secret key for security (required, no default)

**Note:** The application will fail to start if any required environment variable is missing. See `docker-compose.yml` for example values used in Docker deployments.

**Port Configuration:**
- Default port: `9999` (configured in `docker-compose.yml` and `Dockerfile`)

### Authentication

The `/hacker` and `/sms` endpoints are protected with session-based authentication:
- Users must login at `/login` with valid credentials
- Session tokens are stored in Flask sessions (requires `SECRET_KEY`)
- Users can logout at `/logout` which clears the session
- Authentication is enforced via the `@require_auth` decorator on protected routes

### HTML & JavaScript Templates

The application includes embedded HTML/JavaScript within Python strings for:
- Phishing form page with card input validation (Luhn algorithm for credit cards)
- Hebrew-RTL layout for realistic Hebrew banking interface
- Attacker control dashboard with real-time data display
- Client-side form validation using JavaScript regex patterns

**Important:** When editing JavaScript code within Python template strings, escape backslashes in regex patterns (e.g., `\\D` instead of `\D`) to avoid Python syntax warnings.

## Security Considerations & Limitations

**Implemented Security Features:**
- Session-based authentication on `/hacker` and `/sms` endpoints
- Login page with username/password validation
- Logout functionality to clear sessions
- Configurable admin credentials via environment variables (no hardcoded defaults)
- CSRF protection on all forms via Flask-WTF
- XSS prevention via input sanitization (`html.escape()`) and safe DOM manipulation
- Security headers: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- All credentials required from environment variables (fail loudly if missing)
- No sensitive data logged to console

**Design Considerations:**
- HTTPS/TLS encryption: Handled by reverse proxy (application assumes HTTPS)
- Data stored in-memory only (appropriate for demo purposes)
- No cross-origin requests needed (operates behind reverse proxy)
- No rate limiting implemented (demo-specific, not production)

**Production Use:** This application is NOT suitable for production use without: proper secrets management, rate limiting, HTTPS enforcement, secure session storage, and comprehensive logging.

## Deployment

### Docker Configuration

**Dockerfile:** Python 3.13 Alpine base image with Flask, Flask-WTF, and Twilio dependencies
**docker-compose.yml:** Defines service with port mapping (9999:9999), environment variables, and auto-restart policy

## Development Guidelines

When modifying this application:
- Keep all HTML/JavaScript templates in the main `phishing_demo.py` file
- Maintain Hebrew RTL support for the phishing form
- Update both Flask routes and corresponding HTML forms together
- Use proper type hints (imported from `typing` module) for data structures
- Escape backslashes in JavaScript regex patterns within Python strings
- Test both locally (with venv) and via Docker Compose before deploying

### VS Code Setup

The project includes `.vscode/settings.json` configured for Python 3.13 development:
- Virtual environment auto-activation in terminals
- Python interpreter path points to `venv/bin/python`
- Type checking enabled at basic level
