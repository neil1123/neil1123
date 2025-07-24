#!/usr/bin/env python3
"""
Provider Profile Management Backend Testing Script
Tests the newly implemented provider profile management functionality
"""

import requests
import json
import os
from datetime import datetime
import sys
import uuid

# Load environment variables
BACKEND_URL = "https://5f81e1b3-88a9-45db-958d-9cb5f0ec9f5a.preview.emergentagent.com/api"

# Global variables to store test data
provider_token = None
homeowner_token = None
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

def test_provider_registration_and_login():
    """Test provider registration and login for testing"""
    print("\n🔍 Testing Provider Registration and Login...")
    global provider_token, provider_id
    
    try:
        # Register a new provider for testing
        test_email = f"profiletest_{uuid.uuid4().hex[:8]}@doordtest.com"
        register_data = {
            "email": test_email,
            "password": "profiletest123",
            "user_type": "provider",
            "name": "Profile Test Provider",
            "phone": "+1-902-555-9999",
            "address": "123 Profile Test St, Halifax, NS",
            "business_name": "Profile Test Services",
            "services": ["Plumbing", "Electrical", "HVAC"],
            "license": "NS-PROFILE-123"
        }
        
        # Register
        register_response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if register_response.status_code == 200:
            data = register_response.json()
            if "access_token" in data and "user" in data:
                provider_token = data["access_token"]
                provider_id = data["user"]["id"]
                print("✅ Provider registration and login successful")
                print(f"   Provider ID: {provider_id}")
                print(f"   Provider Email: {test_email}")
                return True
            else:
                print(f"❌ Invalid registration response structure: {data}")
                return False
        else:
            print(f"❌ Provider registration failed with status {register_response.status_code}")
            print(f"Response: {register_response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Provider registration failed: {e}")
        return False

def test_homeowner_registration_and_login():
    """Test homeowner registration and login for authorization testing"""
    print("\n🔍 Testing Homeowner Registration and Login...")
    global homeowner_token, homeowner_id
    
    try:
        # Register a new homeowner for testing
        test_email = f"homeownertest_{uuid.uuid4().hex[:8]}@doordtest.com"
        register_data = {
            "email": test_email,
            "password": "homeownertest123",
            "user_type": "homeowner",
            "name": "Test Homeowner",
            "phone": "+1-902-555-8888",
            "address": "456 Homeowner Ave, Halifax, NS"
        }
        
        # Register
        register_response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if register_response.status_code == 200:
            data = register_response.json()
            if "access_token" in data and "user" in data:
                homeowner_token = data["access_token"]
                homeowner_id = data["user"]["id"]
                print("✅ Homeowner registration and login successful")
                return True
            else:
                print(f"❌ Invalid registration response structure: {data}")
                return False
        else:
            print(f"❌ Homeowner registration failed with status {register_response.status_code}")
            print(f"Response: {register_response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Homeowner registration failed: {e}")
        return False

def test_provider_profile_update_basic():
    """Test basic provider profile update functionality"""
    print("\n🔍 Testing Provider Profile Update - Basic Information...")
    
    if not provider_token:
        print("❌ No provider token available for profile update test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {provider_token}", "Content-Type": "application/json"}
        
        # Test updating basic provider information
        profile_data = {
            "business_name": "Elite Home Services Pro",
            "description": "Professional home services with 15+ years of experience",
            "phone": "+1-902-555-9999",
            "address": "789 Professional Ave, Halifax, NS",
            "year_established": "2009"
        }
        
        response = requests.put(
            f"{BACKEND_URL}/providers/profile",
            json=profile_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "Profile updated successfully" in data.get("message", ""):
                print("✅ Basic profile update successful")
                return True
            else:
                print(f"❌ Unexpected response: {data}")
                return False
        else:
            print(f"❌ Profile update failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Basic profile update failed: {e}")
        return False

def test_provider_profile_update_services():
    """Test provider profile update with services and categories"""
    print("\n🔍 Testing Provider Profile Update - Services & Categories...")
    
    if not provider_token:
        print("❌ No provider token available for services update test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {provider_token}", "Content-Type": "application/json"}
        
        # Test updating services-related data
        profile_data = {
            "services": ["Plumbing", "Electrical", "HVAC Services", "Home Renovations"],
            "specialties": ["Emergency repairs", "Commercial services", "Eco-friendly solutions", "24/7 availability"],
            "service_categories": ["Residential", "Commercial", "Emergency Services"],
            "properties_served": ["Single Family Homes", "Condominiums", "Townhouses", "Small Businesses"]
        }
        
        response = requests.put(
            f"{BACKEND_URL}/providers/profile",
            json=profile_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "Profile updated successfully" in data.get("message", ""):
                print("✅ Services & categories update successful")
                return True
            else:
                print(f"❌ Unexpected response: {data}")
                return False
        else:
            print(f"❌ Services update failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Services update failed: {e}")
        return False

def test_provider_profile_update_pricing():
    """Test provider profile update with pricing packages"""
    print("\n🔍 Testing Provider Profile Update - Pricing Packages...")
    
    if not provider_token:
        print("❌ No provider token available for pricing update test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {provider_token}", "Content-Type": "application/json"}
        
        # Test updating pricing packages
        profile_data = {
            "pricing_packages": [
                {
                    "name": "Basic Service",
                    "price": "$75-150",
                    "description": "Standard home service calls",
                    "features": ["1-hour service", "Basic tools included", "Warranty included"]
                },
                {
                    "name": "Premium Service",
                    "price": "$200-400",
                    "description": "Comprehensive service with premium materials",
                    "features": ["2-hour service", "Premium materials", "Extended warranty", "Follow-up included"]
                },
                {
                    "name": "Emergency Service",
                    "price": "$150-300",
                    "description": "24/7 emergency response",
                    "features": ["Same-day service", "Emergency response", "Priority scheduling"]
                }
            ],
            "price_range": "$75-400"
        }
        
        response = requests.put(
            f"{BACKEND_URL}/providers/profile",
            json=profile_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "Profile updated successfully" in data.get("message", ""):
                print("✅ Pricing packages update successful")
                return True
            else:
                print(f"❌ Unexpected response: {data}")
                return False
        else:
            print(f"❌ Pricing update failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Pricing update failed: {e}")
        return False

def test_provider_profile_update_complete():
    """Test complete provider profile update with all fields"""
    print("\n🔍 Testing Provider Profile Update - Complete Profile...")
    
    if not provider_token:
        print("❌ No provider token available for complete profile update test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {provider_token}", "Content-Type": "application/json"}
        
        # Test updating complete profile data
        profile_data = {
            "business_name": "Halifax Premier Home Services",
            "description": "Your trusted partner for all home service needs. We provide professional, reliable, and affordable solutions for residential and commercial properties.",
            "phone": "+1-902-555-7777",
            "address": "456 Service Street, Halifax, NS B3H 2Y9",
            "year_established": "2010",
            "services": ["Plumbing", "Electrical", "HVAC Services", "Home Renovations", "Handyman Services"],
            "specialties": ["Emergency repairs", "Energy-efficient solutions", "Smart home installations", "Preventive maintenance"],
            "service_categories": ["Residential", "Commercial", "Emergency Services", "Maintenance"],
            "properties_served": ["Single Family Homes", "Condominiums", "Townhouses", "Apartments", "Small Businesses", "Retail Spaces"],
            "pricing_packages": [
                {
                    "name": "Standard Service",
                    "price": "$100-200",
                    "description": "Professional service for common home repairs",
                    "features": ["Professional assessment", "Quality materials", "1-year warranty"]
                },
                {
                    "name": "Premium Package",
                    "price": "$250-500",
                    "description": "Comprehensive service with premium solutions",
                    "features": ["Detailed consultation", "Premium materials", "Extended warranty", "Follow-up service"]
                }
            ],
            "price_range": "$100-500",
            "location": "Halifax, NS",
            "response_time": "Usually responds within 30 minutes"
        }
        
        response = requests.put(
            f"{BACKEND_URL}/providers/profile",
            json=profile_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "Profile updated successfully" in data.get("message", ""):
                print("✅ Complete profile update successful")
                return True
            else:
                print(f"❌ Unexpected response: {data}")
                return False
        else:
            print(f"❌ Complete profile update failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Complete profile update failed: {e}")
        return False

def test_profile_data_persistence():
    """Test that profile updates are properly stored and retrieved"""
    print("\n🔍 Testing Profile Data Persistence...")
    
    if not provider_token or not provider_id:
        print("❌ No provider credentials available for persistence test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        
        # First, update profile with specific test data
        test_business_name = f"Test Business {uuid.uuid4().hex[:8]}"
        test_description = f"Test description for persistence verification {uuid.uuid4().hex[:8]}"
        
        profile_data = {
            "business_name": test_business_name,
            "description": test_description,
            "year_established": "2023"
        }
        
        # Update profile
        update_response = requests.put(
            f"{BACKEND_URL}/providers/profile",
            json=profile_data,
            headers={"Authorization": f"Bearer {provider_token}", "Content-Type": "application/json"},
            timeout=30
        )
        
        if update_response.status_code != 200:
            print(f"❌ Profile update for persistence test failed with status {update_response.status_code}")
            return False
        
        # Now retrieve the profile to verify persistence
        response = requests.get(
            f"{BACKEND_URL}/providers/{provider_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            provider_data = response.json()
            
            # Verify the updated data is persisted
            if (provider_data.get("business_name") == test_business_name and 
                provider_data.get("description") == test_description and
                provider_data.get("year_established") == "2023"):
                print("✅ Profile data persistence verified")
                return True
            else:
                print(f"❌ Profile data not properly persisted")
                print(f"   Expected business_name: {test_business_name}")
                print(f"   Got business_name: {provider_data.get('business_name')}")
                print(f"   Expected description: {test_description}")
                print(f"   Got description: {provider_data.get('description')}")
                return False
        else:
            print(f"❌ Failed to retrieve provider profile with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Profile persistence test failed: {e}")
        return False

def test_authentication_required():
    """Test that authentication is required for profile updates"""
    print("\n🔍 Testing Authentication Requirements...")
    
    try:
        # Test without authentication token
        profile_data = {
            "business_name": "Unauthorized Update Test",
            "description": "This should fail"
        }
        
        response = requests.put(
            f"{BACKEND_URL}/providers/profile",
            json=profile_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 403:
            print("✅ Unauthenticated requests properly blocked (403)")
        elif response.status_code == 401:
            print("✅ Unauthenticated requests properly blocked (401)")
        else:
            print(f"❌ Expected 401/403 for unauthenticated request, got {response.status_code}")
            return False
        
        # Test with invalid token
        invalid_headers = {"Authorization": "Bearer invalid-jwt-token", "Content-Type": "application/json"}
        response = requests.put(
            f"{BACKEND_URL}/providers/profile",
            json=profile_data,
            headers=invalid_headers,
            timeout=30
        )
        
        if response.status_code == 401:
            print("✅ Invalid token properly rejected (401)")
            return True
        else:
            print(f"❌ Expected 401 for invalid token, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def test_authorization_provider_only():
    """Test that only providers can update profiles"""
    print("\n🔍 Testing Provider-Only Authorization...")
    
    if not homeowner_token:
        print("❌ No homeowner token available for authorization test")
        return False
    
    try:
        # Test homeowner trying to update provider profile
        headers = {"Authorization": f"Bearer {homeowner_token}", "Content-Type": "application/json"}
        
        profile_data = {
            "business_name": "Homeowner Unauthorized Update",
            "description": "This should fail"
        }
        
        response = requests.put(
            f"{BACKEND_URL}/providers/profile",
            json=profile_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 403:
            print("✅ Homeowner profile update properly blocked (403)")
            return True
        else:
            print(f"❌ Expected 403 for homeowner profile update, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Authorization test failed: {e}")
        return False

def test_partial_profile_updates():
    """Test partial profile updates (only updating some fields)"""
    print("\n🔍 Testing Partial Profile Updates...")
    
    if not provider_token:
        print("❌ No provider token available for partial update test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {provider_token}", "Content-Type": "application/json"}
        
        # Test updating only business name
        profile_data = {
            "business_name": "Partial Update Test Business"
        }
        
        response = requests.put(
            f"{BACKEND_URL}/providers/profile",
            json=profile_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "Profile updated successfully" in data.get("message", ""):
                print("✅ Partial profile update (business_name only) successful")
            else:
                print(f"❌ Unexpected response: {data}")
                return False
        else:
            print(f"❌ Partial profile update failed with status {response.status_code}")
            return False
        
        # Test updating only services array
        profile_data = {
            "services": ["Updated Service 1", "Updated Service 2"]
        }
        
        response = requests.put(
            f"{BACKEND_URL}/providers/profile",
            json=profile_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "Profile updated successfully" in data.get("message", ""):
                print("✅ Partial profile update (services only) successful")
                return True
            else:
                print(f"❌ Unexpected response: {data}")
                return False
        else:
            print(f"❌ Partial services update failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Partial update test failed: {e}")
        return False

def test_integration_with_existing_systems():
    """Test integration with existing order/appointment systems"""
    print("\n🔍 Testing Integration with Existing Systems...")
    
    if not provider_token or not provider_id:
        print("❌ No provider credentials available for integration test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {provider_token}", "Content-Type": "application/json"}
        
        # First, update provider profile with specific services
        profile_data = {
            "business_name": "Integration Test Services",
            "services": ["Integration Test Service", "Test Plumbing", "Test Electrical"],
            "specialties": ["Integration testing", "Quality assurance"]
        }
        
        # Update profile
        update_response = requests.put(
            f"{BACKEND_URL}/providers/profile",
            json=profile_data,
            headers=headers,
            timeout=30
        )
        
        if update_response.status_code != 200:
            print(f"❌ Profile update for integration test failed")
            return False
        
        # Test that updated profile data is available in provider listings
        response = requests.get(
            f"{BACKEND_URL}/providers",
            timeout=30
        )
        
        if response.status_code == 200:
            providers = response.json()
            
            # Find our provider in the list
            our_provider = None
            for provider in providers:
                if provider.get("id") == provider_id:
                    our_provider = provider
                    break
            
            if our_provider:
                if (our_provider.get("business_name") == "Integration Test Services" and
                    "Integration Test Service" in our_provider.get("services", [])):
                    print("✅ Updated profile data available in provider listings")
                else:
                    print(f"❌ Updated profile data not reflected in provider listings")
                    return False
            else:
                print(f"❌ Provider not found in listings")
                return False
        else:
            print(f"❌ Failed to retrieve provider listings")
            return False
        
        # Test creating an order with updated provider data
        order_data = {
            "homeowner_id": "test-homeowner-id",
            "provider_id": provider_id,
            "homeowner_name": "Integration Test Homeowner",
            "homeowner_email": "test@integration.com",
            "homeowner_phone": "+1-902-555-0000",
            "homeowner_address": "123 Integration St, Halifax, NS",
            "provider_name": "Integration Test Services",
            "service_type": "Integration Test Service",
            "services": ["Integration Test Service"],
            "description": "Testing integration with updated provider profile"
        }
        
        order_response = requests.post(
            f"{BACKEND_URL}/orders",
            json=order_data,
            headers=headers,
            timeout=30
        )
        
        if order_response.status_code == 200:
            print("✅ Order creation works with updated provider profile")
            return True
        else:
            print(f"❌ Order creation failed with updated profile: {order_response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Integration test failed: {e}")
        return False

def run_provider_profile_tests():
    """Run all provider profile management tests"""
    print("=" * 80)
    print("🚀 PROVIDER PROFILE MANAGEMENT BACKEND TESTING STARTED")
    print("=" * 80)
    
    test_results = []
    
    # Test 1: Backend Health
    test_results.append(("Backend Health", test_backend_health()))
    
    # Test 2: Provider Registration and Login
    test_results.append(("Provider Registration and Login", test_provider_registration_and_login()))
    
    # Test 3: Homeowner Registration and Login (for authorization testing)
    test_results.append(("Homeowner Registration and Login", test_homeowner_registration_and_login()))
    
    # Test 4: Basic Profile Update
    test_results.append(("Basic Profile Update", test_provider_profile_update_basic()))
    
    # Test 5: Services & Categories Update
    test_results.append(("Services & Categories Update", test_provider_profile_update_services()))
    
    # Test 6: Pricing Packages Update
    test_results.append(("Pricing Packages Update", test_provider_profile_update_pricing()))
    
    # Test 7: Complete Profile Update
    test_results.append(("Complete Profile Update", test_provider_profile_update_complete()))
    
    # Test 8: Profile Data Persistence
    test_results.append(("Profile Data Persistence", test_profile_data_persistence()))
    
    # Test 9: Authentication Required
    test_results.append(("Authentication Required", test_authentication_required()))
    
    # Test 10: Provider-Only Authorization
    test_results.append(("Provider-Only Authorization", test_authorization_provider_only()))
    
    # Test 11: Partial Profile Updates
    test_results.append(("Partial Profile Updates", test_partial_profile_updates()))
    
    # Test 12: Integration with Existing Systems
    test_results.append(("Integration with Existing Systems", test_integration_with_existing_systems()))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 PROVIDER PROFILE MANAGEMENT TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<40} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL PROVIDER PROFILE MANAGEMENT TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️ {failed} PROVIDER PROFILE MANAGEMENT TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = run_provider_profile_tests()
    sys.exit(0 if success else 1)