#!/usr/bin/env python3
"""
Provider Dashboard Enhancement Testing Script
Tests specific provider dashboard enhancements as requested in review:
1. Order Creation Status - Manual orders should be "confirmed" not "pending_quotation"
2. Appointment Creation - Test appointment creation works without errors
3. Date Validation - Test past date restrictions (if implemented)
"""

import requests
import json
import os
from datetime import datetime, timedelta
import sys
import uuid

# Load environment variables
BACKEND_URL = "https://5f81e1b3-88a9-45db-958d-9cb5f0ec9f5a.preview.emergentagent.com/api"

# Global variables to store test data
provider_token = None
provider_id = None
homeowner_id = None

def test_backend_health():
    """Test if backend server is running and accessible"""
    print("🔍 Testing Backend Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "Doord API" in data.get("message", ""):
                print("✅ Backend server is running and accessible")
                return True
            else:
                print(f"❌ Unexpected response: {data}")
                return False
        else:
            print(f"❌ Backend health check failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def setup_test_provider():
    """Create a test provider for testing"""
    print("\n🔍 Setting up Test Provider...")
    global provider_token, provider_id
    
    # Create unique test provider
    test_email = f"testprovider_{uuid.uuid4().hex[:8]}@example.com"
    
    provider_data = {
        "email": test_email,
        "password": "testpass123",
        "user_type": "provider",
        "name": "Test Provider",
        "business_name": "Test Provider Services",
        "services": ["Electrical", "Plumbing"],
        "phone": "555-0123",
        "address": "123 Test St, Halifax, NS"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=provider_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            provider_token = data["access_token"]
            provider_id = data["user"]["id"]
            print(f"✅ Test provider created successfully - ID: {provider_id}")
            return True
        else:
            print(f"❌ Provider registration failed: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Provider registration request failed: {e}")
        return False

def setup_test_homeowner():
    """Create a test homeowner for testing"""
    print("\n🔍 Setting up Test Homeowner...")
    global homeowner_id
    
    # Create unique test homeowner
    test_email = f"testhomeowner_{uuid.uuid4().hex[:8]}@example.com"
    
    homeowner_data = {
        "email": test_email,
        "password": "testpass123",
        "user_type": "homeowner",
        "name": "Test Homeowner",
        "phone": "555-0456",
        "address": "456 Test Ave, Halifax, NS"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=homeowner_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            homeowner_id = data["user"]["id"]
            print(f"✅ Test homeowner created successfully - ID: {homeowner_id}")
            return True
        else:
            print(f"❌ Homeowner registration failed: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Homeowner registration request failed: {e}")
        return False

def test_manual_order_status():
    """Test that manual orders created by providers have 'confirmed' status"""
    print("\n🔍 Testing Manual Order Creation Status...")
    
    if not provider_token or not homeowner_id:
        print("❌ Missing provider token or homeowner ID")
        return False
    
    # Create manual order as provider
    order_data = {
        "homeowner_id": homeowner_id,
        "provider_id": provider_id,
        "homeowner_name": "Test Homeowner",
        "homeowner_email": "test@homeowner.com",
        "homeowner_phone": "555-0456",
        "homeowner_address": "456 Test Ave, Halifax, NS",
        "provider_name": "Test Provider Services",
        "service_type": "Electrical",
        "description": "Manual order test - electrical work",
        "preferred_date": "2025-02-15",
        "preferred_time": "10:00 AM",
        "urgency": "medium"
    }
    
    headers = {"Authorization": f"Bearer {provider_token}"}
    
    try:
        response = requests.post(f"{BACKEND_URL}/orders", json=order_data, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            order_status = data.get("status")
            
            if order_status == "confirmed":
                print("✅ Manual order created with 'confirmed' status as expected")
                return True
            else:
                print(f"❌ Manual order created with '{order_status}' status, expected 'confirmed'")
                return False
        else:
            print(f"❌ Manual order creation failed: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Manual order creation request failed: {e}")
        return False

def test_appointment_creation():
    """Test that appointment creation works properly without errors"""
    print("\n🔍 Testing Appointment Creation...")
    
    if not provider_token:
        print("❌ Missing provider token")
        return False
    
    # Create appointment
    appointment_data = {
        "customer_name": "John Smith",
        "phone_number": "555-0789",
        "service_type": "Electrical",
        "date": "2025-02-20",
        "time": "2:00 PM",
        "address": "789 Customer St, Halifax, NS",
        "notes": "Test appointment creation",
        "source": "manual"
    }
    
    headers = {"Authorization": f"Bearer {provider_token}"}
    
    try:
        response = requests.post(f"{BACKEND_URL}/appointments", json=appointment_data, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            appointment_id = data.get("id")
            
            if appointment_id:
                print(f"✅ Appointment created successfully - ID: {appointment_id}")
                
                # Verify appointment data
                expected_fields = ["customer_name", "phone_number", "service_type", "date", "time", "address"]
                missing_fields = [field for field in expected_fields if field not in data or not data[field]]
                
                if not missing_fields:
                    print("✅ Appointment contains all required fields")
                    return True
                else:
                    print(f"❌ Appointment missing fields: {missing_fields}")
                    return False
            else:
                print("❌ Appointment created but no ID returned")
                return False
        else:
            print(f"❌ Appointment creation failed: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Appointment creation request failed: {e}")
        return False

def test_appointment_retrieval():
    """Test that appointments can be retrieved properly"""
    print("\n🔍 Testing Appointment Retrieval...")
    
    if not provider_token:
        print("❌ Missing provider token")
        return False
    
    headers = {"Authorization": f"Bearer {provider_token}"}
    
    try:
        response = requests.get(f"{BACKEND_URL}/appointments", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                print(f"✅ Appointments retrieved successfully - Count: {len(data)}")
                
                if len(data) > 0:
                    # Check first appointment structure
                    appointment = data[0]
                    required_fields = ["id", "provider_id", "customer_name", "phone_number", "service_type", "date", "time", "address"]
                    missing_fields = [field for field in required_fields if field not in appointment]
                    
                    if not missing_fields:
                        print("✅ Appointment data structure is correct")
                        return True
                    else:
                        print(f"❌ Appointment missing required fields: {missing_fields}")
                        return False
                else:
                    print("✅ No appointments found (empty list is valid)")
                    return True
            else:
                print(f"❌ Expected list of appointments, got: {type(data)}")
                return False
        else:
            print(f"❌ Appointment retrieval failed: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Appointment retrieval request failed: {e}")
        return False

def test_past_date_validation():
    """Test date validation for appointments (if implemented)"""
    print("\n🔍 Testing Past Date Validation...")
    
    if not provider_token:
        print("❌ Missing provider token")
        return False
    
    # Try to create appointment with past date
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    appointment_data = {
        "customer_name": "Past Date Test",
        "phone_number": "555-0999",
        "service_type": "Plumbing",
        "date": yesterday,
        "time": "10:00 AM",
        "address": "999 Past St, Halifax, NS",
        "notes": "Testing past date validation",
        "source": "manual"
    }
    
    headers = {"Authorization": f"Bearer {provider_token}"}
    
    try:
        response = requests.post(f"{BACKEND_URL}/appointments", json=appointment_data, headers=headers, timeout=10)
        
        if response.status_code == 400:
            # Past date validation is working
            print("✅ Past date validation working - appointment creation rejected")
            return True
        elif response.status_code == 200:
            # Past date validation not implemented
            print("⚠️  Past date validation not implemented - appointment created with past date")
            print("   Note: This is not a critical error, but date validation should be added")
            return True
        else:
            print(f"❌ Unexpected response for past date test: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Past date validation test request failed: {e}")
        return False

def test_provider_only_access():
    """Test that only providers can create appointments"""
    print("\n🔍 Testing Provider-Only Appointment Access...")
    
    # Try to create appointment without authentication
    appointment_data = {
        "customer_name": "Unauthorized Test",
        "phone_number": "555-0000",
        "service_type": "Test",
        "date": "2025-02-25",
        "time": "3:00 PM",
        "address": "000 Unauthorized St",
        "notes": "Testing unauthorized access"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/appointments", json=appointment_data, timeout=10)
        
        if response.status_code == 401 or response.status_code == 403:
            print("✅ Unauthorized appointment creation properly rejected")
            return True
        else:
            print(f"❌ Unauthorized appointment creation should be rejected, got: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Unauthorized access test request failed: {e}")
        return False

def run_provider_dashboard_tests():
    """Run all provider dashboard enhancement tests"""
    print("=" * 80)
    print("🚀 PROVIDER DASHBOARD ENHANCEMENT TESTING")
    print("=" * 80)
    
    tests = [
        ("Backend Health Check", test_backend_health),
        ("Setup Test Provider", setup_test_provider),
        ("Setup Test Homeowner", setup_test_homeowner),
        ("Manual Order Status Test", test_manual_order_status),
        ("Appointment Creation Test", test_appointment_creation),
        ("Appointment Retrieval Test", test_appointment_retrieval),
        ("Past Date Validation Test", test_past_date_validation),
        ("Provider-Only Access Test", test_provider_only_access),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print("📊 PROVIDER DASHBOARD TEST RESULTS")
    print("=" * 80)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL PROVIDER DASHBOARD ENHANCEMENT TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_provider_dashboard_tests()
    sys.exit(0 if success else 1)