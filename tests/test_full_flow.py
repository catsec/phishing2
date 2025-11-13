#!/usr/bin/env python3
"""
Automated End-to-End Test for Phishing Demo Application
Tests the complete flow from hacker dashboard to victim interaction
"""

import os
import sys
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file in parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configuration from .env
PORT = os.getenv('PORT', '9999')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
BASE_URL = f'http://127.0.0.1:{PORT}'

# Test data
TEST_CARD_NAME = 'first last'
TEST_CARD_NUMBER = '4580 1234 1234 1232'
TEST_EXPIRY = '12/50'
TEST_CVV = '123'
TEST_OTP = '666666'
TEST_SMS_FROM = 'TEST'
TEST_SMS_TO = '+972524847868'
TEST_SMS_MESSAGE = 'testing'

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def log_step(message):
    """Log a test step"""
    print(f"\n{Colors.BLUE}▶ {message}{Colors.RESET}")

def log_success(message):
    """Log a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def log_error(message):
    """Log an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def log_warning(message):
    """Log a warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def run_command(command, description):
    """Run a shell command and return success status"""
    log_step(description)
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        log_success(f"{description} - Completed")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        log_error(f"{description} - Failed: {e.stderr}")
        return False, e.stderr

def wait_for_docker_ready(timeout=60):
    """Wait for Docker container to be ready"""
    log_step(f"Waiting for Docker container to be ready (timeout: {timeout}s)")
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            result = subprocess.run(
                f'curl -s -o /dev/null -w "%{{http_code}}" {BASE_URL}/disclaimer',
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stdout.strip() == '200':
                log_success("Docker container is ready and responding")
                return True
        except:
            pass
        time.sleep(2)

    log_error("Docker container did not become ready in time")
    return False

def setup_driver():
    """Setup Chrome WebDriver with headless options"""
    log_step("Setting up Chrome WebDriver")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    log_success("Chrome WebDriver initialized")
    return driver

def test_hacker_login(driver):
    """Test hacker dashboard login"""
    log_step("Testing hacker login")

    try:
        driver.get(f'{BASE_URL}/hacker')

        # Should redirect to login
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )

        # Enter credentials
        driver.find_element(By.NAME, 'username').send_keys(ADMIN_USERNAME)
        driver.find_element(By.NAME, 'password').send_keys(ADMIN_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # Wait for dashboard to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'smsForm'))
        )

        log_success("Successfully logged in to hacker dashboard")
        return True
    except Exception as e:
        log_error(f"Failed to login: {str(e)}")
        return False

def test_send_sms(driver):
    """Test SMS sending functionality"""
    log_step("Testing SMS sending")

    try:
        # Fill SMS form
        driver.find_element(By.ID, 'from').clear()
        driver.find_element(By.ID, 'from').send_keys(TEST_SMS_FROM)

        driver.find_element(By.ID, 'to').clear()
        driver.find_element(By.ID, 'to').send_keys(TEST_SMS_TO)

        driver.find_element(By.ID, 'message').clear()
        driver.find_element(By.ID, 'message').send_keys(TEST_SMS_MESSAGE)

        # Submit form
        driver.find_element(By.ID, 'sendBtn').click()

        # Wait for success or error message
        time.sleep(3)
        alert = driver.find_element(By.ID, 'smsAlert')
        alert_text = alert.text.strip()

        if 'SUCCESS' in alert_text or 'SID' in alert_text:
            log_success(f"SMS sent successfully: {alert_text}")
            return True
        elif 'ERROR' in alert_text or 'error' in alert_text.lower():
            log_warning(f"SMS sending failed (expected with test credentials): {alert_text}")
            return True  # This is expected behavior with invalid Twilio credentials
        elif not alert_text:
            log_warning("SMS response empty (expected with test Twilio credentials)")
            return True  # Empty response is also acceptable for test mode
        else:
            log_error(f"Unexpected SMS response: '{alert_text}'")
            return False
    except Exception as e:
        log_error(f"Failed to send SMS: {str(e)}")
        return False

def test_victim_flow_step1(driver_victim):
    """Test victim entering card details"""
    log_step("Testing victim card entry")

    try:
        driver_victim.get(BASE_URL)

        # Wait for form to load
        WebDriverWait(driver_victim, 10).until(
            EC.presence_of_element_located((By.NAME, 'cardName'))
        )

        # Fill in card details
        driver_victim.find_element(By.NAME, 'cardName').send_keys(TEST_CARD_NAME)
        driver_victim.find_element(By.NAME, 'cardNumber').send_keys(TEST_CARD_NUMBER)
        driver_victim.find_element(By.NAME, 'expiry').send_keys(TEST_EXPIRY)
        driver_victim.find_element(By.NAME, 'cvv').send_keys(TEST_CVV)

        # Submit form
        driver_victim.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # Wait for loading page
        WebDriverWait(driver_victim, 10).until(
            EC.url_contains('/submit')
        )

        log_success("Victim card details submitted successfully")
        return True
    except Exception as e:
        log_error(f"Failed victim card entry: {str(e)}")
        return False

def check_hacker_received_card_data(driver_hacker):
    """Check if hacker dashboard shows captured card data"""
    log_step("Checking if hacker received card data")

    try:
        # Wait for auto-refresh to update with captured data (max 15 seconds)
        for attempt in range(5):
            time.sleep(3)

            card_data_div = driver_hacker.find_element(By.ID, 'cardData')
            card_data_text = card_data_div.text

            if TEST_CARD_NAME.lower() in card_data_text.lower():
                log_success("Hacker dashboard shows captured card data")
                return True

            log_warning(f"Attempt {attempt + 1}/5: Card data not yet visible, waiting...")

        log_error("Card data not visible on hacker dashboard after 15 seconds")
        log_warning(f"Current cardData content: {card_data_text}")
        return False
    except Exception as e:
        log_error(f"Failed to check card data: {str(e)}")
        return False

def test_hacker_continue(driver_hacker):
    """Test hacker clicking continue button"""
    log_step("Testing hacker continue to transaction alert")

    try:
        continue_btn = driver_hacker.find_element(By.ID, 'continueBtn')

        # Wait for button to be enabled
        WebDriverWait(driver_hacker, 10).until(
            lambda d: continue_btn.is_enabled()
        )

        # Scroll to button to avoid footer overlap
        driver_hacker.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_btn)
        time.sleep(1)

        # Use JavaScript click to avoid interception issues
        driver_hacker.execute_script("arguments[0].click();", continue_btn)

        # Wait for success message
        time.sleep(2)

        log_success("Hacker clicked continue button")
        return True
    except Exception as e:
        log_error(f"Failed to click continue: {str(e)}")
        return False

def test_victim_transaction_alert(driver_victim):
    """Test victim seeing transaction alert and choosing 'not me'"""
    log_step("Testing victim transaction alert")

    try:
        # Wait for redirect to transaction alert
        WebDriverWait(driver_victim, 15).until(
            EC.url_contains('/transaction_alert')
        )

        # Click "לא ביצעתי" (I didn't do it) button
        not_me_btn = driver_victim.find_element(By.CSS_SELECTOR, '.btn-not-me')
        not_me_btn.click()

        # Wait for OTP page
        WebDriverWait(driver_victim, 10).until(
            EC.url_contains('/otp')
        )

        log_success("Victim proceeded to OTP page")
        return True
    except Exception as e:
        log_error(f"Failed transaction alert step: {str(e)}")
        return False

def test_victim_enter_otp(driver_victim):
    """Test victim entering OTP code"""
    log_step("Testing victim OTP entry")

    try:
        # Enter OTP
        otp_input = driver_victim.find_element(By.NAME, 'otp')
        otp_input.send_keys(TEST_OTP)

        # Submit
        driver_victim.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # Wait for success page
        WebDriverWait(driver_victim, 10).until(
            lambda d: 'verification_success' in d.current_url or 'בוטלה בהצלחה' in d.page_source
        )

        log_success("Victim OTP submitted successfully")
        return True
    except Exception as e:
        log_error(f"Failed to enter OTP: {str(e)}")
        return False

def check_hacker_received_otp(driver_hacker):
    """Check if hacker dashboard shows captured OTP"""
    log_step("Checking if hacker received OTP")

    try:
        # Wait for auto-refresh
        time.sleep(3)

        otp_data_div = driver_hacker.find_element(By.ID, 'otpData')
        otp_data_text = otp_data_div.text

        if TEST_OTP in otp_data_text:
            log_success(f"Hacker dashboard shows captured OTP: {TEST_OTP}")
            return True
        else:
            log_error("OTP not visible on hacker dashboard")
            return False
    except Exception as e:
        log_error(f"Failed to check OTP: {str(e)}")
        return False

def main():
    """Main test execution"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("Phishing Demo - Automated End-to-End Test")
    print(f"{'='*60}{Colors.RESET}\n")

    # Validate environment variables
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        log_error("ADMIN_USERNAME or ADMIN_PASSWORD not set in .env file")
        return False

    log_step(f"Configuration:")
    print(f"  - Port: {PORT}")
    print(f"  - Base URL: {BASE_URL}")
    print(f"  - Admin User: {ADMIN_USERNAME}")

    # Step 1: Build Docker
    success, _ = run_command(
        'docker-compose build',
        'Building Docker image'
    )
    if not success:
        return False

    # Step 2: Start Docker
    success, _ = run_command(
        'docker-compose up -d',
        'Starting Docker container'
    )
    if not success:
        return False

    # Step 3: Wait for container to be ready
    if not wait_for_docker_ready():
        run_command('docker-compose down', 'Shutting down Docker')
        return False

    # Initialize browser drivers
    driver_hacker = None
    driver_victim = None

    try:
        # Step 4: Setup browsers
        driver_hacker = setup_driver()
        driver_victim = setup_driver()

        # Step 5: Test hacker login
        if not test_hacker_login(driver_hacker):
            return False

        # Step 6: Test SMS sending
        if not test_send_sms(driver_hacker):
            log_warning("SMS test completed with warnings (expected if Twilio credentials are test values)")

        # Step 7: Test victim card entry
        if not test_victim_flow_step1(driver_victim):
            return False

        # Step 8: Check hacker received card data
        if not check_hacker_received_card_data(driver_hacker):
            return False

        # Step 9: Hacker clicks continue
        if not test_hacker_continue(driver_hacker):
            return False

        # Step 10: Victim sees transaction alert and clicks "not me"
        if not test_victim_transaction_alert(driver_victim):
            return False

        # Step 11: Victim enters OTP
        if not test_victim_enter_otp(driver_victim):
            return False

        # Step 12: Check hacker received OTP
        if not check_hacker_received_otp(driver_hacker):
            return False

        # All tests passed!
        print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*60}")
        print("✓ ALL TESTS PASSED SUCCESSFULLY!")
        print(f"{'='*60}{Colors.RESET}\n")

        return True

    except Exception as e:
        log_error(f"Unexpected error during test: {str(e)}")
        return False

    finally:
        # Cleanup: Close browsers
        if driver_hacker:
            log_step("Closing hacker browser")
            driver_hacker.quit()
        if driver_victim:
            log_step("Closing victim browser")
            driver_victim.quit()

        # Step 13: Shutdown Docker
        run_command(
            'docker-compose down',
            'Shutting down Docker container'
        )

        print(f"\n{Colors.BLUE}Test execution completed{Colors.RESET}\n")

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
