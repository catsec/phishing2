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
- Retro 80's hacker dashboard with Fira Code font
- Theme toggle (classic hacker / modern gradient)
- Session-based authentication with rate limiting
- In-memory data storage (nothing persisted)
- Automatic CSS cache busting via timestamp versioning
- Cloudflare-compatible cache control headers

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
pip install flask twilio flask-wtf flask-limiter

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

- **Authentication & Sessions:**
  - Session-based authentication for admin routes
  - Session fixation protection (regenerates on login)
  - Constant-time password comparison (prevents timing attacks)
  - Session timeout (1 hour)
  - HttpOnly, SameSite=Lax cookies
  - Optional Secure flag for HTTPS proxy setups

- **Input Protection:**
  - CSRF protection on all forms (Flask-WTF)
  - Comprehensive input validation (Luhn algorithm for cards, E.164 for phones)
  - Input sanitization (HTML escaping)
  - Length limits on all inputs

- **Rate Limiting:**
  - Login endpoint: 5 attempts per minute
  - SMS endpoint: 10 messages per minute
  - Global limits: 200 per day, 50 per hour

- **Security Headers:**
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Content-Security-Policy (restricts script/style sources)
  - Cache-Control: no-cache (prevents caching while allowing sessions)
  - CDN-Cache-Control: no-cache (Cloudflare-specific)

- **Additional Security:**
  - Thread-safe state management with locks
  - No persistent data storage (in-memory only)
  - Environment-based configuration (no hardcoded secrets)
  - Auto-generated cryptographic SECRET_KEY per deployment

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
| `BEHIND_HTTPS_PROXY` | Behind HTTPS reverse proxy | false |
| `DEFAULT_TO_NUMBER` | Default SMS recipient | +9725 |

**Notes:**
- The Flask SECRET_KEY is automatically generated at startup using a cryptographically secure random value
- CSS version is automatically set based on deployment timestamp for cache busting
- Set `BEHIND_HTTPS_PROXY=true` if behind Nginx Proxy Manager or similar HTTPS reverse proxies

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
- **Retro Hacker Theme:** 80's terminal aesthetic with Fira Code monospace font
- **Theme Toggle:** Switch between classic hacker (green on black) and modern gradient themes
- **Real-time Updates:** Auto-refreshing dashboard (2-second interval)
- **Reference Number:** 10-digit unique reference based on card data
- **Flow Control:** Attacker controls victim progression
- **Prominent Warnings:** Red pulsing disclaimer footer on all pages
- **Cache Busting:** Timestamp-based CSS versioning prevents caching issues during deployments
- **CDN Compatible:** Works seamlessly behind Cloudflare and other CDNs

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
- Flask-Limiter 3.5+ (rate limiting)
- Twilio Python SDK
- Docker

**Fonts:**
- Fira Code (Google Fonts) - Hacker dashboard

**Created by:** catsec.com

**Recent Updates:**
- Added timestamp-based CSS cache busting for reliable deployments
- Implemented comprehensive cache control headers (browser + Cloudflare)
- Added theme toggle with retro hacker and modern gradient options
- Switched to Fira Code font for authentic 80's terminal aesthetic
- Enhanced security with rate limiting and timing attack protection
- Fixed CSRF token handling with session-compatible cache headers

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
- לוח בקרה רטרו בסגנון שנות ה-80 עם פונט Fira Code
- החלפת ערכות נושא (האקר קלאסי / גרדיאנט מודרני)
- אימות מבוסס session עם הגבלת קצב
- אחסון נתונים בזיכרון (שום דבר לא נשמר)
- ביטול מטמון CSS אוטומטי באמצעות גרסה מבוססת timestamp
- תאימות לכותרות בקרת מטמון של Cloudflare

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
pip install flask twilio flask-wtf flask-limiter

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

- **אימות ו-Sessions:**
  - אימות מבוסס session למסלולי מנהל
  - הגנה מפני session fixation (יצירה מחדש בהתחברות)
  - השוואת סיסמאות בזמן קבוע (מניעת התקפות timing)
  - פג תוקף session (שעה אחת)
  - עוגיות HttpOnly, SameSite=Lax
  - דגל Secure אופציונלי להגדרות HTTPS proxy

- **הגנת קלט:**
  - הגנת CSRF על כל הטפסים (Flask-WTF)
  - אימות קלט מקיף (אלגוריתם Luhn לכרטיסים, E.164 לטלפונים)
  - חיטוי קלט (HTML escaping)
  - הגבלות אורך על כל הקלטים

- **הגבלת קצב:**
  - נקודת התחברות: 5 ניסיונות לדקה
  - נקודת SMS: 10 הודעות לדקה
  - הגבלות גלובליות: 200 ליום, 50 לשעה

- **כותרות אבטחה:**
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Content-Security-Policy (מגביל מקורות script/style)
  - Cache-Control: no-cache (מונע caching תוך כדי שמירת sessions)
  - CDN-Cache-Control: no-cache (ספציפי ל-Cloudflare)

- **אבטחה נוספת:**
  - ניהול מצב thread-safe עם locks
  - אין אחסון נתונים קבוע (בזיכרון בלבד)
  - תצורה מבוססת סביבה (אין סודות מוקשים)
  - SECRET_KEY קריפטוגרפי אוטומטי לכל deployment

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
| `BEHIND_HTTPS_PROXY` | מאחורי reverse proxy של HTTPS | false |
| `DEFAULT_TO_NUMBER` | נמען SMS ברירת מחדל | +9725 |

**הערות:**
- ה-SECRET_KEY של Flask נוצר אוטומטית בהפעלה באמצעות ערך אקראי מאובטח קריפטוגרפית
- גרסת CSS מוגדרת אוטומטית על בסיס timestamp של deployment לביטול מטמון
- הגדר `BEHIND_HTTPS_PROXY=true` אם מאחורי Nginx Proxy Manager או reverse proxies דומים של HTTPS

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
- **ערכת נושא האקר רטרו:** אסתטיקה של טרמינל משנות ה-80 עם פונט Fira Code monospace
- **החלפת ערכות נושא:** מעבר בין האקר קלאסי (ירוק על שחור) לערכות נושא גרדיאנט מודרניות
- **עדכונים בזמן אמת:** לוח בקרה מתרענן אוטומטית (מרווח של 2 שניות)
- **מספר אסמכתא:** אסמכתא ייחודית בת 10 ספרות מבוססת נתוני כרטיס
- **בקרת זרימה:** התוקף שולט בהתקדמות הקורבן
- **אזהרות בולטות:** כותרת אזהרה אדומה פועמת בכל הדפים
- **ביטול מטמון:** גרסה מבוססת timestamp של CSS מונעת בעיות caching במהלך deployments
- **תאימות CDN:** עובד בצורה חלקה מאחורי Cloudflare ו-CDNs אחרים

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
- Flask-Limiter 3.5+ (הגבלת קצב)
- Twilio Python SDK
- Docker

**פונטים:**
- Fira Code (Google Fonts) - לוח בקרה האקר

**נוצר על ידי:** catsec.com

**עדכונים אחרונים:**
- נוסף ביטול מטמון CSS מבוסס timestamp עבור deployments אמינים
- יושמו כותרות בקרת מטמון מקיפות (דפדפן + Cloudflare)
- נוספה החלפת ערכות נושא עם אפשרויות האקר רטרו וגרדיאנט מודרני
- מעבר לפונט Fira Code עבור אסתטיקה אותנטית של טרמינל משנות ה-80
- שיפור אבטחה עם הגבלת קצב והגנה מפני התקפות timing
- תוקן טיפול ב-token CSRF עם כותרות מטמון תואמות session

---

## Support | תמיכה

For issues, questions, or contributions, please contact catsec.com

לבעיות, שאלות או תרומות, אנא צור קשר עם catsec.com
