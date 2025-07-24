#!/usr/bin/env python3
"""
Additional verification tests for specific review request issues
"""

import requests
import json

BACKEND_URL = "https://5f81e1b3-88a9-45db-958d-9cb5f0ec9f5a.preview.emergentagent.com/api"

def test_homeowner_pending_tab_functionality():
    """Test that homeowner can see quotations in pending tab"""
    print("🔍 Testing Homeowner Pending Tab Functionality...")
    
    # Login as homeowner
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
    
    if response.status_code != 200:
        print("❌ Homeowner login failed")
        return False
    
    homeowner_data = response.json()
    homeowner_token = homeowner_data["access_token"]
    homeowner_id = homeowner_data["user"]["id"]
    
    # Get all orders for homeowner
    headers = {"Authorization": f"Bearer {homeowner_token}"}
    response = requests.get(
        f"{BACKEND_URL}/orders",
        headers=headers,
        timeout=30
    )
    
    if response.status_code != 200:
        print("❌ Failed to retrieve homeowner orders")
        return False
    
    orders = response.json()
    
    # Filter orders by status for different tabs
    pending_orders = [order for order in orders if order.get("status") == "pending_quotation"]
    quoted_orders = [order for order in orders if order.get("status") == "quoted"]
    accepted_orders = [order for order in orders if order.get("status") == "accepted"]
    declined_orders = [order for order in orders if order.get("status") == "declined"]
    
    print(f"  📊 Order Status Summary:")
    print(f"    Pending Quotations: {len(pending_orders)}")
    print(f"    Quoted Orders: {len(quoted_orders)}")
    print(f"    Accepted Orders: {len(accepted_orders)}")
    print(f"    Declined Orders: {len(declined_orders)}")
    
    # Verify that homeowner has orders in different states
    if len(pending_orders) > 0 or len(quoted_orders) > 0:
        print("  ✅ Homeowner can retrieve quotations for 'Pending' tab")
        return True
    else:
        print("  ❌ No quotations found for homeowner")
        return False

def test_no_hardcoded_messages():
    """Test that messages are not hardcoded templates"""
    print("\n🔍 Testing No Hardcoded Messages...")
    
    # Login as provider to access message threads
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
    
    if response.status_code != 200:
        print("❌ Provider login failed")
        return False
    
    provider_data = response.json()
    provider_token = provider_data["access_token"]
    
    # Get message threads
    headers = {"Authorization": f"Bearer {provider_token}"}
    response = requests.get(
        f"{BACKEND_URL}/messages/threads",
        headers=headers,
        timeout=30
    )
    
    if response.status_code != 200:
        print("❌ Failed to retrieve message threads")
        return False
    
    threads = response.json()
    
    if len(threads) == 0:
        print("❌ No message threads found")
        return False
    
    # Check messages in threads for hardcoded content
    hardcoded_patterns = [
        "Dear valued customer",
        "Thank you for choosing our services",
        "We look forward to working with you",
        "Please don't hesitate to contact us"
    ]
    
    for thread in threads[:3]:  # Check first 3 threads
        thread_id = thread["id"]
        
        response = requests.get(
            f"{BACKEND_URL}/messages/{thread_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            messages = response.json()
            
            for message in messages:
                content = message.get("content", "").lower()
                
                # Check if message contains hardcoded patterns
                is_hardcoded = any(pattern.lower() in content for pattern in hardcoded_patterns)
                
                if is_hardcoded:
                    print(f"  ❌ Found hardcoded message: {message.get('content')}")
                    return False
    
    print("  ✅ No hardcoded message templates found")
    return True

def test_provider_messaging_after_quote():
    """Test that provider can message homeowner immediately after quote request"""
    print("\n🔍 Testing Provider Messaging After Quote Request...")
    
    # Login as both users
    homeowner_login = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": "test@homeowner.com", "password": "password123"},
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    provider_login = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": "test@provider.com", "password": "password123"},
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if homeowner_login.status_code != 200 or provider_login.status_code != 200:
        print("❌ Authentication failed")
        return False
    
    homeowner_data = homeowner_login.json()
    provider_data = provider_login.json()
    
    homeowner_id = homeowner_data["user"]["id"]
    provider_id = provider_data["user"]["id"]
    provider_token = provider_data["access_token"]
    
    # Create a new quotation request
    quotation_data = {
        "homeowner_id": homeowner_id,
        "provider_id": provider_id,
        "homeowner_name": "Test Homeowner",
        "homeowner_email": "test@homeowner.com",
        "homeowner_phone": "+1-902-555-1234",
        "homeowner_address": "123 Test St, Halifax, NS",
        "provider_name": "Test Provider Services",
        "service_type": "Electrical Work",
        "description": "Install new electrical outlet in kitchen",
        "preferred_date": "2024-02-20",
        "budget": "$150-250"
    }
    
    response = requests.post(
        f"{BACKEND_URL}/quotations",
        json=quotation_data,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if response.status_code != 200:
        print("❌ Failed to create quotation request")
        return False
    
    quotation_response = response.json()
    order_id = quotation_response.get("order_id")
    
    # Get message threads to find the thread for this order
    headers = {"Authorization": f"Bearer {provider_token}"}
    response = requests.get(
        f"{BACKEND_URL}/messages/threads",
        headers=headers,
        timeout=30
    )
    
    if response.status_code != 200:
        print("❌ Failed to retrieve message threads")
        return False
    
    threads = response.json()
    order_thread = None
    
    for thread in threads:
        if thread.get("order_id") == order_id:
            order_thread = thread
            break
    
    if not order_thread:
        print("❌ No message thread found for quotation request")
        return False
    
    # Provider sends message immediately after quote request
    message_data = {
        "thread_id": order_thread["id"],
        "content": "I received your electrical work request. I can install the outlet for $200 including materials. When would be a good time to schedule?"
    }
    
    response = requests.post(
        f"{BACKEND_URL}/messages",
        json=message_data,
        headers=headers,
        timeout=30
    )
    
    if response.status_code == 200:
        print("  ✅ Provider can message homeowner immediately after quote request")
        return True
    else:
        print(f"  ❌ Provider messaging failed with status {response.status_code}")
        print(f"  Response: {response.text}")
        return False

def test_end_to_end_messaging():
    """Test complete end-to-end messaging system"""
    print("\n🔍 Testing End-to-End Messaging System...")
    
    # Login as both users
    homeowner_login = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": "test@homeowner.com", "password": "password123"},
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    provider_login = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": "test@provider.com", "password": "password123"},
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if homeowner_login.status_code != 200 or provider_login.status_code != 200:
        print("❌ Authentication failed")
        return False
    
    homeowner_data = homeowner_login.json()
    provider_data = provider_login.json()
    
    homeowner_token = homeowner_data["access_token"]
    provider_token = provider_data["access_token"]
    
    # Get existing message threads
    provider_headers = {"Authorization": f"Bearer {provider_token}"}
    response = requests.get(
        f"{BACKEND_URL}/messages/threads",
        headers=provider_headers,
        timeout=30
    )
    
    if response.status_code != 200 or len(response.json()) == 0:
        print("❌ No message threads available for testing")
        return False
    
    thread_id = response.json()[0]["id"]
    
    # Test conversation flow
    conversation_steps = [
        (provider_token, "Hello! I'm ready to provide you with a detailed quote for your project."),
        (homeowner_token, "Great! What's your availability this week?"),
        (provider_token, "I'm available Tuesday and Thursday afternoons. Would either work for you?"),
        (homeowner_token, "Thursday afternoon works perfectly. What time?"),
        (provider_token, "How about 2:00 PM? I'll bring all necessary materials.")
    ]
    
    for token, message_content in conversation_steps:
        headers = {"Authorization": f"Bearer {token}"}
        message_data = {
            "thread_id": thread_id,
            "content": message_content
        }
        
        response = requests.post(
            f"{BACKEND_URL}/messages",
            json=message_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Message sending failed: {response.text}")
            return False
    
    # Verify all messages were sent and received
    response = requests.get(
        f"{BACKEND_URL}/messages/{thread_id}",
        headers=provider_headers,
        timeout=30
    )
    
    if response.status_code == 200:
        messages = response.json()
        if len(messages) >= len(conversation_steps):
            print("  ✅ End-to-end messaging system working correctly")
            return True
        else:
            print(f"  ❌ Expected at least {len(conversation_steps)} messages, got {len(messages)}")
            return False
    else:
        print("❌ Failed to retrieve messages for verification")
        return False

def run_additional_tests():
    """Run additional verification tests"""
    print("=" * 80)
    print("🔍 ADDITIONAL VERIFICATION TESTS")
    print("=" * 80)
    print("Verifying specific issues mentioned in review request")
    print("=" * 80)
    
    test_results = []
    
    # Test 1: Homeowner Pending Tab Functionality
    test_results.append(("Homeowner Pending Tab", test_homeowner_pending_tab_functionality()))
    
    # Test 2: No Hardcoded Messages
    test_results.append(("No Hardcoded Messages", test_no_hardcoded_messages()))
    
    # Test 3: Provider Messaging After Quote
    test_results.append(("Provider Messaging After Quote", test_provider_messaging_after_quote()))
    
    # Test 4: End-to-End Messaging
    test_results.append(("End-to-End Messaging", test_end_to_end_messaging()))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 ADDITIONAL TESTS SUMMARY")
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
    
    print(f"\nTotal Additional Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL ADDITIONAL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️ {failed} ADDITIONAL TESTS FAILED!")
        return False

if __name__ == "__main__":
    run_additional_tests()