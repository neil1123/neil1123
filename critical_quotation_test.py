#!/usr/bin/env python3
"""
Critical Homeowner Quotation Test
Tests the specific functionality that was previously failing
"""

import requests
import json
import uuid
from datetime import datetime

# Backend URL
BACKEND_URL = "https://5f81e1b3-88a9-45db-958d-9cb5f0ec9f5a.preview.emergentagent.com/api"

def test_critical_homeowner_quotation():
    """Test the critical homeowner quotation acceptance/decline functionality"""
    print("🚨 CRITICAL HOMEOWNER QUOTATION TESTING")
    print("=" * 60)
    
    # Step 1: Register homeowner
    print("\n1️⃣ Registering homeowner...")
    homeowner_data = {
        "email": f"critical_homeowner_{uuid.uuid4().hex[:8]}@test.com",
        "password": "testpass123",
        "user_type": "homeowner",
        "name": "Critical Test Homeowner",
        "phone": "+1-902-555-1111",
        "address": "123 Critical St, Halifax, NS"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=homeowner_data, timeout=10)
        if response.status_code != 200:
            print(f"❌ Homeowner registration failed: {response.status_code}")
            return False
        
        homeowner_result = response.json()
        homeowner_token = homeowner_result["access_token"]
        homeowner_id = homeowner_result["user"]["id"]
        print("✅ Homeowner registered successfully")
    except Exception as e:
        print(f"❌ Homeowner registration error: {e}")
        return False
    
    # Step 2: Register provider
    print("\n2️⃣ Registering provider...")
    provider_data = {
        "email": f"critical_provider_{uuid.uuid4().hex[:8]}@test.com",
        "password": "testpass123",
        "user_type": "provider",
        "name": "Critical Test Provider",
        "phone": "+1-902-555-2222",
        "business_name": "Critical Services Inc",
        "services": ["Plumbing"],
        "license": "NS-CRITICAL-123"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=provider_data, timeout=10)
        if response.status_code != 200:
            print(f"❌ Provider registration failed: {response.status_code}")
            return False
        
        provider_result = response.json()
        provider_token = provider_result["access_token"]
        provider_id = provider_result["user"]["id"]
        print("✅ Provider registered successfully")
    except Exception as e:
        print(f"❌ Provider registration error: {e}")
        return False
    
    # Step 3: Create quotation request
    print("\n3️⃣ Creating quotation request...")
    quotation_data = {
        "homeowner_id": homeowner_id,
        "provider_id": provider_id,
        "homeowner_name": "Critical Test Homeowner",
        "homeowner_email": "critical_homeowner@test.com",
        "homeowner_phone": "+1-902-555-1111",
        "homeowner_address": "123 Critical St, Halifax, NS",
        "provider_name": "Critical Services Inc",
        "service_type": "Plumbing",
        "description": "Critical plumbing repair test",
        "preferred_date": "2024-01-20",
        "budget": "$200-300"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/quotations", json=quotation_data, timeout=10)
        if response.status_code != 200:
            print(f"❌ Quotation request failed: {response.status_code}")
            return False
        
        result = response.json()
        order_id = result["order_id"]
        print("✅ Quotation request created successfully")
    except Exception as e:
        print(f"❌ Quotation request error: {e}")
        return False
    
    # Step 4: Provider quotes the order
    print("\n4️⃣ Provider providing quote...")
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.put(
            f"{BACKEND_URL}/orders/{order_id}/status?status=quoted",
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Provider quote failed: {response.status_code}")
            return False
        
        print("✅ Provider quote successful")
    except Exception as e:
        print(f"❌ Provider quote error: {e}")
        return False
    
    # Step 5: CRITICAL TEST - Homeowner accepts quote
    print("\n5️⃣ 🚨 CRITICAL TEST: Homeowner accepting quote...")
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.put(
            f"{BACKEND_URL}/orders/{order_id}/status?status=accepted",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 🎉 CRITICAL SUCCESS: Homeowner can accept quotes!")
            accept_success = True
        elif response.status_code == 403:
            print("❌ 🚨 CRITICAL FAILURE: Homeowner cannot accept quotes (403 Forbidden)")
            accept_success = False
        else:
            print(f"❌ 🚨 CRITICAL FAILURE: Unexpected status {response.status_code}")
            print(f"Response: {response.text}")
            accept_success = False
    except Exception as e:
        print(f"❌ 🚨 CRITICAL FAILURE: Accept quote error: {e}")
        accept_success = False
    
    # Step 6: Create another order for decline test
    print("\n6️⃣ Creating second order for decline test...")
    try:
        quotation_data["description"] = "Second critical plumbing test for decline"
        response = requests.post(f"{BACKEND_URL}/quotations", json=quotation_data, timeout=10)
        if response.status_code != 200:
            print(f"❌ Second quotation request failed: {response.status_code}")
            return False
        
        decline_order_id = response.json()["order_id"]
        
        # Provider quotes this order too
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.put(
            f"{BACKEND_URL}/orders/{decline_order_id}/status?status=quoted",
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Provider quote for decline test failed: {response.status_code}")
            return False
        
        print("✅ Second order created and quoted")
    except Exception as e:
        print(f"❌ Second order creation error: {e}")
        return False
    
    # Step 7: CRITICAL TEST - Homeowner declines quote
    print("\n7️⃣ 🚨 CRITICAL TEST: Homeowner declining quote...")
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.put(
            f"{BACKEND_URL}/orders/{decline_order_id}/status?status=declined",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 🎉 CRITICAL SUCCESS: Homeowner can decline quotes!")
            decline_success = True
        elif response.status_code == 403:
            print("❌ 🚨 CRITICAL FAILURE: Homeowner cannot decline quotes (403 Forbidden)")
            decline_success = False
        else:
            print(f"❌ 🚨 CRITICAL FAILURE: Unexpected status {response.status_code}")
            print(f"Response: {response.text}")
            decline_success = False
    except Exception as e:
        print(f"❌ 🚨 CRITICAL FAILURE: Decline quote error: {e}")
        decline_success = False
    
    # Step 8: Test invalid status (should fail)
    print("\n8️⃣ Testing invalid status update (should fail)...")
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.put(
            f"{BACKEND_URL}/orders/{order_id}/status?status=completed",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 400:
            print("✅ Invalid status properly rejected")
            invalid_status_test = True
        else:
            print(f"❌ Invalid status should have been rejected: {response.status_code}")
            invalid_status_test = False
    except Exception as e:
        print(f"❌ Invalid status test error: {e}")
        invalid_status_test = False
    
    # Final Results
    print("\n" + "=" * 60)
    print("🏁 CRITICAL TEST RESULTS")
    print("=" * 60)
    
    tests = [
        ("Homeowner Accept Quote", accept_success),
        ("Homeowner Decline Quote", decline_success),
        ("Invalid Status Rejection", invalid_status_test)
    ]
    
    passed = 0
    failed = 0
    critical_failures = 0
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
        else:
            failed += 1
            if "Accept" in test_name or "Decline" in test_name:
                critical_failures += 1
    
    print(f"\nTotal Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if critical_failures > 0:
        print(f"\n🚨 CRITICAL ISSUE: {critical_failures} critical homeowner quotation tests failed!")
        print("❌ The backend API fix did NOT resolve the homeowner quotation issue")
        return False
    elif failed == 0:
        print("\n🎉 ALL CRITICAL TESTS PASSED!")
        print("✅ The backend API fix successfully resolved the homeowner quotation issue")
        return True
    else:
        print(f"\n⚠️ {failed} non-critical tests failed, but core functionality works")
        print("✅ The backend API fix successfully resolved the homeowner quotation issue")
        return True

if __name__ == "__main__":
    success = test_critical_homeowner_quotation()
    exit(0 if success else 1)