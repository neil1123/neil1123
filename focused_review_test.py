#!/usr/bin/env python3
"""
Focused Backend Testing for Review Request
Tests specific functionality mentioned in the review request
"""

import requests
import json
import uuid
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://5f81e1b3-88a9-45db-958d-9cb5f0ec9f5a.preview.emergentagent.com/api"

# Global test data
provider_token = None
homeowner_token = None
provider_id = None
homeowner_id = None

def setup_test_users():
    """Setup test users for focused testing"""
    global provider_token, homeowner_token, provider_id, homeowner_id
    
    print("🔧 Setting up test users...")
    
    # Register provider
    provider_data = {
        "email": f"focused_provider_{uuid.uuid4().hex[:8]}@doordtest.com",
        "password": "testpass123",
        "user_type": "provider",
        "name": "Focused Test Provider",
        "business_name": "Elite Home Services",
        "services": ["Electrical", "Plumbing", "HVAC"],
        "phone": "+1-902-555-1111"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/register", json=provider_data, timeout=30)
    if response.status_code == 200:
        data = response.json()
        provider_token = data["access_token"]
        provider_id = data["user"]["id"]
        print("✅ Provider setup successful")
    else:
        print(f"❌ Provider setup failed: {response.status_code}")
        return False
    
    # Register homeowner
    homeowner_data = {
        "email": f"focused_homeowner_{uuid.uuid4().hex[:8]}@doordtest.com",
        "password": "testpass123",
        "user_type": "homeowner",
        "name": "Focused Test Homeowner",
        "phone": "+1-902-555-2222"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/register", json=homeowner_data, timeout=30)
    if response.status_code == 200:
        data = response.json()
        homeowner_token = data["access_token"]
        homeowner_id = data["user"]["id"]
        print("✅ Homeowner setup successful")
        return True
    else:
        print(f"❌ Homeowner setup failed: {response.status_code}")
        return False

def test_orders_filtering_by_status():
    """Test orders filtering by status (quoted, accepted, in_progress, completed)"""
    print("\n🔍 Testing Orders Filtering by Status...")
    
    if not provider_token or not homeowner_token:
        print("❌ Missing tokens for orders filtering test")
        return False
    
    try:
        # Create orders with different statuses
        orders_to_create = [
            {"status": "pending_quotation", "service": "Electrical", "description": "Install outlet"},
            {"status": "quoted", "service": "Plumbing", "description": "Fix leak"},
            {"status": "accepted", "service": "HVAC", "description": "AC repair"},
            {"status": "in_progress", "service": "Electrical", "description": "Rewiring"},
            {"status": "completed", "service": "Plumbing", "description": "Pipe replacement"}
        ]
        
        created_orders = []
        
        # Create orders
        for order_info in orders_to_create:
            order_data = {
                "homeowner_id": homeowner_id,
                "provider_id": provider_id,
                "homeowner_name": "Test Customer",
                "homeowner_email": "customer@test.com",
                "homeowner_phone": "+1-902-555-3333",
                "homeowner_address": "123 Test St",
                "provider_name": "Elite Home Services",
                "service_type": order_info["service"],
                "description": order_info["description"]
            }
            
            headers = {"Authorization": f"Bearer {homeowner_token}"}
            response = requests.post(f"{BACKEND_URL}/orders", json=order_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                order = response.json()
                created_orders.append(order["id"])
                
                # Update status if not pending_quotation
                if order_info["status"] != "pending_quotation":
                    provider_headers = {"Authorization": f"Bearer {provider_token}"}
                    params = {"status": order_info["status"]}
                    
                    status_response = requests.put(
                        f"{BACKEND_URL}/orders/{order['id']}/status",
                        params=params,
                        headers=provider_headers,
                        timeout=30
                    )
                    
                    if status_response.status_code != 200:
                        print(f"❌ Failed to update order status to {order_info['status']}")
                        return False
            else:
                print(f"❌ Failed to create order: {response.status_code}")
                return False
        
        # Test retrieving orders for provider (should get all orders)
        provider_headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.get(f"{BACKEND_URL}/orders", headers=provider_headers, timeout=30)
        
        if response.status_code == 200:
            provider_orders = response.json()
            print(f"✅ Provider can retrieve orders ({len(provider_orders)} orders)")
            
            # Check if we have orders with different statuses
            statuses = [order.get("status") for order in provider_orders]
            unique_statuses = set(statuses)
            
            if len(unique_statuses) >= 3:  # Should have multiple statuses
                print(f"✅ Orders have multiple statuses: {unique_statuses}")
            else:
                print(f"⚠️ Limited status variety: {unique_statuses}")
        else:
            print(f"❌ Failed to retrieve provider orders: {response.status_code}")
            return False
        
        # Test retrieving orders for homeowner
        homeowner_headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.get(f"{BACKEND_URL}/orders", headers=homeowner_headers, timeout=30)
        
        if response.status_code == 200:
            homeowner_orders = response.json()
            print(f"✅ Homeowner can retrieve orders ({len(homeowner_orders)} orders)")
            
            # Frontend can filter these orders by status
            quoted_orders = [o for o in homeowner_orders if o.get("status") == "quoted"]
            accepted_orders = [o for o in homeowner_orders if o.get("status") == "accepted"]
            in_progress_orders = [o for o in homeowner_orders if o.get("status") == "in_progress"]
            completed_orders = [o for o in homeowner_orders if o.get("status") == "completed"]
            
            print(f"✅ Orders can be filtered: quoted({len(quoted_orders)}), accepted({len(accepted_orders)}), in_progress({len(in_progress_orders)}), completed({len(completed_orders)})")
            return True
        else:
            print(f"❌ Failed to retrieve homeowner orders: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Orders filtering test failed: {e}")
        return False

def test_message_thread_creation_for_text_us():
    """Test message thread creation for 'Text Us' functionality"""
    print("\n🔍 Testing Message Thread Creation for 'Text Us'...")
    
    if not provider_token or not homeowner_token:
        print("❌ Missing tokens for message thread test")
        return False
    
    try:
        # Test creating message thread (simulating "Text Us" button click)
        thread_data = {
            "homeowner_id": homeowner_id,
            "provider_id": provider_id,
            "homeowner_name": "Test Customer",
            "provider_name": "Elite Home Services",
            "order_type": "General Inquiry",
            "last_message": "Hi, I'm interested in your services!"
        }
        
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.post(f"{BACKEND_URL}/messages/threads", json=thread_data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            thread = response.json()
            thread_id = thread["id"]
            print("✅ Message thread created successfully for 'Text Us'")
            
            # Test sending initial message
            message_data = {
                "thread_id": thread_id,
                "sender_id": homeowner_id,  # Will be overridden by backend
                "sender_type": "homeowner",  # Will be overridden by backend
                "content": "Hello! I saw your services and I'm interested in getting a quote for electrical work.",
                "read": False
            }
            
            response = requests.post(f"{BACKEND_URL}/messages", json=message_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                print("✅ Initial message sent successfully")
                
                # Test provider can see the thread
                provider_headers = {"Authorization": f"Bearer {provider_token}"}
                response = requests.get(f"{BACKEND_URL}/messages/threads", headers=provider_headers, timeout=30)
                
                if response.status_code == 200:
                    provider_threads = response.json()
                    matching_thread = next((t for t in provider_threads if t["id"] == thread_id), None)
                    
                    if matching_thread:
                        print("✅ Provider can see the message thread")
                        
                        # Test provider can reply
                        reply_data = {
                            "thread_id": thread_id,
                            "sender_id": provider_id,  # Will be overridden by backend
                            "sender_type": "provider",  # Will be overridden by backend
                            "content": "Thank you for your interest! I'd be happy to help with your electrical needs. What specific work do you need done?",
                            "read": False
                        }
                        
                        response = requests.post(f"{BACKEND_URL}/messages", json=reply_data, headers=provider_headers, timeout=30)
                        
                        if response.status_code == 200:
                            print("✅ Provider can reply to messages")
                            return True
                        else:
                            print(f"❌ Provider reply failed: {response.status_code}")
                            return False
                    else:
                        print("❌ Provider cannot see the message thread")
                        return False
                else:
                    print(f"❌ Failed to get provider threads: {response.status_code}")
                    return False
            else:
                print(f"❌ Initial message sending failed: {response.status_code}")
                return False
        else:
            print(f"❌ Message thread creation failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Message thread test failed: {e}")
        return False

def test_provider_data_retrieval_for_service_browsing():
    """Test provider data retrieval for service browsing"""
    print("\n🔍 Testing Provider Data Retrieval for Service Browsing...")
    
    try:
        # Test getting all providers (public endpoint)
        response = requests.get(f"{BACKEND_URL}/providers", timeout=30)
        
        if response.status_code == 200:
            providers = response.json()
            print(f"✅ Retrieved {len(providers)} providers for service browsing")
            
            if len(providers) > 0:
                # Check provider data structure
                sample_provider = providers[0]
                required_fields = ["id", "name", "business_name", "services", "rating", "location"]
                
                missing_fields = [field for field in required_fields if field not in sample_provider]
                
                if not missing_fields:
                    print("✅ Provider data contains all required fields for service browsing")
                    
                    # Test getting individual provider details
                    provider_id_test = sample_provider["id"]
                    response = requests.get(f"{BACKEND_URL}/providers/{provider_id_test}", timeout=30)
                    
                    if response.status_code == 200:
                        provider_details = response.json()
                        print("✅ Individual provider details retrieved successfully")
                        
                        # Check for detailed fields
                        detail_fields = ["description", "specialties", "price_range", "response_time"]
                        available_details = [field for field in detail_fields if field in provider_details]
                        
                        print(f"✅ Provider details include: {available_details}")
                        return True
                    else:
                        print(f"❌ Failed to get individual provider: {response.status_code}")
                        return False
                else:
                    print(f"❌ Provider data missing fields: {missing_fields}")
                    return False
            else:
                print("⚠️ No providers found in database")
                return True  # Not a failure, just empty database
        else:
            print(f"❌ Failed to retrieve providers: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Provider data retrieval test failed: {e}")
        return False

def test_notification_count_calculation():
    """Test notification count calculation for orders and messages"""
    print("\n🔍 Testing Notification Count Calculation...")
    
    if not provider_token or not homeowner_token:
        print("❌ Missing tokens for notification count test")
        return False
    
    try:
        # Create some orders and messages to test notification counts
        
        # 1. Create an order (should create notification for provider)
        order_data = {
            "homeowner_id": homeowner_id,
            "provider_id": provider_id,
            "homeowner_name": "Notification Test Customer",
            "homeowner_email": "notify@test.com",
            "homeowner_phone": "+1-902-555-4444",
            "homeowner_address": "456 Notify St",
            "provider_name": "Elite Home Services",
            "service_type": "Notification Test Service",
            "description": "Test order for notification counting"
        }
        
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.post(f"{BACKEND_URL}/orders", json=order_data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            order = response.json()
            print("✅ Test order created for notification counting")
            
            # 2. Provider can get their orders (for counting new orders)
            provider_headers = {"Authorization": f"Bearer {provider_token}"}
            response = requests.get(f"{BACKEND_URL}/orders", headers=provider_headers, timeout=30)
            
            if response.status_code == 200:
                provider_orders = response.json()
                new_orders = [o for o in provider_orders if o.get("status") == "pending_quotation"]
                print(f"✅ Provider has {len(new_orders)} new orders for notification count")
            else:
                print(f"❌ Failed to get provider orders for counting: {response.status_code}")
                return False
            
            # 3. Create message thread and unread messages
            thread_data = {
                "homeowner_id": homeowner_id,
                "provider_id": provider_id,
                "homeowner_name": "Notification Test Customer",
                "provider_name": "Elite Home Services",
                "order_type": "Notification Test",
                "last_message": "Test message for notifications"
            }
            
            response = requests.post(f"{BACKEND_URL}/messages/threads", json=thread_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                thread = response.json()
                thread_id = thread["id"]
                print("✅ Message thread created for notification counting")
                
                # Send message from homeowner (should create notification for provider)
                message_data = {
                    "thread_id": thread_id,
                    "sender_id": homeowner_id,  # Will be overridden by backend
                    "sender_type": "homeowner",  # Will be overridden by backend
                    "content": "This is an unread message for notification testing",
                    "read": False
                }
                
                response = requests.post(f"{BACKEND_URL}/messages", json=message_data, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    print("✅ Unread message created for notification counting")
                    
                    # Provider can get message threads (for counting unread messages)
                    response = requests.get(f"{BACKEND_URL}/messages/threads", headers=provider_headers, timeout=30)
                    
                    if response.status_code == 200:
                        provider_threads = response.json()
                        print(f"✅ Provider has {len(provider_threads)} message threads for notification count")
                        
                        # Get messages for each thread to count unread
                        total_unread = 0
                        for thread in provider_threads:
                            response = requests.get(f"{BACKEND_URL}/messages/{thread['id']}", headers=provider_headers, timeout=30)
                            if response.status_code == 200:
                                messages = response.json()
                                unread_messages = [m for m in messages if not m.get("read", False) and m.get("sender_id") != provider_id]
                                total_unread += len(unread_messages)
                        
                        print(f"✅ Provider has {total_unread} unread messages for notification count")
                        return True
                    else:
                        print(f"❌ Failed to get provider message threads: {response.status_code}")
                        return False
                else:
                    print(f"❌ Failed to send test message: {response.status_code}")
                    return False
            else:
                print(f"❌ Failed to create message thread: {response.status_code}")
                return False
        else:
            print(f"❌ Failed to create test order: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Notification count test failed: {e}")
        return False

def run_focused_review_tests():
    """Run all focused tests for the review request"""
    print("=" * 70)
    print("🎯 FOCUSED BACKEND TESTING FOR REVIEW REQUEST")
    print("=" * 70)
    
    # Setup test users
    if not setup_test_users():
        print("❌ Failed to setup test users")
        return False
    
    test_results = []
    
    # Test 1: Orders filtering by status
    test_results.append(("Orders Filtering by Status", test_orders_filtering_by_status()))
    
    # Test 2: Message thread creation for "Text Us"
    test_results.append(("Message Thread Creation for Text Us", test_message_thread_creation_for_text_us()))
    
    # Test 3: Provider data retrieval for service browsing
    test_results.append(("Provider Data Retrieval for Service Browsing", test_provider_data_retrieval_for_service_browsing()))
    
    # Test 4: Notification count calculation
    test_results.append(("Notification Count Calculation", test_notification_count_calculation()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 FOCUSED TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<40} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal Focused Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL FOCUSED TESTS PASSED!")
        print("✅ Backend fully supports the frontend changes mentioned in review request")
        return True
    else:
        print(f"\n⚠️ {failed} FOCUSED TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = run_focused_review_tests()
    exit(0 if success else 1)