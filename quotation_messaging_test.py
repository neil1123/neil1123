#!/usr/bin/env python3
"""
Focused Quotation and Messaging Workflow Testing
Tests the complete quotation and messaging workflow as specified in the review request
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
test_order_id = None
test_thread_id = None

def test_authentication_workflow():
    """Test complete authentication workflow for both homeowner and provider"""
    print("🔍 Testing Authentication Workflow...")
    global provider_token, homeowner_token, provider_id, homeowner_id
    
    # Test 1: Homeowner login with test@homeowner.com/password123
    print("\n  Testing homeowner login with test@homeowner.com...")
    try:
        login_data = {
            "email": "test@homeowner.com",
            "password": "password123"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                homeowner_token = data["access_token"]
                homeowner_id = data["user"]["id"]
                print("  ✅ Homeowner login successful")
            else:
                print(f"  ❌ Invalid homeowner login response: {data}")
                return False
        else:
            print(f"  ❌ Homeowner login failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Homeowner login failed: {e}")
        return False
    
    # Test 2: Provider login with test@provider.com/password123
    print("\n  Testing provider login with test@provider.com...")
    try:
        login_data = {
            "email": "test@provider.com",
            "password": "password123"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                provider_token = data["access_token"]
                provider_id = data["user"]["id"]
                print("  ✅ Provider login successful")
            else:
                print(f"  ❌ Invalid provider login response: {data}")
                return False
        else:
            print(f"  ❌ Provider login failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Provider login failed: {e}")
        return False
    
    # Test 3: JWT token validation
    print("\n  Testing JWT token validation...")
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.get(
            f"{BACKEND_URL}/auth/me",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and "email" in data:
                print("  ✅ JWT token validation successful")
                return True
            else:
                print(f"  ❌ Invalid user data structure: {data}")
                return False
        else:
            print(f"  ❌ JWT validation failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ JWT validation failed: {e}")
        return False

def test_quotation_request_workflow():
    """Test complete quotation request workflow"""
    print("\n🔍 Testing Quotation Request Workflow...")
    global test_order_id
    
    if not homeowner_token or not provider_id:
        print("  ❌ Missing authentication data for quotation workflow")
        return False
    
    # Test 1: Create quotation request (POST /api/quotations)
    print("\n  Testing quotation request creation...")
    try:
        quotation_data = {
            "homeowner_id": homeowner_id,
            "provider_id": provider_id,
            "homeowner_name": "Test Homeowner",
            "homeowner_email": "test@homeowner.com",
            "homeowner_phone": "+1-902-555-1234",
            "homeowner_address": "123 Test St, Halifax, NS",
            "provider_name": "Test Provider Services",
            "service_type": "Plumbing Repair",
            "description": "Fix leaky kitchen faucet and check water pressure",
            "preferred_date": "2024-02-15",
            "preferred_time": "10:00 AM",
            "urgency": "medium",
            "budget": "$200-300"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/quotations",
            json=quotation_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "order_id" in data:
                test_order_id = data["order_id"]
                print("  ✅ Quotation request created successfully")
            else:
                print(f"  ❌ Invalid quotation response: {data}")
                return False
        else:
            print(f"  ❌ Quotation request failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Quotation request failed: {e}")
        return False
    
    # Test 2: Verify order created with "pending_quotation" status
    print("\n  Testing order creation with pending_quotation status...")
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.get(
            f"{BACKEND_URL}/orders/{test_order_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            order_data = response.json()
            if order_data.get("status") == "pending_quotation":
                print("  ✅ Order created with 'pending_quotation' status")
            else:
                print(f"  ❌ Expected 'pending_quotation', got '{order_data.get('status')}'")
                return False
        else:
            print(f"  ❌ Failed to retrieve order with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Order status check failed: {e}")
        return False
    
    # Test 3: Check if quotation appears when filtered by homeowner_id
    print("\n  Testing homeowner can retrieve their quotations...")
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.get(
            f"{BACKEND_URL}/orders",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            orders = response.json()
            homeowner_orders = [order for order in orders if order.get("homeowner_id") == homeowner_id]
            pending_orders = [order for order in homeowner_orders if order.get("status") == "pending_quotation"]
            
            if len(pending_orders) > 0:
                print(f"  ✅ Homeowner can retrieve quotations ({len(pending_orders)} pending)")
            else:
                print("  ❌ No pending quotations found for homeowner")
                return False
        else:
            print(f"  ❌ Failed to retrieve homeowner orders with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Homeowner order retrieval failed: {e}")
        return False
    
    return True

def test_quotation_status_updates():
    """Test quotation status update workflow"""
    print("\n🔍 Testing Quotation Status Updates...")
    
    if not provider_token or not homeowner_token or not test_order_id:
        print("  ❌ Missing data for status update testing")
        return False
    
    # Test 1: Provider updates quotation amount (changes status to "quoted")
    print("\n  Testing provider quotation update...")
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        params = {
            "quotation_amount": 275.00,
            "quotation_details": "Complete plumbing repair including faucet replacement and pressure adjustment"
        }
        
        response = requests.put(
            f"{BACKEND_URL}/orders/{test_order_id}/quotation",
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print("  ✅ Provider quotation update successful")
        else:
            print(f"  ❌ Provider quotation update failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Provider quotation update failed: {e}")
        return False
    
    # Test 2: Verify status changed to "quoted"
    print("\n  Testing status changed to 'quoted'...")
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.get(
            f"{BACKEND_URL}/orders/{test_order_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            order_data = response.json()
            if order_data.get("status") == "quoted":
                print("  ✅ Order status changed to 'quoted'")
            else:
                print(f"  ❌ Expected 'quoted', got '{order_data.get('status')}'")
                return False
        else:
            print(f"  ❌ Failed to retrieve updated order with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Order status verification failed: {e}")
        return False
    
    # Test 3: Homeowner accepts quote
    print("\n  Testing homeowner quote acceptance...")
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        params = {"status": "accepted"}
        
        response = requests.put(
            f"{BACKEND_URL}/orders/{test_order_id}/status",
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print("  ✅ Homeowner quote acceptance successful")
        else:
            print(f"  ❌ Homeowner quote acceptance failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Homeowner quote acceptance failed: {e}")
        return False
    
    # Test 4: Test homeowner can decline quotes (reset to declined)
    print("\n  Testing homeowner quote decline...")
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        params = {"status": "declined"}
        
        response = requests.put(
            f"{BACKEND_URL}/orders/{test_order_id}/status",
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print("  ✅ Homeowner quote decline successful")
        else:
            print(f"  ❌ Homeowner quote decline failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Homeowner quote decline failed: {e}")
        return False
    
    return True

def test_messaging_integration():
    """Test messaging system integration with quotation workflow"""
    print("\n🔍 Testing Messaging Integration...")
    global test_thread_id
    
    if not provider_token or not homeowner_token:
        print("  ❌ Missing authentication for messaging tests")
        return False
    
    # Test 1: Verify message thread was created during quotation request
    print("\n  Testing message thread creation...")
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.get(
            f"{BACKEND_URL}/messages/threads",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            threads = response.json()
            # Find thread related to our test order
            order_threads = [thread for thread in threads if thread.get("order_id") == test_order_id]
            
            if len(order_threads) > 0:
                test_thread_id = order_threads[0]["id"]
                print("  ✅ Message thread created during quotation request")
            else:
                print("  ❌ No message thread found for quotation request")
                return False
        else:
            print(f"  ❌ Failed to retrieve message threads with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Message thread retrieval failed: {e}")
        return False
    
    # Test 2: Check initial message content (should not be hardcoded)
    print("\n  Testing initial message content...")
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.get(
            f"{BACKEND_URL}/messages/{test_thread_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            messages = response.json()
            if len(messages) > 0:
                initial_message = messages[0]
                content = initial_message.get("content", "")
                
                # Check that message is not hardcoded template
                if "New quotation request" in content and "Plumbing Repair" in content:
                    print("  ✅ Initial message content is dynamic, not hardcoded")
                else:
                    print(f"  ❌ Unexpected initial message content: {content}")
                    return False
            else:
                print("  ❌ No initial message found in thread")
                return False
        else:
            print(f"  ❌ Failed to retrieve messages with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Initial message check failed: {e}")
        return False
    
    # Test 3: Provider can send message to homeowner
    print("\n  Testing provider can message homeowner...")
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        message_data = {
            "thread_id": test_thread_id,
            "content": "Thank you for your quotation request. I can help you with the plumbing repair. The quote I provided includes all materials and labor."
        }
        
        response = requests.post(
            f"{BACKEND_URL}/messages",
            json=message_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and "content" in data:
                print("  ✅ Provider can send messages to homeowner")
            else:
                print(f"  ❌ Invalid message response: {data}")
                return False
        else:
            print(f"  ❌ Provider message sending failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Provider message sending failed: {e}")
        return False
    
    # Test 4: Homeowner can send message to provider (bidirectional)
    print("\n  Testing homeowner can message provider...")
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        message_data = {
            "thread_id": test_thread_id,
            "content": "Thank you for the quote. When would be the earliest you could start the work?"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/messages",
            json=message_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and "content" in data:
                print("  ✅ Homeowner can send messages to provider")
            else:
                print(f"  ❌ Invalid homeowner message response: {data}")
                return False
        else:
            print(f"  ❌ Homeowner message sending failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Homeowner message sending failed: {e}")
        return False
    
    # Test 5: Verify bidirectional messaging works
    print("\n  Testing bidirectional messaging...")
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.get(
            f"{BACKEND_URL}/messages/{test_thread_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            messages = response.json()
            if len(messages) >= 3:  # Initial + provider + homeowner messages
                provider_messages = [msg for msg in messages if msg.get("sender_type") == "provider"]
                homeowner_messages = [msg for msg in messages if msg.get("sender_type") == "homeowner"]
                
                if len(provider_messages) >= 1 and len(homeowner_messages) >= 2:
                    print("  ✅ Bidirectional messaging working correctly")
                else:
                    print(f"  ❌ Message counts incorrect - Provider: {len(provider_messages)}, Homeowner: {len(homeowner_messages)}")
                    return False
            else:
                print(f"  ❌ Expected at least 3 messages, got {len(messages)}")
                return False
        else:
            print(f"  ❌ Failed to verify bidirectional messaging with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Bidirectional messaging verification failed: {e}")
        return False
    
    return True

def test_data_persistence():
    """Test data persistence in MongoDB"""
    print("\n🔍 Testing Data Persistence...")
    
    if not homeowner_token or not provider_token:
        print("  ❌ Missing authentication for persistence tests")
        return False
    
    # Test 1: Verify quotations are stored in MongoDB
    print("\n  Testing quotation data persistence...")
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.get(
            f"{BACKEND_URL}/orders",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            orders = response.json()
            test_orders = [order for order in orders if order.get("id") == test_order_id]
            
            if len(test_orders) > 0:
                order = test_orders[0]
                if (order.get("service_type") == "Plumbing Repair" and 
                    order.get("homeowner_id") == homeowner_id and
                    order.get("provider_id") == provider_id):
                    print("  ✅ Quotation data properly persisted in MongoDB")
                else:
                    print(f"  ❌ Quotation data incomplete: {order}")
                    return False
            else:
                print("  ❌ Test quotation not found in database")
                return False
        else:
            print(f"  ❌ Failed to retrieve orders for persistence test with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Quotation persistence test failed: {e}")
        return False
    
    # Test 2: Verify message data persistence
    print("\n  Testing message data persistence...")
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.get(
            f"{BACKEND_URL}/messages/{test_thread_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            messages = response.json()
            if len(messages) >= 3:
                # Check that messages have proper structure and are persisted
                for message in messages:
                    if not all(key in message for key in ["id", "thread_id", "sender_id", "sender_type", "content", "timestamp"]):
                        print(f"  ❌ Message missing required fields: {message}")
                        return False
                
                print("  ✅ Message data properly persisted in MongoDB")
            else:
                print(f"  ❌ Expected at least 3 messages, found {len(messages)}")
                return False
        else:
            print(f"  ❌ Failed to retrieve messages for persistence test with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Message persistence test failed: {e}")
        return False
    
    return True

def test_authentication_state():
    """Test authentication state and proper button display"""
    print("\n🔍 Testing Authentication State...")
    
    if not homeowner_token or not provider_token:
        print("  ❌ Missing authentication tokens for state testing")
        return False
    
    # Test 1: Verify JWT tokens are properly stored and sent
    print("\n  Testing JWT token handling...")
    try:
        # Test homeowner token
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.get(
            f"{BACKEND_URL}/auth/me",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get("user_type") == "homeowner":
                print("  ✅ Homeowner JWT token properly validated")
            else:
                print(f"  ❌ Unexpected homeowner user type: {user_data.get('user_type')}")
                return False
        else:
            print(f"  ❌ Homeowner token validation failed with status {response.status_code}")
            return False
        
        # Test provider token
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.get(
            f"{BACKEND_URL}/auth/me",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get("user_type") == "provider":
                print("  ✅ Provider JWT token properly validated")
            else:
                print(f"  ❌ Unexpected provider user type: {user_data.get('user_type')}")
                return False
        else:
            print(f"  ❌ Provider token validation failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ JWT token handling test failed: {e}")
        return False
    
    # Test 2: Verify proper access control
    print("\n  Testing access control...")
    try:
        # Test that homeowner cannot access provider-only endpoints
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.post(
            f"{BACKEND_URL}/appointments",
            json={"customer_name": "Test", "service_type": "Test", "date": "2024-01-01", "time": "10:00"},
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 403:
            print("  ✅ Homeowner properly blocked from provider endpoints")
        else:
            print(f"  ❌ Expected 403 for homeowner accessing provider endpoint, got {response.status_code}")
            return False
        
        # Test that provider can access provider endpoints
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.get(
            f"{BACKEND_URL}/appointments",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print("  ✅ Provider can access provider endpoints")
        else:
            print(f"  ❌ Provider access to provider endpoints failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Access control test failed: {e}")
        return False
    
    return True

def run_focused_tests():
    """Run all focused quotation and messaging workflow tests"""
    print("=" * 80)
    print("🎯 FOCUSED QUOTATION AND MESSAGING WORKFLOW TESTING")
    print("=" * 80)
    print("Testing critical issues as specified in review request:")
    print("• Homeowner quote requests appear in 'Pending' tab")
    print("• Authentication state shows proper buttons")
    print("• Provider can message homeowner after quote request")
    print("• No hardcoded messages in system")
    print("• End-to-end messaging system verification")
    print("=" * 80)
    
    test_results = []
    
    # Test 1: Authentication Workflow
    test_results.append(("Authentication Workflow", test_authentication_workflow()))
    
    # Test 2: Quotation Request Workflow
    test_results.append(("Quotation Request Workflow", test_quotation_request_workflow()))
    
    # Test 3: Quotation Status Updates
    test_results.append(("Quotation Status Updates", test_quotation_status_updates()))
    
    # Test 4: Messaging Integration
    test_results.append(("Messaging Integration", test_messaging_integration()))
    
    # Test 5: Data Persistence
    test_results.append(("Data Persistence", test_data_persistence()))
    
    # Test 6: Authentication State
    test_results.append(("Authentication State", test_authentication_state()))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 FOCUSED TEST SUMMARY")
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
        print("\n🎉 ALL FOCUSED TESTS PASSED!")
        print("✅ Quotation and messaging workflow is fully functional")
        return True
    else:
        print(f"\n⚠️ {failed} FOCUSED TESTS FAILED!")
        print("❌ Critical issues found in quotation and messaging workflow")
        return False

if __name__ == "__main__":
    success = run_focused_tests()
    sys.exit(0 if success else 1)