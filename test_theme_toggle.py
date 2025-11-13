#!/usr/bin/env python3
"""
Test script to verify the theme toggle functionality on the hacker dashboard.
"""

import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "http://localhost:9999"

def test_theme_toggle():
    """Test that the theme toggle button and JavaScript are present."""

    session = requests.Session()

    # Step 1: Get login page to extract CSRF token
    print("1. Getting login page...")
    login_page = session.get(f"{BASE_URL}/login")
    soup = BeautifulSoup(login_page.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    print(f"   ✓ Got CSRF token: {csrf_token[:20]}...")

    # Step 2: Login
    print("2. Logging in...")
    login_data = {
        'username': 'admin',
        'password': 'password',
        'csrf_token': csrf_token
    }
    login_response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)

    # Check if redirected to hacker page
    if login_response.status_code in [302, 303, 307]:
        print(f"   ✓ Login successful, redirecting to: {login_response.headers.get('Location')}")
        # Follow redirect to get hacker page
        hacker_page = session.get(f"{BASE_URL}/hacker")
        if hacker_page.status_code == 200:
            print("   ✓ Successfully accessed hacker dashboard")
            login_response = hacker_page
        else:
            print(f"   ✗ Failed to access hacker dashboard (status: {hacker_page.status_code})")
            return False
    elif 'PHISHING CONTROL PANEL' in login_response.text:
        print("   ✓ Successfully logged in (direct)")
    else:
        print(f"   ✗ Login failed (status: {login_response.status_code})")
        # Check for error message
        soup_check = BeautifulSoup(login_response.text, 'html.parser')
        error_div = soup_check.find('div', {'class': 'error'})
        if error_div:
            print(f"   Error message: {error_div.get_text(strip=True)}")
        print(f"   Response snippet: {login_response.text[:200]}...")
        return False

    # Step 3: Check for theme toggle button
    print("3. Checking for theme toggle button...")
    soup = BeautifulSoup(login_response.text, 'html.parser')
    theme_button = soup.find('button', {'id': 'themeToggleBtn'})

    if theme_button:
        button_text = theme_button.get_text(strip=True)
        print(f"   ✓ Theme toggle button found with text: '{button_text}'")
        if button_text == 'מה זו הקלישאה הזו?':
            print("   ✓ Button has correct initial Hebrew text")
        else:
            print(f"   ✗ Button text is incorrect: '{button_text}'")
            return False
    else:
        print("   ✗ Theme toggle button NOT found")
        return False

    # Step 4: Check for theme toggle JavaScript
    print("4. Checking for theme toggle JavaScript...")
    page_text = login_response.text

    checks = [
        ('themeToggleBtn', 'Button element reference'),
        ('modern-theme', 'Modern theme class'),
        ('localStorage.getItem', 'LocalStorage get'),
        ('localStorage.setItem', 'LocalStorage set'),
        ('חזרה לשנות השמונים', 'Hebrew toggle text (back to 80s)'),
        ('addEventListener', 'Event listener')
    ]

    all_checks_passed = True
    for check_string, description in checks:
        if check_string in page_text:
            print(f"   ✓ Found: {description}")
        else:
            print(f"   ✗ Missing: {description}")
            all_checks_passed = False

    # Step 5: Check CSS for modern theme styles
    print("5. Checking CSS for modern theme styles...")
    css_response = session.get(f"{BASE_URL}/static/css/main.css")
    css_text = css_response.text

    css_checks = [
        ('body.hacker-page.modern-theme', 'Modern theme body style'),
        ('.theme-toggle-btn', 'Theme toggle button style'),
        ('left: 50%', 'Button centering'),
        ('transform: translateX(-50%)', 'Button transform for centering')
    ]

    css_checks_passed = True
    for check_string, description in css_checks:
        if check_string in css_text:
            print(f"   ✓ Found: {description}")
        else:
            print(f"   ✗ Missing: {description}")
            css_checks_passed = False

    # Final result
    print("\n" + "="*60)
    if all_checks_passed and css_checks_passed:
        print("✓ ALL TESTS PASSED - Theme toggle is properly implemented!")
        return True
    else:
        print("✗ SOME TESTS FAILED - Please review the issues above")
        return False

if __name__ == "__main__":
    try:
        success = test_theme_toggle()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
