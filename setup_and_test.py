#!/usr/bin/env python3
"""
Setup test users and run focused backend tests
"""

import requests
import json
import uuid
import sys

# Backend URL from environment
BACKEND_URL = "https://5f81e1b3-88a9-45db-958d-9cb5f0ec9f5a.preview.emergentagent.com/api"

def setup_test_users():
    """Create test users for testing"""
    print("🔧 Setting up test users...")
    
    try:
        # Create homeowner test user
        homeowner_data = {
            "email": "test@homeowner.com",
            "password": "password123",
            "user_type": "homeowner",
            "name": "Test Homeowner",
            "phone": "+1-902-555-0123",
            "address": "123 Test St, Halifax, NS"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json=homeowner_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Homeowner test user created")
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️ Homeowner test user already exists")
        else:
            print(f"❌ Failed to create homeowner: {response.status_code}")
            print(f"Response: {response.text}")
        
        # Create provider test user
        provider_data = {
            "email": "test@provider.com",
            "password": "password123",
            "user_type": "provider",
            "name": "Test Provider",
            "phone": "+1-902-555-0456",
            "address": "456 Provider St, Halifax, NS",
            "business_name": "Test Home Services",
            "services": ["Plumbing", "Electrical", "General Repair"],
            "license": "NS-TEST-123"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json=provider_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Provider test user created")
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️ Provider test user already exists")
        else:
            print(f"❌ Failed to create provider: {response.status_code}")
            print(f"Response: {response.text}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to setup test users: {e}")
        return False

if __name__ == "__main__":
    setup_test_users()
    
    # Now run the focused tests
    print("\n" + "="*50)
    print("Running focused backend tests...")
    print("="*50)
    
    import subprocess
    result = subprocess.run([sys.executable, "focused_backend_test.py"], cwd="/app")
    sys.exit(result.returncode)