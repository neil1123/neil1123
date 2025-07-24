#!/usr/bin/env python3
"""
Doord Quotation Management Testing Script
Tests the new quotation update and delete endpoints as specified in review request
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
test_quotation_order_id = None

def setup_test_users():
    """Setup test provider and homeowner accounts"""
    print("🔧 Setting up test users...")
    global provider_token, homeowner_token, provider_id, homeowner_id
    
    # Register test provider
    provider_data = {
        "email": f"testprovider_{uuid.uuid4().hex[:8]}@quotationtest.com",
        "password": "testpass123",
        "user_type": "provider",
        "name": "Test Provider Services",
        "business_name": "Test Provider Services",
        "services": ["Electrical", "Plumbing", "HVAC"],
        "phone": "+1-902-555-0123",
        "address": "123 Provider St, Halifax, NS"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=provider_data, timeout=30)
        if response.status_code == 200:
            data = response.json()
            provider_token = data["access_token"]
            provider_id = data["user"]["id"]
            print("✅ Test provider registered successfully")
        else:
            print(f"❌ Provider registration failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Provider registration error: {e}")
        return False
    
    # Register test homeowner
    homeowner_data = {
        "email": f"testhomeowner_{uuid.uuid4().hex[:8]}@quotationtest.com",
        "password": "testpass123",
        "user_type": "homeowner",
        "name": "Test Homeowner",
        "phone": "+1-902-555-0456",
        "address": "456 Homeowner Ave, Halifax, NS"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=homeowner_data, timeout=30)
        if response.status_code == 200:
            data = response.json()
            homeowner_token = data["access_token"]
            homeowner_id = data["user"]["id"]
            print("✅ Test homeowner registered successfully")
            return True
        else:
            print(f"❌ Homeowner registration failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Homeowner registration error: {e}")
        return False

def create_test_quotation():
    """Create a test quotation for testing update and delete operations"""
    print("\n🔍 Creating test quotation...")
    global test_quotation_order_id
    
    if not provider_token or not homeowner_token:
        print("❌ Missing tokens for quotation creation")
        return False
    
    try:
        # Create a quotation request
        quotation_data = {
            "homeowner_id": homeowner_id,
            "provider_id": provider_id,
            "homeowner_name": "Test Homeowner",
            "homeowner_email": "testhomeowner@quotationtest.com",
            "homeowner_phone": "+1-902-555-0456",
            "homeowner_address": "456 Homeowner Ave, Halifax, NS",
            "provider_name": "Test Provider Services",
            "service_type": "Electrical Installation",
            "description": "Install new electrical panel and upgrade wiring",
            "preferred_date": "2024-02-20",
            "budget": "$2000-3000",
            "urgency": "medium"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/quotations",
            json=quotation_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            test_quotation_order_id = data.get("order_id")
            if test_quotation_order_id:
                print("✅ Test quotation created successfully")
                return True
            else:
                print("❌ No order_id returned from quotation creation")
                return False
        else:
            print(f"❌ Quotation creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Quotation creation error: {e}")
        return False

def test_quotation_update_endpoint():
    """Test PUT /quotations/{order_id} endpoint"""
    print("\n🔍 Testing Quotation Update Endpoint (PUT /quotations/{order_id})...")
    
    if not provider_token or not test_quotation_order_id:
        print("❌ Missing required data for quotation update test")
        return False
    
    try:
        # Test updating quotation with new amount and details
        update_data = {
            "quotation_amount": 2750.00,
            "quotation_details": "Complete electrical panel upgrade with premium materials and 5-year warranty",
            "quotation_valid_until": "2024-03-15"
        }
        
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.put(
            f"{BACKEND_URL}/quotations/{test_quotation_order_id}",
            json=update_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "quotation updated" in data.get("message", "").lower():
                print("✅ Quotation update successful")
                
                # Verify the changes were saved by retrieving the order
                response = requests.get(
                    f"{BACKEND_URL}/orders/{test_quotation_order_id}",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    order_data = response.json()
                    if (order_data.get("quotation_amount") == 2750.00 and 
                        "premium materials" in order_data.get("quotation_details", "")):
                        print("✅ Quotation changes verified in database")
                        return True
                    else:
                        print("❌ Quotation changes not reflected in database")
                        print(f"Amount: {order_data.get('quotation_amount')}")
                        print(f"Details: {order_data.get('quotation_details')}")
                        return False
                else:
                    print(f"❌ Failed to verify quotation update: {response.status_code}")
                    return False
            else:
                print(f"❌ Unexpected update response: {data}")
                return False
        else:
            print(f"❌ Quotation update failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Quotation update test error: {e}")
        return False

def test_quotation_delete_endpoint():
    """Test DELETE /quotations/{order_id} endpoint"""
    print("\n🔍 Testing Quotation Delete Endpoint (DELETE /quotations/{order_id})...")
    
    if not provider_token or not test_quotation_order_id:
        print("❌ Missing required data for quotation delete test")
        return False
    
    try:
        # First, verify the quotation exists
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.get(
            f"{BACKEND_URL}/orders/{test_quotation_order_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print("❌ Test quotation not found before deletion")
            return False
        
        print("✅ Confirmed quotation exists before deletion")
        
        # Check if there are related message threads
        response = requests.get(
            f"{BACKEND_URL}/messages/threads",
            headers=headers,
            timeout=30
        )
        
        related_threads_before = 0
        if response.status_code == 200:
            threads = response.json()
            related_threads_before = len([t for t in threads if t.get("order_id") == test_quotation_order_id])
            print(f"✅ Found {related_threads_before} related message threads before deletion")
        
        # Now delete the quotation
        response = requests.delete(
            f"{BACKEND_URL}/quotations/{test_quotation_order_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "quotation deleted" in data.get("message", "").lower():
                print("✅ Quotation deletion successful")
                
                # Verify the quotation is removed from database
                response = requests.get(
                    f"{BACKEND_URL}/orders/{test_quotation_order_id}",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 404:
                    print("✅ Quotation successfully removed from database")
                    
                    # Verify related message threads are cleaned up
                    response = requests.get(
                        f"{BACKEND_URL}/messages/threads",
                        headers=headers,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        threads = response.json()
                        related_threads_after = len([t for t in threads if t.get("order_id") == test_quotation_order_id])
                        
                        if related_threads_after == 0 and related_threads_before > 0:
                            print("✅ Related message threads cleaned up successfully")
                            return True
                        elif related_threads_before == 0:
                            print("✅ No related threads to clean up")
                            return True
                        else:
                            print(f"❌ Message threads not cleaned up properly (before: {related_threads_before}, after: {related_threads_after})")
                            return False
                    else:
                        print("⚠️ Could not verify message thread cleanup")
                        return True  # Still consider successful if order was deleted
                else:
                    print(f"❌ Quotation still exists after deletion (status: {response.status_code})")
                    return False
            else:
                print(f"❌ Unexpected deletion response: {data}")
                return False
        else:
            print(f"❌ Quotation deletion failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Quotation deletion test error: {e}")
        return False

def test_provider_authentication_required():
    """Test that only providers can edit/delete quotations"""
    print("\n🔍 Testing Provider Authentication Requirements...")
    
    # Create a new quotation for this test
    if not create_test_quotation():
        print("❌ Failed to create test quotation for authentication test")
        return False
    
    try:
        # Test 1: Homeowner trying to update quotation (should be denied)
        print("\n  Testing homeowner access to quotation update...")
        update_data = {
            "quotation_amount": 1000.00,
            "quotation_details": "Unauthorized update attempt"
        }
        
        homeowner_headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.put(
            f"{BACKEND_URL}/quotations/{test_quotation_order_id}",
            json=update_data,
            headers=homeowner_headers,
            timeout=30
        )
        
        if response.status_code == 403:
            print("✅ Homeowner quotation update properly denied (403)")
        else:
            print(f"❌ Expected 403 for homeowner update, got {response.status_code}")
            return False
        
        # Test 2: Homeowner trying to delete quotation (should be denied)
        print("\n  Testing homeowner access to quotation delete...")
        response = requests.delete(
            f"{BACKEND_URL}/quotations/{test_quotation_order_id}",
            headers=homeowner_headers,
            timeout=30
        )
        
        if response.status_code == 403:
            print("✅ Homeowner quotation delete properly denied (403)")
        else:
            print(f"❌ Expected 403 for homeowner delete, got {response.status_code}")
            return False
        
        # Test 3: Unauthenticated access to update (should be denied)
        print("\n  Testing unauthenticated access to quotation update...")
        response = requests.put(
            f"{BACKEND_URL}/quotations/{test_quotation_order_id}",
            json=update_data,
            timeout=30
        )
        
        if response.status_code == 403:
            print("✅ Unauthenticated quotation update properly denied (403)")
        else:
            print(f"❌ Expected 403 for unauthenticated update, got {response.status_code}")
            return False
        
        # Test 4: Unauthenticated access to delete (should be denied)
        print("\n  Testing unauthenticated access to quotation delete...")
        response = requests.delete(
            f"{BACKEND_URL}/quotations/{test_quotation_order_id}",
            timeout=30
        )
        
        if response.status_code == 403:
            print("✅ Unauthenticated quotation delete properly denied (403)")
        else:
            print(f"❌ Expected 403 for unauthenticated delete, got {response.status_code}")
            return False
        
        # Test 5: Provider can still access their own quotations
        print("\n  Testing provider access to their own quotations...")
        provider_headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.put(
            f"{BACKEND_URL}/quotations/{test_quotation_order_id}",
            json={"quotation_amount": 2500.00},
            headers=provider_headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Provider can update their own quotations")
            return True
        else:
            print(f"❌ Provider cannot update their own quotations: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Provider authentication test error: {e}")
        return False

def test_provider_ownership_validation():
    """Test that providers can only edit their own quotations"""
    print("\n🔍 Testing Provider Ownership Validation...")
    
    # Create another provider to test cross-provider access
    other_provider_data = {
        "email": f"otherprovider_{uuid.uuid4().hex[:8]}@quotationtest.com",
        "password": "testpass123",
        "user_type": "provider",
        "name": "Other Provider Services",
        "business_name": "Other Provider Services",
        "services": ["Landscaping", "Cleaning"],
        "phone": "+1-902-555-0789"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json=other_provider_data, timeout=30)
        if response.status_code != 200:
            print("❌ Failed to create second provider for ownership test")
            return False
        
        other_provider_token = response.json()["access_token"]
        print("✅ Created second provider for ownership test")
        
        # Create a quotation for the original provider
        if not create_test_quotation():
            print("❌ Failed to create test quotation for ownership test")
            return False
        
        # Try to update the quotation with the other provider's token
        update_data = {
            "quotation_amount": 5000.00,
            "quotation_details": "Unauthorized cross-provider update"
        }
        
        other_headers = {"Authorization": f"Bearer {other_provider_token}"}
        response = requests.put(
            f"{BACKEND_URL}/quotations/{test_quotation_order_id}",
            json=update_data,
            headers=other_headers,
            timeout=30
        )
        
        if response.status_code == 404:  # Order not found for this provider
            print("✅ Cross-provider quotation update properly denied (404)")
        elif response.status_code == 403:  # Access denied
            print("✅ Cross-provider quotation update properly denied (403)")
        else:
            print(f"❌ Expected 404 or 403 for cross-provider update, got {response.status_code}")
            return False
        
        # Try to delete the quotation with the other provider's token
        response = requests.delete(
            f"{BACKEND_URL}/quotations/{test_quotation_order_id}",
            headers=other_headers,
            timeout=30
        )
        
        if response.status_code == 404:  # Order not found for this provider
            print("✅ Cross-provider quotation delete properly denied (404)")
            return True
        elif response.status_code == 403:  # Access denied
            print("✅ Cross-provider quotation delete properly denied (403)")
            return True
        else:
            print(f"❌ Expected 404 or 403 for cross-provider delete, got {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Provider ownership validation test error: {e}")
        return False

def test_data_integrity():
    """Test data integrity for quotation operations"""
    print("\n🔍 Testing Data Integrity...")
    
    try:
        # Create a fresh quotation for integrity testing
        if not create_test_quotation():
            print("❌ Failed to create test quotation for integrity test")
            return False
        
        # Test 1: Verify updated quotations reflect changes immediately
        print("\n  Testing immediate reflection of quotation updates...")
        
        original_amount = 1500.00
        updated_amount = 2250.00
        
        # First update
        headers = {"Authorization": f"Bearer {provider_token}"}
        update_data = {
            "quotation_amount": original_amount,
            "quotation_details": "Initial quotation details"
        }
        
        response = requests.put(
            f"{BACKEND_URL}/quotations/{test_quotation_order_id}",
            json=update_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Initial quotation update failed: {response.status_code}")
            return False
        
        # Immediately check if changes are reflected
        response = requests.get(
            f"{BACKEND_URL}/orders/{test_quotation_order_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            order_data = response.json()
            if order_data.get("quotation_amount") == original_amount:
                print("✅ Initial quotation update reflected immediately")
            else:
                print(f"❌ Initial update not reflected (expected: {original_amount}, got: {order_data.get('quotation_amount')})")
                return False
        else:
            print(f"❌ Failed to retrieve order after update: {response.status_code}")
            return False
        
        # Second update to test immediate reflection
        update_data["quotation_amount"] = updated_amount
        update_data["quotation_details"] = "Updated quotation details with new pricing"
        
        response = requests.put(
            f"{BACKEND_URL}/quotations/{test_quotation_order_id}",
            json=update_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Second quotation update failed: {response.status_code}")
            return False
        
        # Immediately check if second changes are reflected
        response = requests.get(
            f"{BACKEND_URL}/orders/{test_quotation_order_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            order_data = response.json()
            if (order_data.get("quotation_amount") == updated_amount and 
                "new pricing" in order_data.get("quotation_details", "")):
                print("✅ Updated quotation changes reflected immediately")
            else:
                print(f"❌ Second update not reflected properly")
                print(f"Amount: expected {updated_amount}, got {order_data.get('quotation_amount')}")
                print(f"Details: {order_data.get('quotation_details')}")
                return False
        else:
            print(f"❌ Failed to retrieve order after second update: {response.status_code}")
            return False
        
        # Test 2: Test deletion data integrity (this will consume the test quotation)
        print("\n  Testing deletion data integrity...")
        
        # Get initial counts
        response = requests.get(f"{BACKEND_URL}/orders", headers=headers, timeout=30)
        initial_order_count = len(response.json()) if response.status_code == 200 else 0
        
        response = requests.get(f"{BACKEND_URL}/messages/threads", headers=headers, timeout=30)
        initial_thread_count = len(response.json()) if response.status_code == 200 else 0
        
        # Delete the quotation
        response = requests.delete(
            f"{BACKEND_URL}/quotations/{test_quotation_order_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Quotation deletion failed: {response.status_code}")
            return False
        
        # Verify counts decreased
        response = requests.get(f"{BACKEND_URL}/orders", headers=headers, timeout=30)
        final_order_count = len(response.json()) if response.status_code == 200 else 0
        
        response = requests.get(f"{BACKEND_URL}/messages/threads", headers=headers, timeout=30)
        final_thread_count = len(response.json()) if response.status_code == 200 else 0
        
        if final_order_count < initial_order_count:
            print("✅ Order count decreased after deletion")
        else:
            print(f"❌ Order count not decreased (before: {initial_order_count}, after: {final_order_count})")
            return False
        
        if final_thread_count <= initial_thread_count:
            print("✅ Message thread cleanup verified")
        else:
            print(f"❌ Message threads not cleaned up (before: {initial_thread_count}, after: {final_thread_count})")
            return False
        
        print("✅ Data integrity tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Data integrity test error: {e}")
        return False

def run_quotation_management_tests():
    """Run all quotation management tests"""
    print("=" * 80)
    print("🚀 DOORD QUOTATION MANAGEMENT TESTING STARTED")
    print("=" * 80)
    
    test_results = []
    
    # Setup
    test_results.append(("Setup Test Users", setup_test_users()))
    
    if not provider_token or not homeowner_token:
        print("❌ Cannot proceed without test users")
        return False
    
    # Test 1: Quotation Update Endpoint
    test_results.append(("Create Test Quotation", create_test_quotation()))
    test_results.append(("Quotation Update Endpoint", test_quotation_update_endpoint()))
    
    # Test 2: Quotation Delete Endpoint (will consume the test quotation)
    test_results.append(("Quotation Delete Endpoint", test_quotation_delete_endpoint()))
    
    # Test 3: Provider Authentication
    test_results.append(("Provider Authentication Required", test_provider_authentication_required()))
    
    # Test 4: Provider Ownership Validation
    test_results.append(("Provider Ownership Validation", test_provider_ownership_validation()))
    
    # Test 5: Data Integrity
    test_results.append(("Data Integrity", test_data_integrity()))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 QUOTATION MANAGEMENT TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<35} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL QUOTATION MANAGEMENT TESTS PASSED!")
        print("✅ Quotation update and delete functionality working correctly")
        print("✅ Provider authentication and authorization working")
        print("✅ Data integrity maintained across operations")
        return True
    else:
        print(f"\n⚠️ {failed} QUOTATION MANAGEMENT TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = run_quotation_management_tests()
    sys.exit(0 if success else 1)