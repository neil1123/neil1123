#!/usr/bin/env python3
"""
Doord Backend API Testing Script
Tests all backend endpoints for the home services marketplace
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

def test_provider_registration():
    """Test provider registration"""
    print("\n🔍 Testing Provider Registration...")
    global provider_token, provider_id
    
    try:
        test_data = {
            "email": f"provider_{uuid.uuid4().hex[:8]}@doordtest.com",
            "password": "testpass123",
            "user_type": "provider",
            "name": "John Smith",
            "phone": "+1-902-555-0123",
            "address": "123 Main St, Halifax, NS",
            "business_name": "Smith Home Services",
            "services": ["Plumbing", "Electrical"],
            "license": "NS-12345"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                provider_token = data["access_token"]
                provider_id = data["user"]["id"]
                print("✅ Provider registration successful")
                return True
            else:
                print(f"❌ Invalid response structure: {data}")
                return False
        else:
            print(f"❌ Provider registration failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Provider registration failed: {e}")
        return False

def test_homeowner_registration():
    """Test homeowner registration"""
    print("\n🔍 Testing Homeowner Registration...")
    global homeowner_token, homeowner_id
    
    try:
        test_data = {
            "email": f"homeowner_{uuid.uuid4().hex[:8]}@doordtest.com",
            "password": "testpass123",
            "user_type": "homeowner",
            "name": "Jane Doe",
            "phone": "+1-902-555-0456",
            "address": "456 Oak Ave, Halifax, NS"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data and "user" in data:
                homeowner_token = data["access_token"]
                homeowner_id = data["user"]["id"]
                print("✅ Homeowner registration successful")
                return True
            else:
                print(f"❌ Invalid response structure: {data}")
                return False
        else:
            print(f"❌ Homeowner registration failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Homeowner registration failed: {e}")
        return False

def test_provider_login():
    """Test provider login with existing credentials"""
    print("\n🔍 Testing Provider Login...")
    
    try:
        # First register a provider for login test
        test_email = f"logintest_{uuid.uuid4().hex[:8]}@doordtest.com"
        register_data = {
            "email": test_email,
            "password": "logintest123",
            "user_type": "provider",
            "name": "Login Test Provider",
            "business_name": "Test Services"
        }
        
        # Register
        register_response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if register_response.status_code != 200:
            print("❌ Failed to register test user for login")
            return False
        
        # Now test login
        login_data = {
            "email": test_email,
            "password": "logintest123"
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
                print("✅ Provider login successful")
                return True
            else:
                print(f"❌ Invalid login response structure: {data}")
                return False
        else:
            print(f"❌ Provider login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Provider login failed: {e}")
        return False

def test_jwt_validation():
    """Test JWT token validation"""
    print("\n🔍 Testing JWT Token Validation...")
    
    if not provider_token:
        print("❌ No provider token available for validation test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.get(
            f"{BACKEND_URL}/auth/me",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and "email" in data:
                print("✅ JWT token validation successful")
                return True
            else:
                print(f"❌ Invalid user data structure: {data}")
                return False
        else:
            print(f"❌ JWT validation failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ JWT validation failed: {e}")
        return False

def test_get_all_providers():
    """Test getting all providers"""
    print("\n🔍 Testing Get All Providers...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/providers", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ Providers retrieved successfully ({len(data)} providers)")
                return True
            else:
                print(f"❌ Expected list, got: {type(data)}")
                return False
        else:
            print(f"❌ Get providers failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Get providers failed: {e}")
        return False

def test_get_individual_provider():
    """Test getting individual provider"""
    print("\n🔍 Testing Get Individual Provider...")
    
    if not provider_id:
        print("❌ No provider ID available for individual provider test")
        return False
    
    try:
        response = requests.get(f"{BACKEND_URL}/providers/{provider_id}", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and "business_name" in data:
                print("✅ Individual provider retrieved successfully")
                return True
            else:
                print(f"❌ Invalid provider data structure: {data}")
                return False
        else:
            print(f"❌ Get individual provider failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Get individual provider failed: {e}")
        return False

def test_order_creation():
    """Test order creation"""
    print("\n🔍 Testing Order Creation...")
    global test_order_id
    
    if not homeowner_token or not provider_id or not homeowner_id:
        print("❌ Missing required data for order creation test")
        return False
    
    try:
        order_data = {
            "homeowner_id": homeowner_id,
            "provider_id": provider_id,
            "homeowner_name": "Jane Doe",
            "homeowner_email": "jane@doordtest.com",
            "homeowner_phone": "+1-902-555-0456",
            "homeowner_address": "456 Oak Ave, Halifax, NS",
            "provider_name": "Smith Home Services",
            "service_type": "Plumbing",
            "description": "Fix leaky kitchen faucet",
            "preferred_date": "2024-01-15",
            "preferred_time": "10:00 AM",
            "urgency": "medium",
            "budget": "$100-200"
        }
        
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.post(
            f"{BACKEND_URL}/orders",
            json=order_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and "service_type" in data:
                test_order_id = data["id"]
                print("✅ Order creation successful")
                return True
            else:
                print(f"❌ Invalid order response structure: {data}")
                return False
        else:
            print(f"❌ Order creation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Order creation failed: {e}")
        return False

def test_quotation_request():
    """Test quotation request creation"""
    print("\n🔍 Testing Quotation Request...")
    
    if not provider_id:
        print("❌ No provider ID available for quotation request test")
        return False
    
    try:
        quotation_data = {
            "homeowner_id": str(uuid.uuid4()),
            "provider_id": provider_id,
            "homeowner_name": "Test Customer",
            "homeowner_email": "customer@doordtest.com",
            "homeowner_phone": "+1-902-555-0789",
            "homeowner_address": "789 Pine St, Halifax, NS",
            "provider_name": "Smith Home Services",
            "service_type": "Electrical",
            "description": "Install new ceiling fan",
            "preferred_date": "2024-01-20",
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
                print("✅ Quotation request successful")
                return True
            else:
                print(f"❌ Invalid quotation response structure: {data}")
                return False
        else:
            print(f"❌ Quotation request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Quotation request failed: {e}")
        return False

def test_order_retrieval():
    """Test order retrieval for providers"""
    print("\n🔍 Testing Order Retrieval...")
    
    if not provider_token:
        print("❌ No provider token available for order retrieval test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.get(
            f"{BACKEND_URL}/orders",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ Orders retrieved successfully ({len(data)} orders)")
                return True
            else:
                print(f"❌ Expected list, got: {type(data)}")
                return False
        else:
            print(f"❌ Order retrieval failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Order retrieval failed: {e}")
        return False

def test_message_thread_creation():
    """Test message thread creation"""
    print("\n🔍 Testing Message Thread Creation...")
    global test_thread_id
    
    if not provider_token or not provider_id or not homeowner_id:
        print("❌ Missing required data for message thread creation test")
        return False
    
    try:
        thread_data = {
            "homeowner_id": homeowner_id,
            "provider_id": provider_id,
            "homeowner_name": "Jane Doe",
            "provider_name": "Smith Home Services",
            "order_type": "Plumbing",
            "last_message": "Initial message"
        }
        
        headers = {"Authorization": f"Bearer {provider_token}"}
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
                print("✅ Message thread creation successful")
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

def test_send_message():
    """Test sending messages"""
    print("\n🔍 Testing Send Message...")
    
    if not provider_token or not test_thread_id or not provider_id:
        print("❌ Missing required data for send message test")
        return False
    
    try:
        message_data = {
            "thread_id": test_thread_id,
            "sender_id": provider_id,  # Will be overridden by backend
            "sender_type": "provider",  # Will be overridden by backend
            "content": "Hello, I can help you with your plumbing needs!"
        }
        
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.post(
            f"{BACKEND_URL}/messages",
            json=message_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and "content" in data:
                print("✅ Message sending successful")
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

def test_appointment_creation():
    """Test appointment creation"""
    print("\n🔍 Testing Appointment Creation...")
    
    if not provider_token or not provider_id:
        print("❌ No provider token available for appointment creation test")
        return False
    
    try:
        appointment_data = {
            "provider_id": provider_id,  # Will be overridden by backend
            "customer_name": "Test Customer",
            "phone_number": "+1-902-555-0999",
            "service_type": "Plumbing",
            "date": "2024-01-25",
            "time": "2:00 PM",
            "address": "999 Test St, Halifax, NS",
            "notes": "Test appointment"
        }
        
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.post(
            f"{BACKEND_URL}/appointments",
            json=appointment_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "id" in data and "customer_name" in data:
                print("✅ Appointment creation successful")
                return True
            else:
                print(f"❌ Invalid appointment response structure: {data}")
                return False
        else:
            print(f"❌ Appointment creation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Appointment creation failed: {e}")
        return False

def test_update_order_quotation():
    """Test updating order quotation (PUT /api/orders/{order_id}/quotation)"""
    print("\n🔍 Testing Update Order Quotation...")
    
    if not provider_token or not test_order_id:
        print("❌ Missing required data for quotation update test")
        return False
    
    try:
        # Test updating quotation with amount and details
        headers = {"Authorization": f"Bearer {provider_token}"}
        params = {
            "quotation_amount": 150.00,
            "quotation_details": "Complete plumbing repair including parts and labor"
        }
        
        response = requests.put(
            f"{BACKEND_URL}/orders/{test_order_id}/quotation",
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "quotation updated" in data["message"].lower():
                print("✅ Order quotation update successful")
                return True
            else:
                print(f"❌ Invalid quotation update response: {data}")
                return False
        else:
            print(f"❌ Order quotation update failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Order quotation update failed: {e}")
        return False

def test_provider_order_status_update():
    """Test provider updating order status"""
    print("\n🔍 Testing Provider Order Status Update...")
    
    if not provider_token or not test_order_id:
        print("❌ Missing required data for provider status update test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        params = {"status": "quoted"}
        
        response = requests.put(
            f"{BACKEND_URL}/orders/{test_order_id}/status",
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "status updated" in data["message"].lower():
                print("✅ Provider order status update successful")
                return True
            else:
                print(f"❌ Invalid status update response: {data}")
                return False
        else:
            print(f"❌ Provider order status update failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Provider order status update failed: {e}")
        return False

def test_homeowner_order_status_update():
    """Test homeowner updating order status (accept/decline)"""
    print("\n🔍 Testing Homeowner Order Status Update...")
    
    if not homeowner_token or not test_order_id:
        print("❌ Missing required data for homeowner status update test")
        return False
    
    try:
        # Test homeowner accepting quote
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        params = {"status": "accepted"}
        
        response = requests.put(
            f"{BACKEND_URL}/orders/{test_order_id}/status",
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "status updated" in data["message"].lower():
                print("✅ Homeowner order status update (accept) successful")
                
                # Test homeowner declining quote
                params = {"status": "declined"}
                response = requests.put(
                    f"{BACKEND_URL}/orders/{test_order_id}/status",
                    params=params,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print("✅ Homeowner order status update (decline) successful")
                    return True
                else:
                    print(f"❌ Homeowner decline failed with status {response.status_code}")
                    return False
            else:
                print(f"❌ Invalid homeowner status update response: {data}")
                return False
        else:
            print(f"❌ Homeowner order status update failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Homeowner order status update failed: {e}")
        return False

def test_get_message_threads():
    """Test getting message threads"""
    print("\n🔍 Testing Get Message Threads...")
    
    if not provider_token:
        print("❌ No provider token available for message threads test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.get(
            f"{BACKEND_URL}/messages/threads",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ Message threads retrieved successfully ({len(data)} threads)")
                return True
            else:
                print(f"❌ Expected list, got: {type(data)}")
                return False
        else:
            print(f"❌ Get message threads failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Get message threads failed: {e}")
        return False

def test_get_messages_for_thread():
    """Test getting messages for a specific thread"""
    print("\n🔍 Testing Get Messages for Thread...")
    
    if not provider_token or not test_thread_id:
        print("❌ Missing required data for get messages test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.get(
            f"{BACKEND_URL}/messages/{test_thread_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ Messages for thread retrieved successfully ({len(data)} messages)")
                return True
            else:
                print(f"❌ Expected list, got: {type(data)}")
                return False
        else:
            print(f"❌ Get messages for thread failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Get messages for thread failed: {e}")
        return False

def test_error_handling():
    """Test error handling scenarios"""
    print("\n🔍 Testing Error Handling...")
    
    if not provider_token:
        print("❌ No provider token available for error handling test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        
        # Test 1: Invalid order ID for quotation update
        invalid_order_id = "invalid-order-id"
        params = {"quotation_amount": 100.00}
        
        response = requests.put(
            f"{BACKEND_URL}/orders/{invalid_order_id}/quotation",
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 404:
            print("✅ Invalid order ID properly handled (404)")
        else:
            print(f"❌ Expected 404 for invalid order ID, got {response.status_code}")
            return False
        
        # Test 2: Unauthorized access (no token)
        response = requests.get(f"{BACKEND_URL}/orders", timeout=30)
        
        if response.status_code == 403:
            print("✅ Unauthorized access properly handled (403)")
        else:
            print(f"❌ Expected 403 for unauthorized access, got {response.status_code}")
            return False
        
        # Test 3: Invalid JWT token
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        response = requests.get(
            f"{BACKEND_URL}/orders",
            headers=invalid_headers,
            timeout=30
        )
        
        if response.status_code == 401:
            print("✅ Invalid JWT token properly handled (401)")
        else:
            print(f"❌ Expected 401 for invalid token, got {response.status_code}")
            return False
        
        # Test 4: Homeowner trying invalid status update
        if homeowner_token:
            homeowner_headers = {"Authorization": f"Bearer {homeowner_token}"}
            params = {"status": "in_progress"}  # Invalid status for homeowner
            
            response = requests.put(
                f"{BACKEND_URL}/orders/{test_order_id}/status",
                params=params,
                headers=homeowner_headers,
                timeout=30
            )
            
            if response.status_code == 400:
                print("✅ Invalid homeowner status update properly handled (400)")
            else:
                print(f"❌ Expected 400 for invalid homeowner status, got {response.status_code}")
                return False
        
        print("✅ All error handling tests passed")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_mongodb_persistence():
    """Test MongoDB data persistence"""
    print("\n🔍 Testing MongoDB Data Persistence...")
    
    # Test by retrieving previously created data
    if not provider_token:
        print("❌ No provider token available for persistence test")
        return False
    
    try:
        # Get providers to check if our registered provider persists
        response = requests.get(f"{BACKEND_URL}/providers", timeout=30)
        
        if response.status_code == 200:
            providers = response.json()
            if any(p.get("id") == provider_id for p in providers):
                print("✅ MongoDB data persistence verified")
                return True
            else:
                print("❌ Registered provider not found in database")
                return False
        else:
            print(f"❌ Failed to verify persistence with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ MongoDB persistence test failed: {e}")
        return False

def test_quotation_workflow_complete():
    """Test complete quotation workflow as requested in review"""
    print("\n🔍 Testing Complete Quotation Workflow...")
    
    if not provider_token or not homeowner_token:
        print("❌ Missing tokens for complete quotation workflow test")
        return False
    
    try:
        # Step 1: Create a quotation request (POST /api/quotations)
        quotation_data = {
            "homeowner_id": homeowner_id,
            "provider_id": provider_id,
            "homeowner_name": "Sarah Johnson",
            "homeowner_email": "sarah@doordtest.com",
            "homeowner_phone": "+1-902-555-1234",
            "homeowner_address": "123 Elm St, Halifax, NS",
            "provider_name": "Smith Home Services",
            "service_type": "Kitchen Renovation",
            "description": "Complete kitchen renovation including cabinets, countertops, and appliances",
            "preferred_date": "2024-02-15",
            "budget": "$15000-20000",
            "urgency": "medium"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/quotations",
            json=quotation_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Quotation request creation failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        quotation_response = response.json()
        workflow_order_id = quotation_response.get("order_id")
        
        if not workflow_order_id:
            print("❌ No order_id returned from quotation request")
            return False
        
        print("✅ Step 1: Quotation request created successfully")
        
        # Step 2: Verify order is created with "pending_quotation" status
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.get(
            f"{BACKEND_URL}/orders/{workflow_order_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to retrieve created order with status {response.status_code}")
            return False
        
        order_data = response.json()
        if order_data.get("status") != "pending_quotation":
            print(f"❌ Expected 'pending_quotation' status, got '{order_data.get('status')}'")
            return False
        
        print("✅ Step 2: Order created with 'pending_quotation' status")
        
        # Step 3: Update the order quotation (PUT /api/orders/{order_id}/quotation)
        params = {
            "quotation_amount": 18500.00,
            "quotation_details": "Complete kitchen renovation package including premium materials, professional installation, and 2-year warranty"
        }
        
        response = requests.put(
            f"{BACKEND_URL}/orders/{workflow_order_id}/quotation",
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Quotation update failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        update_response = response.json()
        if "quotation updated" not in update_response.get("message", "").lower():
            print(f"❌ Unexpected quotation update response: {update_response}")
            return False
        
        print("✅ Step 3: Quotation amount updated successfully")
        
        # Step 4: Verify order status changed to "quoted"
        response = requests.get(
            f"{BACKEND_URL}/orders/{workflow_order_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to retrieve updated order with status {response.status_code}")
            return False
        
        updated_order = response.json()
        if updated_order.get("status") != "quoted":
            print(f"❌ Expected 'quoted' status after update, got '{updated_order.get('status')}'")
            return False
        
        if updated_order.get("quotation_amount") != 18500.00:
            print(f"❌ Expected quotation amount 18500.00, got {updated_order.get('quotation_amount')}")
            return False
        
        print("✅ Step 4: Order status changed to 'quoted' with correct amount")
        
        # Step 5: Test homeowner can accept/decline the quote
        homeowner_headers = {"Authorization": f"Bearer {homeowner_token}"}
        
        # Test accept
        params = {"status": "accepted"}
        response = requests.put(
            f"{BACKEND_URL}/orders/{workflow_order_id}/status",
            params=params,
            headers=homeowner_headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Homeowner quote acceptance failed with status {response.status_code}")
            return False
        
        print("✅ Step 5: Homeowner can accept quotes")
        
        # Test decline
        params = {"status": "declined"}
        response = requests.put(
            f"{BACKEND_URL}/orders/{workflow_order_id}/status",
            params=params,
            headers=homeowner_headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Homeowner quote decline failed with status {response.status_code}")
            return False
        
        print("✅ Step 6: Homeowner can decline quotes")
        
        print("✅ COMPLETE QUOTATION WORKFLOW TEST PASSED")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Complete quotation workflow test failed: {e}")
        return False

def test_quotation_error_scenarios():
    """Test error handling for quotation update endpoint"""
    print("\n🔍 Testing Quotation Update Error Scenarios...")
    
    if not provider_token:
        print("❌ No provider token available for error scenario testing")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        
        # Test 1: Invalid order ID
        invalid_order_id = "non-existent-order-id"
        params = {"quotation_amount": 100.00}
        
        response = requests.put(
            f"{BACKEND_URL}/orders/{invalid_order_id}/quotation",
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 404:
            print(f"❌ Expected 404 for invalid order ID, got {response.status_code}")
            return False
        
        print("✅ Invalid order ID properly handled (404)")
        
        # Test 2: Unauthorized access (no token)
        response = requests.put(
            f"{BACKEND_URL}/orders/{test_order_id}/quotation",
            params=params,
            timeout=30
        )
        
        if response.status_code != 403:
            print(f"❌ Expected 403 for no authentication, got {response.status_code}")
            return False
        
        print("✅ No authentication properly handled (403)")
        
        # Test 3: Invalid JWT token
        invalid_headers = {"Authorization": "Bearer invalid-jwt-token"}
        response = requests.put(
            f"{BACKEND_URL}/orders/{test_order_id}/quotation",
            params=params,
            headers=invalid_headers,
            timeout=30
        )
        
        if response.status_code != 401:
            print(f"❌ Expected 401 for invalid token, got {response.status_code}")
            return False
        
        print("✅ Invalid JWT token properly handled (401)")
        
        # Test 4: Homeowner trying to update quotation (should fail)
        if homeowner_token:
            homeowner_headers = {"Authorization": f"Bearer {homeowner_token}"}
            response = requests.put(
                f"{BACKEND_URL}/orders/{test_order_id}/quotation",
                params=params,
                headers=homeowner_headers,
                timeout=30
            )
            
            if response.status_code != 403:
                print(f"❌ Expected 403 for homeowner quotation update, got {response.status_code}")
                return False
            
            print("✅ Homeowner quotation update properly blocked (403)")
        
        # Test 5: Invalid quotation amount (negative)
        params = {"quotation_amount": -100.00}
        response = requests.put(
            f"{BACKEND_URL}/orders/{test_order_id}/quotation",
            params=params,
            headers=headers,
            timeout=30
        )
        
        # Note: Backend might accept negative values, but let's check the response
        print(f"ℹ️ Negative amount test returned status {response.status_code}")
        
        print("✅ All quotation error scenarios tested")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Quotation error scenarios test failed: {e}")
        return False

def test_review_system_homeowner_submit_review():
    """Test homeowner submitting a review for a provider after completing an order"""
    print("\n🔍 Testing Review System - Homeowner Submit Review...")
    
    if not homeowner_token or not provider_id:
        print("❌ Missing homeowner token or provider ID for review test")
        return False
    
    try:
        # First, create a completed order for the homeowner to review
        order_data = {
            "homeowner_id": homeowner_id,
            "provider_id": provider_id,
            "homeowner_name": "Test Homeowner",
            "homeowner_email": "test@homeowner.com",
            "homeowner_phone": "+1-902-555-0001",
            "homeowner_address": "123 Test St, Halifax, NS",
            "provider_name": "Test Provider",
            "service_type": "Home Cleaning",
            "description": "Regular house cleaning service"
        }
        
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.post(
            f"{BACKEND_URL}/orders",
            json=order_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to create test order for review: {response.status_code}")
            return False
        
        test_order = response.json()
        test_order_id = test_order["id"]
        
        # Update order status to completed (as provider)
        provider_headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.put(
            f"{BACKEND_URL}/orders/{test_order_id}/status?status=completed",
            headers=provider_headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to mark order as completed: {response.status_code}")
            return False
        
        print("✅ Test order created and marked as completed")
        
        # Now submit a review
        review_data = {
            "provider_id": provider_id,
            "rating": 5,
            "review_text": "Excellent service! Very professional and thorough cleaning.",
            "order_id": test_order_id
        }
        
        response = requests.post(
            f"{BACKEND_URL}/reviews",
            json=review_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Review submission failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        review_response = response.json()
        
        # Verify review data
        if (review_response.get("provider_id") != provider_id or
            review_response.get("rating") != 5 or
            review_response.get("homeowner_id") != homeowner_id):
            print(f"❌ Review data mismatch: {review_response}")
            return False
        
        print("✅ Review submitted successfully")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Review submission test failed: {e}")
        return False

def test_review_system_get_provider_reviews():
    """Test fetching reviews for a provider"""
    print("\n🔍 Testing Review System - Get Provider Reviews...")
    
    if not provider_id:
        print("❌ Missing provider ID for review retrieval test")
        return False
    
    try:
        # Get reviews for the provider (no authentication required)
        response = requests.get(
            f"{BACKEND_URL}/providers/{provider_id}/reviews",
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get provider reviews with status {response.status_code}")
            return False
        
        reviews = response.json()
        
        # Should be a list
        if not isinstance(reviews, list):
            print(f"❌ Expected list of reviews, got: {type(reviews)}")
            return False
        
        # If we have reviews, verify structure
        if reviews:
            review = reviews[0]
            required_fields = ["id", "homeowner_id", "provider_id", "rating", "review_text", "created_at"]
            for field in required_fields:
                if field not in review:
                    print(f"❌ Missing required field '{field}' in review")
                    return False
            
            # Verify rating is between 1-5
            if not (1 <= review["rating"] <= 5):
                print(f"❌ Invalid rating value: {review['rating']}")
                return False
        
        print(f"✅ Retrieved {len(reviews)} reviews for provider")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Get provider reviews test failed: {e}")
        return False

def test_review_system_validation_rules():
    """Test review system validation rules"""
    print("\n🔍 Testing Review System - Validation Rules...")
    
    if not homeowner_token or not provider_id:
        print("❌ Missing tokens for review validation test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        
        # Test 1: Provider trying to submit review (should fail)
        if provider_token:
            provider_headers = {"Authorization": f"Bearer {provider_token}"}
            review_data = {
                "provider_id": provider_id,
                "rating": 4,
                "review_text": "Good service"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/reviews",
                json=review_data,
                headers=provider_headers,
                timeout=30
            )
            
            if response.status_code != 403:
                print(f"❌ Expected 403 for provider review submission, got {response.status_code}")
                return False
            
            print("✅ Provider review submission properly blocked (403)")
        
        # Test 2: Homeowner reviewing without completed order (should fail)
        # Create a new provider for this test
        new_provider_data = {
            "email": f"testprovider{uuid.uuid4().hex[:8]}@doordtest.com",
            "password": "password123",
            "user_type": "provider",
            "name": "Test Provider 2",
            "business_name": "Test Services 2",
            "services": ["Plumbing"]
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json=new_provider_data,
            timeout=30
        )
        
        if response.status_code == 200:
            new_provider = response.json()
            new_provider_id = new_provider["user"]["id"]
            
            # Try to review without completed order
            review_data = {
                "provider_id": new_provider_id,
                "rating": 3,
                "review_text": "Test review without order"
            }
            
            response = requests.post(
                f"{BACKEND_URL}/reviews",
                json=review_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code != 400:
                print(f"❌ Expected 400 for review without completed order, got {response.status_code}")
                return False
            
            print("✅ Review without completed order properly blocked (400)")
        
        # Test 3: Invalid rating values
        review_data = {
            "provider_id": provider_id,
            "rating": 6,  # Invalid rating > 5
            "review_text": "Test review with invalid rating"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/reviews",
            json=review_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code not in [400, 422]:
            print(f"❌ Expected 400/422 for invalid rating, got {response.status_code}")
            return False
        
        print("✅ Invalid rating properly rejected")
        
        # Test 4: Duplicate review (should fail)
        # Try to submit another review for the same provider
        review_data = {
            "provider_id": provider_id,
            "rating": 4,
            "review_text": "Another review for same provider"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/reviews",
            json=review_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 400:
            print(f"❌ Expected 400 for duplicate review, got {response.status_code}")
            return False
        
        print("✅ Duplicate review properly blocked (400)")
        
        print("✅ All review validation rules working correctly")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Review validation test failed: {e}")
        return False

def test_review_system_provider_rating_update():
    """Test that provider rating is updated when reviews are submitted"""
    print("\n🔍 Testing Review System - Provider Rating Update...")
    
    if not provider_id:
        print("❌ Missing provider ID for rating update test")
        return False
    
    try:
        # Get provider's current rating
        response = requests.get(
            f"{BACKEND_URL}/providers/{provider_id}",
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get provider data: {response.status_code}")
            return False
        
        provider_data = response.json()
        initial_rating = provider_data.get("rating", 0)
        initial_review_count = provider_data.get("reviews", 0)
        
        print(f"ℹ️ Initial rating: {initial_rating}, review count: {initial_review_count}")
        
        # Create a new homeowner for this test
        new_homeowner_data = {
            "email": f"testhomeowner{uuid.uuid4().hex[:8]}@doordtest.com",
            "password": "password123",
            "user_type": "homeowner",
            "name": "Test Homeowner 2"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/register",
            json=new_homeowner_data,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to create test homeowner: {response.status_code}")
            return False
        
        new_homeowner = response.json()
        new_homeowner_id = new_homeowner["user"]["id"]
        new_homeowner_token = new_homeowner["access_token"]
        
        # Create and complete an order
        order_data = {
            "homeowner_id": new_homeowner_id,
            "provider_id": provider_id,
            "homeowner_name": "Test Homeowner 2",
            "homeowner_email": new_homeowner_data["email"],
            "homeowner_phone": "+1-902-555-0002",
            "homeowner_address": "456 Test Ave, Halifax, NS",
            "provider_name": "Test Provider",
            "service_type": "Electrical Work",
            "description": "Electrical outlet installation"
        }
        
        headers = {"Authorization": f"Bearer {new_homeowner_token}"}
        response = requests.post(
            f"{BACKEND_URL}/orders",
            json=order_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to create test order: {response.status_code}")
            return False
        
        test_order = response.json()
        test_order_id = test_order["id"]
        
        # Complete the order (as provider)
        provider_headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.put(
            f"{BACKEND_URL}/orders/{test_order_id}/status?status=completed",
            headers=provider_headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to complete order: {response.status_code}")
            return False
        
        # Submit a review with rating 4
        review_data = {
            "provider_id": provider_id,
            "rating": 4,
            "review_text": "Good electrical work, professional service.",
            "order_id": test_order_id
        }
        
        response = requests.post(
            f"{BACKEND_URL}/reviews",
            json=review_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to submit review: {response.status_code}")
            return False
        
        print("✅ Review submitted successfully")
        
        # Check if provider rating was updated
        response = requests.get(
            f"{BACKEND_URL}/providers/{provider_id}",
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get updated provider data: {response.status_code}")
            return False
        
        updated_provider_data = response.json()
        updated_rating = updated_provider_data.get("rating", 0)
        updated_review_count = updated_provider_data.get("reviews", 0)
        
        print(f"ℹ️ Updated rating: {updated_rating}, review count: {updated_review_count}")
        
        # Verify review count increased
        if updated_review_count <= initial_review_count:
            print(f"❌ Review count did not increase: {initial_review_count} -> {updated_review_count}")
            return False
        
        # Verify rating is reasonable (should be average of all ratings)
        if updated_rating < 1 or updated_rating > 5:
            print(f"❌ Invalid updated rating: {updated_rating}")
            return False
        
        print("✅ Provider rating and review count updated correctly")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Provider rating update test failed: {e}")
        return False

def test_analytics_data_orders():
    """Test that orders endpoint returns proper data for analytics calculations"""
    print("\n🔍 Testing Analytics Data - Orders Endpoint...")
    
    if not provider_token:
        print("❌ Missing provider token for analytics test")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.get(
            f"{BACKEND_URL}/orders",
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get orders for analytics: {response.status_code}")
            return False
        
        orders = response.json()
        
        if not isinstance(orders, list):
            print(f"❌ Expected list of orders, got: {type(orders)}")
            return False
        
        # Verify order structure for analytics
        analytics_fields = ["id", "status", "quotation_amount", "request_date", "service_type"]
        status_counts = {"completed": 0, "in_progress": 0, "accepted": 0}
        total_revenue = 0
        
        for order in orders:
            # Check required fields for analytics
            for field in analytics_fields:
                if field not in order:
                    print(f"❌ Missing analytics field '{field}' in order")
                    return False
            
            # Count orders by status
            order_status = order.get("status", "")
            if order_status in status_counts:
                status_counts[order_status] += 1
            
            # Calculate revenue from completed orders
            if order_status == "completed" and order.get("quotation_amount"):
                total_revenue += float(order["quotation_amount"])
        
        print(f"✅ Orders analytics data verified:")
        print(f"   - Total orders: {len(orders)}")
        print(f"   - Completed: {status_counts['completed']}")
        print(f"   - In Progress: {status_counts['in_progress']}")
        print(f"   - Accepted: {status_counts['accepted']}")
        print(f"   - Total Revenue: ${total_revenue:.2f}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Analytics data test failed: {e}")
        return False

def run_all_tests():
    """Run all backend tests"""
    print("=" * 70)
    print("🚀 DOORD BACKEND API TESTING STARTED")
    print("=" * 70)
    
    test_results = []
    
    # Test 1: Backend Health
    test_results.append(("Backend Health", test_backend_health()))
    
    # Test 2: Provider Registration
    test_results.append(("Provider Registration", test_provider_registration()))
    
    # Test 3: Homeowner Registration
    test_results.append(("Homeowner Registration", test_homeowner_registration()))
    
    # Test 4: Provider Login
    test_results.append(("Provider Login", test_provider_login()))
    
    # Test 5: JWT Token Validation
    test_results.append(("JWT Token Validation", test_jwt_validation()))
    
    # Test 6: Get All Providers
    test_results.append(("Get All Providers", test_get_all_providers()))
    
    # Test 7: Get Individual Provider
    test_results.append(("Get Individual Provider", test_get_individual_provider()))
    
    # Test 8: Order Creation
    test_results.append(("Order Creation", test_order_creation()))
    
    # Test 9: Quotation Request
    test_results.append(("Quotation Request", test_quotation_request()))
    
    # Test 10: Order Retrieval
    test_results.append(("Order Retrieval", test_order_retrieval()))
    
    # Test 11: Message Thread Creation
    test_results.append(("Message Thread Creation", test_message_thread_creation()))
    
    # Test 12: Send Message
    test_results.append(("Send Message", test_send_message()))
    
    # Test 13: Appointment Creation
    test_results.append(("Appointment Creation", test_appointment_creation()))
    
    # Test 14: Update Order Quotation
    test_results.append(("Update Order Quotation", test_update_order_quotation()))
    
    # Test 15: Provider Order Status Update
    test_results.append(("Provider Order Status Update", test_provider_order_status_update()))
    
    # Test 16: Homeowner Order Status Update
    test_results.append(("Homeowner Order Status Update", test_homeowner_order_status_update()))
    
    # Test 17: Get Message Threads
    test_results.append(("Get Message Threads", test_get_message_threads()))
    
    # Test 18: Get Messages for Thread
    test_results.append(("Get Messages for Thread", test_get_messages_for_thread()))
    
    # Test 19: Error Handling
    test_results.append(("Error Handling", test_error_handling()))
    
    # Test 20: MongoDB Persistence
    test_results.append(("MongoDB Persistence", test_mongodb_persistence()))
    
    # FOCUSED TESTS FOR QUOTATION UPDATE FUNCTIONALITY
    print("\n" + "=" * 70)
    print("🎯 FOCUSED QUOTATION UPDATE TESTING")
    print("=" * 70)
    
    # Test 21: Complete Quotation Workflow
    test_results.append(("Complete Quotation Workflow", test_quotation_workflow_complete()))
    
    # Test 22: Quotation Error Scenarios
    test_results.append(("Quotation Error Scenarios", test_quotation_error_scenarios()))
    
    # NEW REVIEW SYSTEM TESTS
    print("\n" + "=" * 70)
    print("🌟 REVIEW SYSTEM TESTING")
    print("=" * 70)
    
    # Test 23: Review System - Homeowner Submit Review
    test_results.append(("Review System - Submit Review", test_review_system_homeowner_submit_review()))
    
    # Test 24: Review System - Get Provider Reviews
    test_results.append(("Review System - Get Reviews", test_review_system_get_provider_reviews()))
    
    # Test 25: Review System - Validation Rules
    test_results.append(("Review System - Validation", test_review_system_validation_rules()))
    
    # Test 26: Review System - Provider Rating Update
    test_results.append(("Review System - Rating Update", test_review_system_provider_rating_update()))
    
    # Test 27: Analytics Data - Orders
    test_results.append(("Analytics Data - Orders", test_analytics_data_orders()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
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
        print("\n🎉 ALL BACKEND TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️ {failed} BACKEND TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)