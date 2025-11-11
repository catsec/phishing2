# Phishing Awareness Training Demo | הדגמת מודעות לפישינג

[English](#english) | [עברית](#hebrew)

---

<a name="english"></a>
## English

### WARNING - Educational Use Only

This application simulates a phishing attack for **authorized security awareness training purposes ONLY**.

**DO NOT:**
- Use this for actual phishing attacks
- Use on unauthorized systems
- Enter real personal information
- Use real credit card numbers

This tool is designed for educational demonstrations in controlled environments to help users recognize phishing attempts.

---

### Overview

A Flask-based phishing awareness training application that demonstrates:
- Fake banking phishing pages
- SMS phishing (smishing) techniques
- OTP capture methods
- Real-time attacker control panel
- Complete phishing attack flow simulation

**Key Features:**
- Multi-stage phishing flow (card capture → transaction alert → OTP)
- Admin dashboard with SMS sending capability (Twilio integration)
- Real-time data capture display
- Hebrew RTL interface for realistic Israeli banking simulation
- Terminal-style hacker dashboard
- Session-based authentication
- In-memory data storage (nothing persisted)

---

### Quick Start

#### Prerequisites
- Docker and Docker Compose **OR**
- Python 3.13+
- Twilio account (for SMS functionality)

#### Installation

**Option 1: Pre-built Docker Image (Fastest)**

```bash
# Pull the pre-built image from Docker Hub
docker pull ramprass/phishing-demo:latest

# Create .env file with your credentials
cat > .env <<'EOF'
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
DEFAULT_FROM_NUMBER=BANK
DEFAULT_SMS_MESSAGE=Your SMS message here
COMPANY_HEBREW=בנק
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_this_password
PORT=9999
FLASK_DEBUG=false
BEHIND_HTTPS_PROXY=false
DEFAULT_TO_NUMBER=+9725
EOF

# Run the container
docker run -d \
  --name phishing-demo \
  -p 9999:9999 \
  --env-file .env \
  ramprass/phishing-demo:latest
```

The application will be available at `http://localhost:9999`

**Option 2: Docker Compose (Build from Source)**

```bash
# Clone the repository
git clone https://github.com/catsec/phishing2.git
cd phishing2

# Copy example .env and configure your credentials
cp .env.example .env
# Edit .env with your actual credentials

# ⚠️ SECURITY WARNING: Change the default admin credentials!

# Start the application
docker-compose up
```

The application will be available at `http://localhost:9999`

**Option 3: Python Virtual Environment**

```bash
# Create virtual environment
python3.13 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install flask twilio flask-wtf

# Set required environment variables
export TWILIO_ACCOUNT_SID="your-twilio-sid"
export TWILIO_AUTH_TOKEN="your-twilio-token"
export DEFAULT_FROM_NUMBER="BANK"
export DEFAULT_SMS_MESSAGE="This is a test message from your bank"
export COMPANY_HEBREW="בנק"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="password"
export PORT="9999"
export FLASK_DEBUG="false"

# Run the application
python phishing_demo.py
```

---

### Usage

#### For Demonstrators (Attackers)

1. **Access Admin Panel:**
   - Navigate to `http://localhost:9999/login`
   - Login with credentials (default: admin/password)

2. **Hacker Dashboard:**
   - View captured credit card data
   - View captured OTP codes
   - Send SMS messages via Twilio
   - Control victim flow (advance to next stage)
   - Clear data for new demonstrations

3. **SMS Sending:**
   - Enter "from" number (can be alphanumeric like "Cal")
   - Enter victim's phone number
   - Compose message (supports Hebrew RTL)
   - Click send

4. **Flow Control:**
   - Wait for victim to submit card details
   - Click "Continue to Transaction Alert" when ready
   - Victim proceeds through transaction alert → OTP entry
   - View all captured data in real-time

#### For Participants (Victims)

1. **Receive SMS** with phishing link
2. **Click link** → lands on fake banking page
3. **Enter card details** → loading page (waits for attacker)
4. **Transaction alert** → shows fake suspicious transaction
5. **Enter OTP** → final capture
6. **Success page** → shows reference number

#### Test Data

Use these test credentials for demonstrations:
- **Name:** test test
- **Card Number:** 4580123412341232
- **Expiry:** 12/35
- **CVV:** 123
- **OTP:** Any 6 digits

---

### Project Structure

```
phishing2/
├── phishing_demo.py          # Main Flask application
├── logo.png                  # Logo image
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose setup
├── templates/                # HTML templates
│   ├── phishing_form.html    # Initial card capture page
│   ├── loading.html          # Waiting page
│   ├── transaction_alert.html # Fake transaction alert
│   ├── otp.html              # OTP entry page
│   ├── verification_success.html # Final success page
│   ├── hacker_dashboard.html # Admin control panel
│   ├── login.html            # Admin login
│   └── disclaimer.html       # Disclaimer/warning page
└── static/
    └── css/
        └── main.css          # Unified stylesheet
```

---

### Security Features

- Session-based authentication for admin routes
- CSRF protection on all forms (Flask-WTF)
- Input validation and sanitization
- Security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
- Thread-safe state management
- No persistent data storage (in-memory only)
- Environment-based configuration (no hardcoded secrets)

---

### Configuration

All configuration via environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `TWILIO_ACCOUNT_SID` | Twilio account ID | ACxxxxxxxxxx |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | Your token |
| `DEFAULT_FROM_NUMBER` | Default SMS sender | BANK or +1234567890 |
| `DEFAULT_SMS_MESSAGE` | Default SMS template | Your message |
| `COMPANY_HEBREW` | Company name in Hebrew | בנק |
| `ADMIN_USERNAME` | Admin login username | admin |
| `ADMIN_PASSWORD` | Admin login password | password |
| `PORT` | Application port | 9999 |
| `FLASK_DEBUG` | Debug mode | false |

**Note:** The Flask SECRET_KEY is automatically generated at startup using a cryptographically secure random value. No configuration needed.

See `docker-compose.yml` for default values.

---

### Endpoints

**Victim Flow:**
- `/` - Phishing form (Hebrew banking interface)
- `/submit` - Card data submission
- `/check_ready` - Polling endpoint for flow control
- `/transaction_alert` - Fake transaction alert
- `/otp` - OTP entry page
- `/verify` - OTP verification & reference number generation
- `/disclaimer` - Warning and information page

**Admin Routes (Authentication Required):**
- `/login` - Admin login page
- `/hacker` - Main dashboard
- `/hacker/data` - JSON API for captured data
- `/hacker/continue` - Advance victim flow
- `/hacker/clear` - Clear all captured data
- `/send` - SMS sending API

---

### Features

- **Hebrew RTL Support:** Realistic Israeli banking interface
- **Terminal Theme:** Matrix-style hacker dashboard
- **Real-time Updates:** Auto-refreshing dashboard (2-second interval)
- **Reference Number:** 10-digit unique reference based on card data
- **Flow Control:** Attacker controls victim progression
- **Prominent Warnings:** Red pulsing disclaimer footer on all pages

---

### License & Disclaimer

**This software is for educational and authorized security training purposes only.**

By using this software, you agree to:
- Only use it in controlled, authorized environments
- Never use it for malicious purposes
- Not enter real personal or financial information
- Comply with all applicable laws and regulations

The authors and contributors are not responsible for misuse of this software.

---

### Development

**Built with:**
- Python 3.13
- Flask 3.1+
- Flask-WTF (CSRF protection)
- Twilio Python SDK
- Docker

**Created by:** catsec.com

---

<a name="hebrew"></a>
## עברית

### אזהרה - לשימוש חינוכי בלבד

אפליקציה זו מדמה התקפת פישינג **למטרות הדרכה מורשות בלבד**.

**אין לעשות:**
- שימוש למטרות פישינג אמיתיות
- שימוש על מערכות לא מורשות
- הזנת מידע אישי אמיתי
- שימוש במספרי כרטיסי אשראי אמיתיים

כלי זה מיועד להדגמות חינוכיות בסביבות מבוקרות כדי לעזור למשתמשים לזהות ניסיונות פישינג.

---

### סקירה כללית

אפליקציית הדרכה מבוססת Flask המדגימה:
- דפי פישינג מזויפים של בנקים
- טכניקות פישינג SMS (smishing)
- שיטות לכידת OTP
- לוח בקרה של תוקף בזמן אמת
- סימולציה של זרימת התקפת פישינג מלאה

**תכונות עיקריות:**
- זרימת פישינג רב-שלבית (לכידת כרטיס → התראת עסקה → OTP)
- לוח ניהול מנהל עם יכולת שליחת SMS (אינטגרציית Twilio)
- תצוגת לכידת נתונים בזמן אמת
- ממשק עברי RTL לסימולציה ריאליסטית של בנקאות ישראלית
- לוח בקרה בסגנון טרמינל
- אימות מבוסס session
- אחסון נתונים בזיכרון (שום דבר לא נשמר)

---

### התחלה מהירה

#### דרישות מקדימות
- Docker ו-Docker Compose **או**
- Python 3.13+
- חשבון Twilio (לפונקציונליות SMS)

#### התקנה

**אפשרות 1: Docker Image מוכן מראש (הכי מהיר)**

```bash
# משיכת ה-image המוכן מ-Docker Hub
docker pull ramprass/phishing-demo:latest

# יצירת קובץ .env עם האישורים שלך
cat > .env <<'EOF'
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
DEFAULT_FROM_NUMBER=BANK
DEFAULT_SMS_MESSAGE=הודעת SMS שלך כאן
COMPANY_HEBREW=בנק
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_this_password
PORT=9999
FLASK_DEBUG=false
BEHIND_HTTPS_PROXY=false
DEFAULT_TO_NUMBER=+9725
EOF

# הרצת ה-container
docker run -d \
  --name phishing-demo \
  -p 9999:9999 \
  --env-file .env \
  ramprass/phishing-demo:latest
```

האפליקציה תהיה זמינה ב-`http://localhost:9999`

**אפשרות 2: Docker Compose (בניה מקוד מקור)**

```bash
# שיבוט המאגר
git clone https://github.com/catsec/phishing2.git
cd phishing2

# העתקת .env לדוגמה והגדרת האישורים שלך
cp .env.example .env
# ערוך .env עם האישורים האמיתיים שלך

# ⚠️ אזהרת אבטחה: שנה את אישורי ברירת המחדל של המנהל!

# הפעלת האפליקציה
docker-compose up
```

האפליקציה תהיה זמינה ב-`http://localhost:9999`

**אפשרות 3: סביבה וירטואלית של Python**

```bash
# יצירת סביבה וירטואלית
python3.13 -m venv venv

# הפעלת הסביבה הוירטואלית
source venv/bin/activate  # ב-Windows: venv\Scripts\activate

# התקנת תלויות
pip install flask twilio flask-wtf

# הגדרת משתני סביבה נדרשים
export TWILIO_ACCOUNT_SID="your-twilio-sid"
export TWILIO_AUTH_TOKEN="your-twilio-token"
export DEFAULT_FROM_NUMBER="BANK"
export DEFAULT_SMS_MESSAGE="הודעת SMS שלך כאן"
export COMPANY_HEBREW="בנק"
export ADMIN_USERNAME="admin"
export ADMIN_PASSWORD="password"
export PORT="9999"
export FLASK_DEBUG="false"

# הרצת האפליקציה
python phishing_demo.py
```

---

### שימוש

#### למדגימים (תוקפים)

1. **גישה ללוח הניהול:**
   - ניווט ל-`http://localhost:9999/login`
   - התחברות עם אישורים (ברירת מחדל: admin/password)

2. **לוח בקרה:**
   - צפייה בנתוני כרטיסי אשראי שנלכדו
   - צפייה בקודי OTP שנלכדו
   - שליחת הודעות SMS דרך Twilio
   - שליטה בזרימת הקורבן (קידום לשלב הבא)
   - ניקוי נתונים להדגמות חדשות

3. **שליחת SMS:**
   - הזנת מספר "מאת" (יכול להיות אלפאנומרי כמו "Cal")
   - הזנת מספר טלפון של הקורבן
   - כתיבת הודעה (תומך בעברית RTL)
   - לחיצה על שלח

4. **בקרת זרימה:**
   - המתנה לקורבן להגיש פרטי כרטיס
   - לחיצה על "Continue to Transaction Alert" כשמוכן
   - הקורבן ממשיך דרך התראת עסקה → הזנת OTP
   - צפייה בכל הנתונים שנלכדו בזמן אמת

#### למשתתפים (קורבנות)

1. **קבלת SMS** עם קישור פישינג
2. **לחיצה על הקישור** → נחיתה בדף בנקאות מזויף
3. **הזנת פרטי כרטיס** → דף טעינה (ממתין לתוקף)
4. **התראת עסקה** → מציג עסקה חשודה מזויפת
5. **הזנת OTP** → לכידה סופית
6. **דף הצלחה** → מציג מספר אסמכתא

#### נתוני בדיקה

השתמש באישורים אלה להדגמות:
- **שם:** test test
- **מספר כרטיס:** 4580123412341232
- **תוקף:** 12/35
- **CVV:** 123
- **OTP:** כל 6 ספרות

---

### מבנה הפרויקט

```
phishing2/
├── phishing_demo.py          # אפליקציית Flask ראשית
├── logo.png                  # תמונת לוגו
├── Dockerfile                # תצורת Docker
├── docker-compose.yml        # הגדרת Docker Compose
├── templates/                # תבניות HTML
│   ├── phishing_form.html    # דף לכידת כרטיס ראשוני
│   ├── loading.html          # דף המתנה
│   ├── transaction_alert.html # התראת עסקה מזויפת
│   ├── otp.html              # דף הזנת OTP
│   ├── verification_success.html # דף הצלחה סופי
│   ├── hacker_dashboard.html # לוח בקרה של מנהל
│   ├── login.html            # התחברות מנהל
│   └── disclaimer.html       # דף אזהרה/מידע
└── static/
    └── css/
        └── main.css          # גיליון סגנון מאוחד
```

---

### תכונות אבטחה

- אימות מבוסס session למסלולי מנהל
- הגנת CSRF על כל הטפסים (Flask-WTF)
- אימות וחיטוי קלט
- כותרות אבטחה (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
- ניהול מצב thread-safe
- אין אחסון נתונים קבוע (בזיכרון בלבד)
- תצורה מבוססת סביבה (אין סודות מוקשים)

---

### תצורה

כל התצורה באמצעות משתני סביבה:

| משתנה | תיאור | דוגמה |
|-------|--------|--------|
| `TWILIO_ACCOUNT_SID` | מזהה חשבון Twilio | ACxxxxxxxxxx |
| `TWILIO_AUTH_TOKEN` | טוקן אימות Twilio | הטוקן שלך |
| `DEFAULT_FROM_NUMBER` | שולח SMS ברירת מחדל | BANK או +1234567890 |
| `DEFAULT_SMS_MESSAGE` | תבנית SMS ברירת מחדל | ההודעה שלך |
| `COMPANY_HEBREW` | שם החברה בעברית | בנק |
| `ADMIN_USERNAME` | שם משתמש להתחברות מנהל | admin |
| `ADMIN_PASSWORD` | סיסמת מנהל | password |
| `PORT` | פורט אפליקציה | 9999 |
| `FLASK_DEBUG` | מצב debug | false |

**הערה:** ה-SECRET_KEY של Flask נוצר אוטומטית בהפעלה באמצעות ערך אקראי מאובטח קריפטוגרפית. אין צורך בתצורה.

ראה `docker-compose.yml` לערכי ברירת מחדל.

---

### נקודות קצה

**זרימת קורבן:**
- `/` - טופס פישינג (ממשק בנקאי עברי)
- `/submit` - הגשת נתוני כרטיס
- `/check_ready` - נקודת polling לבקרת זרימה
- `/transaction_alert` - התראת עסקה מזויפת
- `/otp` - דף הזנת OTP
- `/verify` - אימות OTP ויצירת מספר אסמכתא
- `/disclaimer` - דף אזהרה ומידע

**מסלולי מנהל (נדרש אימות):**
- `/login` - דף התחברות מנהל
- `/hacker` - לוח בקרה ראשי
- `/hacker/data` - API JSON לנתונים שנלכדו
- `/hacker/continue` - קידום זרימת קורבן
- `/hacker/clear` - ניקוי כל הנתונים שנלכדו
- `/send` - API שליחת SMS

---

### תכונות

- **תמיכה בעברית RTL:** ממשק בנקאי ישראלי ריאליסטי
- **ערכת טרמינל:** לוח בקרה בסגנון Matrix
- **עדכונים בזמן אמת:** לוח בקרה מתרענן אוטומטית (מרווח של 2 שניות)
- **מספר אסמכתא:** אסמכתא ייחודית בת 10 ספרות מבוססת נתוני כרטיס
- **בקרת זרימה:** התוקף שולט בהתקדמות הקורבן
- **אזהרות בולטות:** כותרת אזהרה אדומה פועמת בכל הדפים

---

### רישיון ואזהרה

**תוכנה זו מיועדת למטרות חינוכיות והדרכה מורשות בלבד.**

על ידי שימוש בתוכנה זו, אתה מסכים:
- להשתמש בה רק בסביבות מבוקרות ומורשות
- לעולם לא להשתמש בה למטרות זדוניות
- לא להזין מידע אישי או פיננסי אמיתי
- לציית לכל החוקים והתקנות החלים

המחברים והתורמים אינם אחראים לשימוש לרעה בתוכנה זו.

---

### פיתוח

**נבנה עם:**
- Python 3.13
- Flask 3.1+
- Flask-WTF (הגנת CSRF)
- Twilio Python SDK
- Docker

**נוצר על ידי:** catsec.com

---

## Support | תמיכה

For issues, questions, or contributions, please contact catsec.com

לבעיות, שאלות או תרומות, אנא צור קשר עם catsec.com
