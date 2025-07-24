#!/usr/bin/env python3
"""
Text Us Messaging Functionality Test
Tests the specific "Text Us" messaging flow for homeowners as described in the review request
"""

import requests
import json
import os
from datetime import datetime
import sys
import uuid

# Load environment variables
BACKEND_URL = "https://5f81e1b3-88a9-45db-958d-9cb5f0ec9f5a.preview.emergentagent.com/api"

# Test data
homeowner_token = None
homeowner_id = None
provider_id = "56414503-b0f2-4d92-87b0-9ba25c4c76eb"  # Specific provider ID from review request
test_thread_id = None

def test_homeowner_login():
    """Test homeowner login with test@homeowner.com / password123"""
    print("🔍 Testing Homeowner Login (test@homeowner.com)...")
    global homeowner_token, homeowner_id
    
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
                print(f"✅ Homeowner login successful - User ID: {homeowner_id}")
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

def test_provider_exists():
    """Test that the specific provider ID exists"""
    print(f"🔍 Testing Provider Exists (ID: {provider_id})...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/providers/{provider_id}", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and "business_name" in data:
                print(f"✅ Provider found - Business: {data.get('business_name', 'Unknown')}")
                return True
            else:
                print(f"❌ Invalid provider data structure: {data}")
                return False
        elif response.status_code == 404:
            print(f"❌ Provider with ID {provider_id} not found")
            return False
        else:
            print(f"❌ Provider lookup failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Provider lookup failed: {e}")
        return False

def test_create_message_thread():
    """Test creating a message thread with the specific provider"""
    print(f"🔍 Testing Message Thread Creation with Provider {provider_id}...")
    global test_thread_id
    
    if not homeowner_token or not homeowner_id:
        print("❌ Missing homeowner authentication for thread creation")
        return False
    
    try:
        # First get provider details to get the name
        provider_response = requests.get(f"{BACKEND_URL}/providers/{provider_id}", timeout=30)
        if provider_response.status_code != 200:
            print("❌ Could not get provider details for thread creation")
            return False
        
        provider_data = provider_response.json()
        provider_name = provider_data.get('business_name', 'Unknown Provider')
        
        thread_data = {
            "homeowner_id": homeowner_id,
            "provider_id": provider_id,
            "homeowner_name": "Test Homeowner",
            "provider_name": provider_name,
            "order_type": "Text Us Inquiry",
            "last_message": "Initial contact via Text Us button"
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
                print(f"✅ Message thread created successfully - Thread ID: {test_thread_id}")
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

def test_send_message_to_thread():
    """Test sending a message to the created thread"""
    print("🔍 Testing Send Message to Thread...")
    
    if not homeowner_token or not test_thread_id:
        print("❌ Missing required data for message sending")
        return False
    
    try:
        message_data = {
            "thread_id": test_thread_id,
            "sender_id": homeowner_id,  # Will be overridden by backend
            "sender_type": "homeowner",  # Will be overridden by backend
            "content": "Hi! I'm interested in your services. I clicked 'Text Us' to get in touch with you directly."
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
                print(f"✅ Message sent successfully - Message ID: {data['id']}")
                print(f"   Content: {data['content']}")
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

def test_retrieve_messages_from_thread():
    """Test retrieving messages from the thread"""
    print("🔍 Testing Retrieve Messages from Thread...")
    
    if not homeowner_token or not test_thread_id:
        print("❌ Missing required data for message retrieval")
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
                
                # Verify our sent message appears
                for message in data:
                    if message.get('sender_id') == homeowner_id:
                        print(f"   Found our message: {message.get('content', '')[:50]}...")
                        return True
                
                print("❌ Our sent message not found in retrieved messages")
                return False
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

def test_get_homeowner_message_threads():
    """Test getting all message threads for the homeowner"""
    print("🔍 Testing Get Homeowner Message Threads...")
    
    if not homeowner_token:
        print("❌ No homeowner token available for thread retrieval")
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
                print(f"✅ Message threads retrieved successfully ({len(data)} threads)")
                
                # Verify our created thread appears
                for thread in data:
                    if thread.get('id') == test_thread_id:
                        print(f"   Found our thread with provider: {thread.get('provider_name', 'Unknown')}")
                        return True
                
                print("❌ Our created thread not found in retrieved threads")
                return False
            else:
                print(f"❌ Expected list, got: {type(data)}")
                return False
        else:
            print(f"❌ Thread retrieval failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Thread retrieval failed: {e}")
        return False

def test_authentication_token_issues():
    """Test for authentication token issues that might prevent messaging"""
    print("🔍 Testing Authentication Token Issues...")
    
    if not homeowner_token:
        print("❌ No homeowner token available for authentication testing")
        return False
    
    try:
        # Test 1: Verify token is valid for protected endpoints
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.get(
            f"{BACKEND_URL}/auth/me",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Authentication token is valid")
        else:
            print(f"❌ Authentication token validation failed with status {response.status_code}")
            return False
        
        # Test 2: Test token with messaging endpoints
        response = requests.get(
            f"{BACKEND_URL}/messages/threads",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Authentication token works with messaging endpoints")
            return True
        else:
            print(f"❌ Authentication token failed with messaging endpoints: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Authentication token testing failed: {e}")
        return False

def test_thread_selection_problems():
    """Test for thread selection problems that might prevent messaging"""
    print("🔍 Testing Thread Selection Problems...")
    
    if not homeowner_token or not test_thread_id:
        print("❌ Missing required data for thread selection testing")
        return False
    
    try:
        # Test 1: Verify thread exists and is accessible
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.get(
            f"{BACKEND_URL}/messages/{test_thread_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Thread is accessible and can be selected")
        else:
            print(f"❌ Thread selection failed with status {response.status_code}")
            return False
        
        # Test 2: Verify thread appears in homeowner's thread list
        response = requests.get(
            f"{BACKEND_URL}/messages/threads",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            threads = response.json()
            thread_found = any(thread.get('id') == test_thread_id for thread in threads)
            if thread_found:
                print("✅ Thread appears in homeowner's thread list")
                return True
            else:
                print("❌ Thread not found in homeowner's thread list")
                return False
        else:
            print(f"❌ Failed to get thread list with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Thread selection testing failed: {e}")
        return False

def run_text_us_tests():
    """Run all Text Us messaging functionality tests"""
    print("=" * 70)
    print("🚀 TEXT US MESSAGING FUNCTIONALITY TESTING STARTED")
    print("=" * 70)
    print("Testing the complete 'Text Us' messaging flow for homeowners")
    print(f"Target Provider ID: {provider_id}")
    print("=" * 70)
    
    test_results = []
    
    # Test 1: Homeowner Login
    test_results.append(("Homeowner Login (test@homeowner.com)", test_homeowner_login()))
    
    # Test 2: Provider Exists
    test_results.append(("Provider Exists Check", test_provider_exists()))
    
    # Test 3: Create Message Thread
    test_results.append(("Create Message Thread", test_create_message_thread()))
    
    # Test 4: Send Message to Thread
    test_results.append(("Send Message to Thread", test_send_message_to_thread()))
    
    # Test 5: Retrieve Messages from Thread
    test_results.append(("Retrieve Messages from Thread", test_retrieve_messages_from_thread()))
    
    # Test 6: Get Homeowner Message Threads
    test_results.append(("Get Homeowner Message Threads", test_get_homeowner_message_threads()))
    
    # DIAGNOSTIC TESTS FOR KNOWN ISSUES
    print("\n" + "=" * 70)
    print("🔍 DIAGNOSTIC TESTS FOR KNOWN ISSUES")
    print("=" * 70)
    
    # Test 7: Authentication Token Issues
    test_results.append(("Authentication Token Issues", test_authentication_token_issues()))
    
    # Test 8: Thread Selection Problems
    test_results.append(("Thread Selection Problems", test_thread_selection_problems()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEXT US MESSAGING TEST SUMMARY")
    print("=" * 70)
    
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
    
    # Analysis
    print("\n" + "=" * 70)
    print("🔍 ANALYSIS OF TEXT US FUNCTIONALITY")
    print("=" * 70)
    
    if failed == 0:
        print("✅ ALL TEXT US MESSAGING TESTS PASSED!")
        print("The 'Text Us' messaging functionality is working correctly:")
        print("  • Homeowner can login successfully")
        print("  • Provider exists and is accessible")
        print("  • Message threads can be created")
        print("  • Messages can be sent successfully")
        print("  • Messages can be retrieved correctly")
        print("  • Authentication tokens are working")
        print("  • Thread selection is functioning")
        return True
    else:
        print(f"❌ {failed} TEXT US MESSAGING TESTS FAILED!")
        print("Issues identified with 'Text Us' functionality:")
        
        for test_name, result in test_results:
            if not result:
                print(f"  • {test_name}: FAILED")
        
        print("\nPossible causes:")
        print("  • Authentication token issues")
        print("  • Thread selection problems")
        print("  • Message sending API failures")
        print("  • Provider ID not found")
        print("  • Database connectivity issues")
        return False

if __name__ == "__main__":
    success = run_text_us_tests()
    sys.exit(0 if success else 1)