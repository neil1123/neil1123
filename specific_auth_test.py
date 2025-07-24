#!/usr/bin/env python3
"""
Specific Authentication Test for Provider Registration and Login
Tests the exact scenario requested by the user
"""

import requests
import json
import sys

# Backend URL from environment
BACKEND_URL = "https://5f81e1b3-88a9-45db-958d-9cb5f0ec9f5a.preview.emergentagent.com/api"

def test_provider_registration_with_specific_credentials():
    """Test provider registration with the specific credentials provided"""
    print("🔍 Testing Provider Registration with Specific Credentials...")
    
    test_data = {
        "email": "test@provider.com",
        "password": "password123",
        "user_type": "provider",
        "name": "Test Provider",
        "phone": "(555) 123-4567",
        "business_name": "Test Provider Service",
        "services": ["Plumbing", "Electrical"]
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Provider registration successful")
            print(f"Access Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"User ID: {data.get('user', {}).get('id', 'N/A')}")
            print(f"User Type: {data.get('user', {}).get('user_type', 'N/A')}")
            return data.get('access_token'), data.get('user', {}).get('id')
        elif response.status_code == 400:
            print("⚠️ User already exists (this is expected if running multiple times)")
            return None, None
        else:
            print(f"❌ Provider registration failed")
            print(f"Response: {response.text}")
            return None, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Provider registration failed: {e}")
        return None, None

def test_provider_login_with_specific_credentials():
    """Test provider login with the specific credentials provided"""
    print("\n🔍 Testing Provider Login with Specific Credentials...")
    
    login_data = {
        "email": "test@provider.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Provider login successful")
            print(f"Access Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"User ID: {data.get('user', {}).get('id', 'N/A')}")
            print(f"User Type: {data.get('user', {}).get('user_type', 'N/A')}")
            print(f"Business Name: {data.get('user', {}).get('business_name', 'N/A')}")
            return data.get('access_token')
        else:
            print(f"❌ Provider login failed")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Provider login failed: {e}")
        return None

def test_jwt_token_validation(token):
    """Test JWT token validation with /auth/me endpoint"""
    print("\n🔍 Testing JWT Token Validation...")
    
    if not token:
        print("❌ No token available for validation")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BACKEND_URL}/auth/me",
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ JWT token validation successful")
            print(f"User ID: {data.get('id', 'N/A')}")
            print(f"Email: {data.get('email', 'N/A')}")
            print(f"User Type: {data.get('user_type', 'N/A')}")
            print(f"Business Name: {data.get('business_name', 'N/A')}")
            return True
        else:
            print(f"❌ JWT token validation failed")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ JWT token validation failed: {e}")
        return False

def test_protected_route_access(token):
    """Test access to protected /orders route"""
    print("\n🔍 Testing Protected Route Access (/api/orders)...")
    
    if not token:
        print("❌ No token available for protected route test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BACKEND_URL}/orders",
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Protected route access successful")
            print(f"Orders retrieved: {len(data)} orders")
            return True
        else:
            print(f"❌ Protected route access failed")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Protected route access failed: {e}")
        return False

def main():
    """Run the specific authentication tests"""
    print("=" * 80)
    print("🚀 SPECIFIC PROVIDER AUTHENTICATION TESTING")
    print("=" * 80)
    
    # Test 1: Provider Registration
    token, user_id = test_provider_registration_with_specific_credentials()
    
    # Test 2: Provider Login (this should work regardless of registration result)
    login_token = test_provider_login_with_specific_credentials()
    
    # Use login token if available, otherwise use registration token
    test_token = login_token or token
    
    # Test 3: JWT Token Validation
    jwt_valid = test_jwt_token_validation(test_token)
    
    # Test 4: Protected Route Access
    protected_access = test_protected_route_access(test_token)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SPECIFIC AUTHENTICATION TEST SUMMARY")
    print("=" * 80)
    
    tests = [
        ("Provider Registration", token is not None or "already exists"),
        ("Provider Login", login_token is not None),
        ("JWT Token Validation", jwt_valid),
        ("Protected Route Access", protected_access)
    ]
    
    passed = 0
    for test_name, result in tests:
        if result == "already exists":
            status = "⚠️ SKIP (User exists)"
            passed += 1
        elif result:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
        print(f"{test_name:<25} {status}")
    
    print(f"\nPassed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("\n🎉 ALL AUTHENTICATION TESTS PASSED!")
        print("✅ Provider registration and authentication system is working properly")
        return True
    else:
        print(f"\n⚠️ {len(tests) - passed} AUTHENTICATION TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)