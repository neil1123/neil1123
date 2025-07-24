#!/usr/bin/env python3
"""
Text Us Messaging Flow Test
Tests the complete "Text Us" messaging flow as specified in the review request
"""

import requests
import json
import os
from datetime import datetime
import sys
import uuid

# Load environment variables
BACKEND_URL = "https://5f81e1b3-88a9-45db-958d-9cb5f0ec9f5a.preview.emergentagent.com/api"

# Test data from review request
HOMEOWNER_EMAIL = "homeowner1@example.com"
HOMEOWNER_PASSWORD = "password123"
PROVIDER_ID = "910d675a-0d7f-430d-bc42-932e8c238505"

# Global variables
homeowner_token = None
homeowner_id = None
test_thread_id = None

def test_homeowner_login():
    """Test homeowner login with provided credentials"""
    print("🔍 Step 1: Testing Homeowner Login...")
    global homeowner_token, homeowner_id
    
    try:
        login_data = {
            "email": HOMEOWNER_EMAIL,
            "password": HOMEOWNER_PASSWORD
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
                homeowner_name = data["user"]["name"]
                print(f"✅ Homeowner login successful - User: {homeowner_name} (ID: {homeowner_id})")
                return True
            else:
                print(f"❌ Invalid login response structure: {data}")
                return False
        else:
            print(f"❌ Homeowner login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Homeowner login failed: {e}")
        return False

def test_get_provider_details():
    """Test getting provider details by ID to confirm it exists"""
    print(f"\n🔍 Step 2: Testing Get Provider Details (ID: {PROVIDER_ID})...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/providers/{PROVIDER_ID}", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and "business_name" in data:
                business_name = data.get("business_name", "Unknown")
                services = data.get("services", [])
                location = data.get("location", "Unknown")
                print(f"✅ Provider found - Business: {business_name}")
                print(f"   Services: {', '.join(services) if services else 'None listed'}")
                print(f"   Location: {location}")
                return True, data
            else:
                print(f"❌ Invalid provider data structure: {data}")
                return False, None
        else:
            print(f"❌ Get provider failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
    except requests.exceptions.RequestException as e:
        print(f"❌ Get provider failed: {e}")
        return False, None

def test_create_message_thread(provider_data):
    """Test creating message thread between homeowner and provider"""
    print("\n🔍 Step 3: Testing Create Message Thread...")
    global test_thread_id
    
    if not homeowner_token or not homeowner_id:
        print("❌ Missing homeowner authentication data")
        return False
    
    try:
        thread_data = {
            "id": str(uuid.uuid4()),
            "homeowner_id": homeowner_id,
            "provider_id": PROVIDER_ID,
            "homeowner_name": "John Smith",  # From review request
            "provider_name": provider_data.get("business_name", "Halifax Cleaning Pro"),
            "order_type": "Text Us Inquiry",
            "last_message": "Initial contact via Text Us",
            "last_message_time": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat()
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
                print(f"✅ Message thread created successfully (Thread ID: {test_thread_id})")
                print(f"   Between: {data.get('homeowner_name')} ↔ {data.get('provider_name')}")
                return True
            else:
                print(f"❌ Invalid thread response structure: {data}")
                return False
        else:
            print(f"❌ Message thread creation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Message thread creation failed: {e}")
        return False

def test_send_first_message():
    """Test sending first message from homeowner to provider"""
    print("\n🔍 Step 4: Testing Send First Message...")
    
    if not homeowner_token or not test_thread_id:
        print("❌ Missing required data for sending message")
        return False
    
    try:
        # Using MessageCreate model (only requires thread_id and content)
        message_data = {
            "thread_id": test_thread_id,
            "content": "Hi! I'm interested in your services. Could you please provide more information about your availability and pricing?"
        }
        
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.post(
            f"{BACKEND_URL}/messages",
            json=message_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and "content" in data:
                print(f"✅ First message sent successfully")
                print(f"   Message ID: {data['id']}")
                print(f"   Sender: {data.get('sender_type', 'unknown')} (ID: {data.get('sender_id', 'unknown')})")
                print(f"   Content: {data['content'][:50]}...")
                return True
            else:
                print(f"❌ Invalid message response structure: {data}")
                return False
        else:
            print(f"❌ Message sending failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Message sending failed: {e}")
        return False

def test_retrieve_messages():
    """Test retrieving messages to verify conversation is working"""
    print("\n🔍 Step 5: Testing Retrieve Messages...")
    
    if not homeowner_token or not test_thread_id:
        print("❌ Missing required data for retrieving messages")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.get(
            f"{BACKEND_URL}/messages/{test_thread_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ Messages retrieved successfully ({len(data)} messages)")
                for i, message in enumerate(data, 1):
                    sender_type = message.get('sender_type', 'unknown')
                    content = message.get('content', '')
                    timestamp = message.get('timestamp', '')
                    print(f"   Message {i}: [{sender_type}] {content[:50]}{'...' if len(content) > 50 else ''}")
                return True
            else:
                print(f"❌ Expected list, got: {type(data)}")
                return False
        else:
            print(f"❌ Message retrieval failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Message retrieval failed: {e}")
        return False

def test_check_thread_list():
    """Test checking thread list to verify thread appears correctly"""
    print("\n🔍 Step 6: Testing Check Thread List...")
    
    if not homeowner_token:
        print("❌ Missing homeowner token for thread list check")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.get(
            f"{BACKEND_URL}/messages/threads",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ Thread list retrieved successfully ({len(data)} threads)")
                
                # Look for our test thread
                test_thread_found = False
                for thread in data:
                    if thread.get('id') == test_thread_id:
                        test_thread_found = True
                        print(f"   ✅ Test thread found in list:")
                        print(f"      Thread ID: {thread.get('id')}")
                        print(f"      Participants: {thread.get('homeowner_name')} ↔ {thread.get('provider_name')}")
                        print(f"      Last Message: {thread.get('last_message', '')[:50]}...")
                        print(f"      Order Type: {thread.get('order_type', 'Unknown')}")
                        break
                
                if test_thread_found:
                    print("✅ Thread appears correctly in homeowner's message list")
                    return True
                else:
                    print("❌ Test thread not found in homeowner's thread list")
                    return False
            else:
                print(f"❌ Expected list, got: {type(data)}")
                return False
        else:
            print(f"❌ Thread list retrieval failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Thread list retrieval failed: {e}")
        return False

def test_additional_message_flow():
    """Test sending additional messages to verify ongoing conversation"""
    print("\n🔍 Step 7: Testing Additional Message Flow...")
    
    if not homeowner_token or not test_thread_id:
        print("❌ Missing required data for additional message test")
        return False
    
    try:
        # Send a follow-up message
        message_data = {
            "thread_id": test_thread_id,
            "content": "Also, do you offer emergency services? I might need urgent assistance."
        }
        
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.post(
            f"{BACKEND_URL}/messages",
            json=message_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Follow-up message sent successfully")
            
            # Verify thread last_message was updated
            response = requests.get(
                f"{BACKEND_URL}/messages/threads",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                threads = response.json()
                for thread in threads:
                    if thread.get('id') == test_thread_id:
                        last_message = thread.get('last_message', '')
                        if "emergency services" in last_message.lower():
                            print("✅ Thread last_message updated correctly")
                            return True
                        else:
                            print(f"❌ Thread last_message not updated. Got: {last_message}")
                            return False
                
                print("❌ Test thread not found when checking last_message update")
                return False
            else:
                print("❌ Failed to verify thread last_message update")
                return False
        else:
            print(f"❌ Follow-up message failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Additional message flow test failed: {e}")
        return False

def run_text_us_flow_test():
    """Run the complete Text Us messaging flow test"""
    print("=" * 80)
    print("🚀 TEXT US MESSAGING FLOW TEST STARTED")
    print("=" * 80)
    print(f"Testing with:")
    print(f"  Homeowner: {HOMEOWNER_EMAIL}")
    print(f"  Provider ID: {PROVIDER_ID}")
    print(f"  Backend URL: {BACKEND_URL}")
    print("=" * 80)
    
    test_results = []
    provider_data = None
    
    # Step 1: Login as homeowner
    test_results.append(("Homeowner Login", test_homeowner_login()))
    
    # Step 2: Get provider details
    if test_results[-1][1]:  # If login succeeded
        success, provider_data = test_get_provider_details()
        test_results.append(("Get Provider Details", success))
    else:
        test_results.append(("Get Provider Details", False))
    
    # Step 3: Create message thread
    if test_results[-1][1] and provider_data:  # If provider found
        test_results.append(("Create Message Thread", test_create_message_thread(provider_data)))
    else:
        test_results.append(("Create Message Thread", False))
    
    # Step 4: Send first message
    if test_results[-1][1]:  # If thread created
        test_results.append(("Send First Message", test_send_first_message()))
    else:
        test_results.append(("Send First Message", False))
    
    # Step 5: Retrieve messages
    if test_results[-1][1]:  # If message sent
        test_results.append(("Retrieve Messages", test_retrieve_messages()))
    else:
        test_results.append(("Retrieve Messages", False))
    
    # Step 6: Check thread list
    if test_results[-2][1]:  # If thread operations working
        test_results.append(("Check Thread List", test_check_thread_list()))
    else:
        test_results.append(("Check Thread List", False))
    
    # Step 7: Additional message flow
    if test_results[-1][1]:  # If thread list working
        test_results.append(("Additional Message Flow", test_additional_message_flow()))
    else:
        test_results.append(("Additional Message Flow", False))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEXT US FLOW TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 TEXT US MESSAGING FLOW TEST PASSED!")
        print("✅ Complete 'Text Us' functionality is working correctly")
        print("✅ Homeowner can successfully message providers")
        print("✅ Message threads are created and managed properly")
        print("✅ Conversation flow is fully functional")
        return True
    else:
        print(f"\n⚠️ {failed} TEXT US FLOW TESTS FAILED!")
        print("❌ Text Us messaging functionality has issues")
        return False

if __name__ == "__main__":
    success = run_text_us_flow_test()
    sys.exit(0 if success else 1)