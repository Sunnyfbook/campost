#!/usr/bin/env python3
"""
Debug script for CamGrabber Admin API
This script will help identify why the admin API endpoints are not working
"""

import requests
import json
import sys

def test_endpoint(url, method="GET", data=None, headers=None):
    """Test an endpoint and return the response"""
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
        
        print(f"📡 {method} {url}")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"   Response: {json.dumps(response_json, indent=2)}")
        except:
            print(f"   Response: {response.text[:200]}...")
        
        print()
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing {method} {url}: {e}")
        print()
        return None

def main():
    """Main debug function"""
    base_url = "https://camgrabber.onrender.com"
    
    print("🔍 CamGrabber Admin API Debug Tool")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print("=" * 50)
    print()
    
    # Test basic connectivity
    print("1️⃣ Testing basic connectivity...")
    test_endpoint(f"{base_url}/")
    
    # Test simple API endpoint
    print("2️⃣ Testing simple API endpoint...")
    test_endpoint(f"{base_url}/api/test")
    
    # Test simple admin test endpoint
    print("3️⃣ Testing simple admin test endpoint...")
    test_endpoint(f"{base_url}/api/admin/simple-test")
    
    # Test simple admin stats endpoint
    print("4️⃣ Testing simple admin stats endpoint...")
    test_endpoint(f"{base_url}/api/admin/simple-stats")
    
    # Test simple admin login endpoint with POST
    print("5️⃣ Testing simple admin login with POST...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    headers = {
        "Content-Type": "application/json"
    }
    test_endpoint(f"{base_url}/api/admin/simple-login", method="POST", data=login_data, headers=headers)
    
    # Test admin simple test endpoint (from full admin API)
    print("6️⃣ Testing admin simple test endpoint (full API)...")
    test_endpoint(f"{base_url}/api/admin/simple-test")
    
    # Test admin test endpoint
    print("7️⃣ Testing admin test endpoint...")
    test_endpoint(f"{base_url}/api/admin/test")
    
    # Test admin login endpoint with GET (should fail)
    print("8️⃣ Testing admin login with GET (should fail)...")
    test_endpoint(f"{base_url}/api/admin/login")
    
    # Test admin login endpoint with POST
    print("9️⃣ Testing admin login with POST...")
    test_endpoint(f"{base_url}/api/admin/login", method="POST", data=login_data, headers=headers)
    
    # Test admin panel access
    print("7️⃣ Testing admin panel access...")
    test_endpoint(f"{base_url}/admin")
    
    print("=" * 50)
    print("🔍 Debug Summary:")
    print("If you see 405 errors, it means the routes are not registered properly.")
    print("If you see 404 errors, it means the routes don't exist.")
    print("If you see 500 errors, it means there's a server error.")
    print("=" * 50)

if __name__ == "__main__":
    main() 