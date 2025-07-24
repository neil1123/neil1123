#!/usr/bin/env python3
"""
Debug the workflow integration failure
"""

import requests
import json

# Backend URL from environment
BACKEND_URL = "https://5f81e1b3-88a9-45db-958d-9cb5f0ec9f5a.preview.emergentagent.com/api"

def debug_message_sending():
    """Debug the message sending issue in workflow"""
    print("🔍 Debugging Message Sending Issue...")
    
    # Login as homeowner
    homeowner_data = {
        "email": "test@homeowner.com",
        "password": "password123"
    }
    
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json=homeowner_data,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if response.status_code != 200:
        print("❌ Failed to login as homeowner")
        return
    
    homeowner_token = response.json()["access_token"]
    homeowner_id = response.json()["user"]["id"]
    
    # Login as provider
    provider_data = {
        "email": "test@provider.com",
        "password": "password123"
    }
    
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json=provider_data,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if response.status_code != 200:
        print("❌ Failed to login as provider")
        return
    
    provider_token = response.json()["access_token"]
    provider_id = response.json()["user"]["id"]
    
    # Create a message thread
    thread_data = {
        "homeowner_id": homeowner_id,
        "provider_id": provider_id,
        "homeowner_name": "Debug Test Homeowner",
        "provider_name": "Debug Test Provider",
        "order_type": "Debug Test",
        "last_message": "Debug message thread"
    }
    
    homeowner_headers = {"Authorization": f"Bearer {homeowner_token}"}
    response = requests.post(
        f"{BACKEND_URL}/messages/threads",
        json=thread_data,
        headers=homeowner_headers,
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to create thread: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    thread_id = response.json()["id"]
    print(f"✅ Thread created: {thread_id}")
    
    # Try to send a message
    message_data = {
        "thread_id": thread_id,
        "content": "Debug test message"
    }
    
    print(f"Sending message data: {json.dumps(message_data, indent=2)}")
    
    response = requests.post(
        f"{BACKEND_URL}/messages",
        json=message_data,
        headers=homeowner_headers,
        timeout=30
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response text: {response.text}")
    
    if response.status_code == 200:
        print("✅ Message sent successfully")
    else:
        print("❌ Message sending failed")
        
        # Try with different data structure
        print("\nTrying with explicit sender fields...")
        message_data_v2 = {
            "thread_id": thread_id,
            "sender_id": homeowner_id,
            "sender_type": "homeowner",
            "content": "Debug test message v2"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/messages",
            json=message_data_v2,
            headers=homeowner_headers,
            timeout=30
        )
        
        print(f"V2 Response status: {response.status_code}")
        print(f"V2 Response text: {response.text}")

if __name__ == "__main__":
    debug_message_sending()