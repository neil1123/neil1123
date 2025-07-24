#!/usr/bin/env python3
"""
Setup test users for quotation and messaging workflow testing
"""

import requests
import json
import uuid

BACKEND_URL = "https://5f81e1b3-88a9-45db-958d-9cb5f0ec9f5a.preview.emergentagent.com/api"

def create_test_homeowner():
    """Create test homeowner account"""
    print("🔍 Creating test homeowner account...")
    
    try:
        test_data = {
            "email": "test@homeowner.com",
            "password": "password123",
            "user_type": "homeowner",
            "name": "Test Homeowner",
            "phone": "+1-902-555-1234",
            "address": "123 Test St, Halifax, NS"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Test homeowner created successfully")
            return data["user"]["id"], data["access_token"]
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️ Test homeowner already exists, trying login...")
            # Try to login
            login_data = {
                "email": "test@homeowner.com",
                "password": "password123"
            }
            
            login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                print("✅ Test homeowner login successful")
                return login_data["user"]["id"], login_data["access_token"]
            else:
                print(f"❌ Test homeowner login failed: {login_response.text}")
                return None, None
        else:
            print(f"❌ Test homeowner creation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"❌ Test homeowner creation failed: {e}")
        return None, None

def create_test_provider():
    """Create test provider account"""
    print("\n🔍 Creating test provider account...")
    
    try:
        test_data = {
            "email": "test@provider.com",
            "password": "password123",
            "user_type": "provider",
            "name": "Test Provider",
            "phone": "+1-902-555-5678",
            "address": "456 Provider Ave, Halifax, NS",
            "business_name": "Test Home Services",
            "services": ["Plumbing", "Electrical", "HVAC"],
            "license": "NS-TEST-123"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Test provider created successfully")
            return data["user"]["id"], data["access_token"]
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️ Test provider already exists, trying login...")
            # Try to login
            login_data = {
                "email": "test@provider.com",
                "password": "password123"
            }
            
            login_response = requests.post(
                f"{BACKEND_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                print("✅ Test provider login successful")
                return login_data["user"]["id"], login_data["access_token"]
            else:
                print(f"❌ Test provider login failed: {login_response.text}")
                return None, None
        else:
            print(f"❌ Test provider creation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"❌ Test provider creation failed: {e}")
        return None, None

def main():
    print("=" * 60)
    print("🚀 SETTING UP TEST USERS")
    print("=" * 60)
    
    homeowner_id, homeowner_token = create_test_homeowner()
    provider_id, provider_token = create_test_provider()
    
    if homeowner_id and provider_id:
        print("\n✅ Test users setup complete!")
        print(f"Homeowner ID: {homeowner_id}")
        print(f"Provider ID: {provider_id}")
        print("\nYou can now run the quotation and messaging workflow tests.")
        return True
    else:
        print("\n❌ Test users setup failed!")
        return False

if __name__ == "__main__":
    main()