#!/usr/bin/env python3
"""
Focused Backend API Testing for Critical User Issues
Tests the specific APIs mentioned in the review request
"""

import requests
import json
import uuid
import sys

# Backend URL from environment
BACKEND_URL = "https://5f81e1b3-88a9-45db-958d-9cb5f0ec9f5a.preview.emergentagent.com/api"

# Test credentials
HOMEOWNER_EMAIL = "test@homeowner.com"
HOMEOWNER_PASSWORD = "password123"
PROVIDER_EMAIL = "test@provider.com"
PROVIDER_PASSWORD = "password123"

# Global test data
homeowner_token = None
provider_token = None
homeowner_id = None
provider_id = None
test_order_id = None
test_thread_id = None

def test_authentication():
    """Test authentication for both homeowner and provider"""
    print("🔍 Testing Authentication...")
    global homeowner_token, provider_token, homeowner_id, provider_id
    
    try:
        # Test homeowner login
        homeowner_data = {
            "email": HOMEOWNER_EMAIL,
            "password": HOMEOWNER_PASSWORD
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=homeowner_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            homeowner_token = data["access_token"]
            homeowner_id = data["user"]["id"]
            print("✅ Homeowner authentication successful")
        else:
            print(f"❌ Homeowner authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Test provider login
        provider_data = {
            "email": PROVIDER_EMAIL,
            "password": PROVIDER_PASSWORD
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=provider_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            provider_token = data["access_token"]
            provider_id = data["user"]["id"]
            print("✅ Provider authentication successful")
            return True
        else:
            print(f"❌ Provider authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Authentication failed: {e}")
        return False

def test_message_thread_creation():
    """Test POST /api/messages/threads (for creating message threads from 'Get best deals')"""
    print("\n🔍 Testing Message Thread Creation (GET BEST DEALS)...")
    global test_thread_id
    
    if not homeowner_token or not provider_id or not homeowner_id:
        print("❌ Missing authentication data for message thread test")
        return False
    
    try:
        thread_data = {
            "homeowner_id": homeowner_id,
            "provider_id": provider_id,
            "homeowner_name": "Test Homeowner",
            "provider_name": "Test Provider",
            "order_type": "General Inquiry",
            "last_message": "Hi, I'm interested in your services. Can we discuss?"
        }
        
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.post(
            f"{BACKEND_URL}/messages/threads",
            json=thread_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data:
                test_thread_id = data["id"]
                print("✅ Message thread creation successful (Get Best Deals workflow)")
                return True
            else:
                print(f"❌ Invalid thread response structure: {data}")
                return False
        else:
            print(f"❌ Message thread creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Message thread creation failed: {e}")
        return False

def test_homeowner_orders_retrieval():
    """Test GET /api/orders (for homeowner orders display)"""
    print("\n🔍 Testing Homeowner Orders Retrieval...")
    
    if not homeowner_token:
        print("❌ No homeowner token for orders retrieval test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.get(
            f"{BACKEND_URL}/orders",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ Homeowner orders retrieved successfully ({len(data)} orders)")
                
                # Check if any orders have quotation amounts
                orders_with_quotes = [order for order in data if order.get("quotation_amount") is not None]
                if orders_with_quotes:
                    print(f"ℹ️ Found {len(orders_with_quotes)} orders with quotation amounts")
                    for order in orders_with_quotes[:3]:  # Show first 3
                        amount = order.get("quotation_amount")
                        print(f"   Order {order.get('id', 'N/A')[:8]}...: ${amount}")
                
                return True
            else:
                print(f"❌ Expected list, got: {type(data)}")
                return False
        else:
            print(f"❌ Homeowner orders retrieval failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Homeowner orders retrieval failed: {e}")
        return False

def test_quotation_amount_storage():
    """Test PUT /api/orders/{order_id}/quotation (for setting exact quotation amounts)"""
    print("\n🔍 Testing Quotation Amount Storage...")
    global test_order_id
    
    if not provider_token or not homeowner_id or not provider_id:
        print("❌ Missing authentication data for quotation test")
        return False
    
    try:
        # First create an order to test quotation on
        order_data = {
            "homeowner_id": homeowner_id,
            "provider_id": provider_id,
            "homeowner_name": "Test Homeowner",
            "homeowner_email": "test@homeowner.com",
            "homeowner_phone": "+1-902-555-0123",
            "homeowner_address": "123 Test St, Halifax, NS",
            "provider_name": "Test Provider",
            "service_type": "Plumbing",
            "description": "Test quotation amount storage",
            "preferred_date": "2024-01-15",
            "budget": "$200-300"
        }
        
        homeowner_headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.post(
            f"{BACKEND_URL}/orders",
            json=order_data,
            headers=homeowner_headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to create test order: {response.status_code}")
            return False
        
        order_response = response.json()
        test_order_id = order_response["id"]
        print("✅ Test order created for quotation testing")
        
        # Now test quotation amount update
        provider_headers = {"Authorization": f"Bearer {provider_token}"}
        exact_amount = 275.50  # Exact amount, not a range
        
        params = {
            "quotation_amount": exact_amount,
            "quotation_details": "Exact quotation: $275.50 for plumbing repair including parts and labor"
        }
        
        response = requests.put(
            f"{BACKEND_URL}/orders/{test_order_id}/quotation",
            params=params,
            headers=provider_headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Quotation amount update successful")
            
            # Verify the exact amount was stored
            response = requests.get(
                f"{BACKEND_URL}/orders/{test_order_id}",
                headers=provider_headers,
                timeout=30
            )
            
            if response.status_code == 200:
                order_data = response.json()
                stored_amount = order_data.get("quotation_amount")
                
                if stored_amount == exact_amount:
                    print(f"✅ Exact quotation amount stored correctly: ${stored_amount}")
                    print(f"✅ Order status updated to: {order_data.get('status')}")
                    return True
                else:
                    print(f"❌ Amount mismatch. Expected: ${exact_amount}, Got: ${stored_amount}")
                    return False
            else:
                print(f"❌ Failed to verify stored amount: {response.status_code}")
                return False
        else:
            print(f"❌ Quotation amount update failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Quotation amount storage test failed: {e}")
        return False

def test_notification_badges():
    """Test GET /api/messages/threads (for notification badges)"""
    print("\n🔍 Testing Notification Badge Calculation...")
    
    if not homeowner_token or not provider_token:
        print("❌ Missing tokens for notification badge test")
        return False
    
    try:
        # Test homeowner notification count
        homeowner_headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.get(
            f"{BACKEND_URL}/messages/threads",
            headers=homeowner_headers,
            timeout=30
        )
        
        if response.status_code == 200:
            homeowner_threads = response.json()
            print(f"✅ Homeowner message threads retrieved: {len(homeowner_threads)} threads")
        else:
            print(f"❌ Homeowner threads retrieval failed: {response.status_code}")
            return False
        
        # Test provider notification count
        provider_headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.get(
            f"{BACKEND_URL}/messages/threads",
            headers=provider_headers,
            timeout=30
        )
        
        if response.status_code == 200:
            provider_threads = response.json()
            print(f"✅ Provider message threads retrieved: {len(provider_threads)} threads")
        else:
            print(f"❌ Provider threads retrieval failed: {response.status_code}")
            return False
        
        # Test orders count for notification badges
        response = requests.get(
            f"{BACKEND_URL}/orders",
            headers=homeowner_headers,
            timeout=30
        )
        
        if response.status_code == 200:
            homeowner_orders = response.json()
            pending_orders = [order for order in homeowner_orders if order.get("status") in ["pending_quotation", "quoted"]]
            print(f"✅ Homeowner orders for badges: {len(homeowner_orders)} total, {len(pending_orders)} pending/quoted")
            return True
        else:
            print(f"❌ Homeowner orders for badges failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Notification badge test failed: {e}")
        return False

def test_complete_workflow():
    """Test the complete workflow: Get Best Deals -> Message Thread -> Order -> Quotation"""
    print("\n🔍 Testing Complete Workflow Integration...")
    
    if not homeowner_token or not provider_token:
        print("❌ Missing tokens for complete workflow test")
        return False
    
    try:
        # Step 1: Create message thread (Get Best Deals button)
        thread_data = {
            "homeowner_id": homeowner_id,
            "provider_id": provider_id,
            "homeowner_name": "Workflow Test Homeowner",
            "provider_name": "Workflow Test Provider",
            "order_type": "Kitchen Renovation",
            "last_message": "Hi! I clicked 'Get Best Deals' and would like to discuss kitchen renovation."
        }
        
        homeowner_headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.post(
            f"{BACKEND_URL}/messages/threads",
            json=thread_data,
            headers=homeowner_headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Workflow Step 1 failed: {response.status_code}")
            return False
        
        workflow_thread_id = response.json()["id"]
        print("✅ Step 1: Message thread created from 'Get Best Deals'")
        
        # Step 2: Send initial message
        message_data = {
            "thread_id": workflow_thread_id,
            "sender_id": homeowner_id,
            "sender_type": "homeowner",
            "content": "I'm interested in a complete kitchen renovation. Can you provide a quote?"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/messages",
            json=message_data,
            headers=homeowner_headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Workflow Step 2 failed: {response.status_code}")
            return False
        
        print("✅ Step 2: Initial message sent")
        
        # Step 3: Create order for quotation
        order_data = {
            "homeowner_id": homeowner_id,
            "provider_id": provider_id,
            "homeowner_name": "Workflow Test Homeowner",
            "homeowner_email": "workflow@homeowner.com",
            "homeowner_phone": "+1-902-555-9999",
            "homeowner_address": "999 Workflow St, Halifax, NS",
            "provider_name": "Workflow Test Provider",
            "service_type": "Kitchen Renovation",
            "description": "Complete kitchen renovation from Get Best Deals workflow",
            "preferred_date": "2024-02-01",
            "budget": "$20000-25000"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/orders",
            json=order_data,
            headers=homeowner_headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Workflow Step 3 failed: {response.status_code}")
            return False
        
        workflow_order_id = response.json()["id"]
        print("✅ Step 3: Order created for quotation")
        
        # Step 4: Provider provides exact quotation
        provider_headers = {"Authorization": f"Bearer {provider_token}"}
        params = {
            "quotation_amount": 22750.00,  # Exact amount
            "quotation_details": "Complete kitchen renovation: $22,750.00 - Premium package with granite countertops"
        }
        
        response = requests.put(
            f"{BACKEND_URL}/orders/{workflow_order_id}/quotation",
            params=params,
            headers=provider_headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Workflow Step 4 failed: {response.status_code}")
            return False
        
        print("✅ Step 4: Provider provided exact quotation amount")
        
        # Step 5: Verify homeowner can see the exact amount
        response = requests.get(
            f"{BACKEND_URL}/orders/{workflow_order_id}",
            headers=homeowner_headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Workflow Step 5 failed: {response.status_code}")
            return False
        
        order_data = response.json()
        if order_data.get("quotation_amount") == 22750.00:
            print("✅ Step 5: Homeowner can see exact quotation amount (not range)")
        else:
            print(f"❌ Step 5: Amount mismatch: {order_data.get('quotation_amount')}")
            return False
        
        # Step 6: Test notification badge data
        response = requests.get(
            f"{BACKEND_URL}/orders",
            headers=homeowner_headers,
            timeout=30
        )
        
        if response.status_code == 200:
            orders = response.json()
            quoted_orders = [o for o in orders if o.get("status") == "quoted"]
            print(f"✅ Step 6: Notification badge data available ({len(quoted_orders)} quoted orders)")
        else:
            print(f"❌ Workflow Step 6 failed: {response.status_code}")
            return False
        
        print("✅ COMPLETE WORKFLOW TEST PASSED")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Complete workflow test failed: {e}")
        return False

def run_focused_tests():
    """Run focused tests for critical user issues"""
    print("=" * 80)
    print("🎯 FOCUSED BACKEND TESTING FOR CRITICAL USER ISSUES")
    print("=" * 80)
    print("Testing the specific APIs mentioned in the review request:")
    print("1. POST /api/messages/threads (Get Best Deals button)")
    print("2. GET /api/orders (homeowner orders display)")
    print("3. PUT /api/orders/{order_id}/quotation (exact quotation amounts)")
    print("4. GET /api/messages/threads (notification badges)")
    print("=" * 80)
    
    test_results = []
    
    # Test 1: Authentication
    test_results.append(("Authentication Setup", test_authentication()))
    
    # Test 2: Message Thread Creation (Get Best Deals)
    test_results.append(("Message Thread Creation (Get Best Deals)", test_message_thread_creation()))
    
    # Test 3: Homeowner Orders Retrieval
    test_results.append(("Homeowner Orders Retrieval", test_homeowner_orders_retrieval()))
    
    # Test 4: Quotation Amount Storage
    test_results.append(("Quotation Amount Storage (Exact Numbers)", test_quotation_amount_storage()))
    
    # Test 5: Notification Badge Data
    test_results.append(("Notification Badge Calculation", test_notification_badges()))
    
    # Test 6: Complete Workflow Integration
    test_results.append(("Complete Workflow Integration", test_complete_workflow()))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 FOCUSED TEST RESULTS")
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
        print("\n🎉 ALL CRITICAL BACKEND APIS ARE WORKING!")
        print("✅ Get Best Deals button workflow supported")
        print("✅ Orders system properly retrieves homeowner orders")
        print("✅ Quotation amounts stored as exact numbers (not ranges)")
        print("✅ Notification badge data available")
        return True
    else:
        print(f"\n⚠️ {failed} CRITICAL BACKEND TESTS FAILED!")
        print("❌ Some user-reported issues may be due to backend problems")
        return False

if __name__ == "__main__":
    success = run_focused_tests()
    sys.exit(0 if success else 1)