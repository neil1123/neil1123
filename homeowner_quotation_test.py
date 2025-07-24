#!/usr/bin/env python3
"""
Homeowner Quotation System Testing Script
Tests specific homeowner quotation functionality as requested
"""

import requests
import json
import uuid
from datetime import datetime

# Load environment variables
BACKEND_URL = "https://5f81e1b3-88a9-45db-958d-9cb5f0ec9f5a.preview.emergentagent.com/api"

# Global variables to store test data
homeowner_token = None
provider_token = None
homeowner_id = None
provider_id = None
test_order_id = None

def setup_test_users():
    """Setup test homeowner and provider for quotation testing"""
    print("🔧 Setting up test users...")
    global homeowner_token, provider_token, homeowner_id, provider_id
    
    # Register homeowner
    homeowner_data = {
        "email": f"homeowner_{uuid.uuid4().hex[:8]}@quotationtest.com",
        "password": "testpass123",
        "user_type": "homeowner",
        "name": "Sarah Johnson",
        "phone": "+1-902-555-1234",
        "address": "123 Maple Street, Halifax, NS"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/register", json=homeowner_data, timeout=30)
    if response.status_code == 200:
        data = response.json()
        homeowner_token = data["access_token"]
        homeowner_id = data["user"]["id"]
        print("✅ Homeowner registered successfully")
    else:
        print(f"❌ Homeowner registration failed: {response.text}")
        return False
    
    # Register provider
    provider_data = {
        "email": f"provider_{uuid.uuid4().hex[:8]}@quotationtest.com",
        "password": "testpass123",
        "user_type": "provider",
        "name": "Mike Wilson",
        "phone": "+1-902-555-5678",
        "address": "456 Oak Avenue, Halifax, NS",
        "business_name": "Wilson Home Services",
        "services": ["Plumbing", "Electrical", "HVAC"],
        "license": "NS-67890"
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/register", json=provider_data, timeout=30)
    if response.status_code == 200:
        data = response.json()
        provider_token = data["access_token"]
        provider_id = data["user"]["id"]
        print("✅ Provider registered successfully")
        return True
    else:
        print(f"❌ Provider registration failed: {response.text}")
        return False

def test_quotation_request_workflow():
    """Test complete quotation request workflow"""
    print("\n🔍 Testing Quotation Request Workflow...")
    global test_order_id
    
    try:
        quotation_data = {
            "homeowner_id": homeowner_id,
            "provider_id": provider_id,
            "homeowner_name": "Sarah Johnson",
            "homeowner_email": "sarah@quotationtest.com",
            "homeowner_phone": "+1-902-555-1234",
            "homeowner_address": "123 Maple Street, Halifax, NS",
            "provider_name": "Wilson Home Services",
            "service_type": "Plumbing",
            "description": "Need to fix a leaking bathroom faucet and replace kitchen sink",
            "preferred_date": "2024-01-20",
            "preferred_time": "10:00 AM",
            "urgency": "medium",
            "budget": "$200-400",
            "property_size": "2 bedroom apartment",
            "additional_requirements": "Please call before arriving"
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
                print("✅ Quotation request workflow successful")
                print(f"   Created order ID: {test_order_id}")
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

def test_homeowner_order_retrieval():
    """Test homeowner can retrieve their own orders"""
    print("\n🔍 Testing Homeowner Order Retrieval...")
    
    if not homeowner_token:
        print("❌ No homeowner token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.get(
            f"{BACKEND_URL}/orders",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            orders = response.json()
            if isinstance(orders, list):
                # Check if our test order is in the list
                homeowner_orders = [order for order in orders if order.get("homeowner_id") == homeowner_id]
                if len(homeowner_orders) > 0:
                    print(f"✅ Homeowner order retrieval successful ({len(homeowner_orders)} orders found)")
                    
                    # Verify homeowner only sees their own orders
                    all_homeowner_ids = [order.get("homeowner_id") for order in orders]
                    if all(hid == homeowner_id for hid in all_homeowner_ids):
                        print("✅ Access control verified - homeowner only sees own orders")
                        return True
                    else:
                        print("❌ Access control failed - homeowner can see other orders")
                        return False
                else:
                    print("❌ No orders found for homeowner")
                    return False
            else:
                print(f"❌ Expected list, got: {type(orders)}")
                return False
        else:
            print(f"❌ Order retrieval failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Order retrieval failed: {e}")
        return False

def test_homeowner_order_filtering():
    """Test homeowner order filtering by email"""
    print("\n🔍 Testing Homeowner Order Filtering...")
    
    if not homeowner_token:
        print("❌ No homeowner token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.get(
            f"{BACKEND_URL}/orders",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            orders = response.json()
            if isinstance(orders, list) and len(orders) > 0:
                # Check if orders are properly filtered by homeowner
                for order in orders:
                    if order.get("homeowner_id") != homeowner_id:
                        print(f"❌ Found order with wrong homeowner_id: {order.get('homeowner_id')}")
                        return False
                
                print("✅ Order filtering working correctly")
                return True
            else:
                print("❌ No orders found to test filtering")
                return False
        else:
            print(f"❌ Order filtering test failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Order filtering test failed: {e}")
        return False

def test_homeowner_status_update():
    """Test homeowner can update order status (accept/decline quotes)"""
    print("\n🔍 Testing Homeowner Order Status Update...")
    
    if not homeowner_token or not test_order_id:
        print("❌ Missing homeowner token or test order ID")
        return False
    
    try:
        # Test accepting a quote
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        
        # Try to update status to "accepted"
        response = requests.put(
            f"{BACKEND_URL}/orders/{test_order_id}/status?status=accepted",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Homeowner can update order status")
            return True
        elif response.status_code == 403:
            print("❌ CRITICAL ISSUE: Homeowners cannot update order status (403 Forbidden)")
            print("   This prevents homeowners from accepting/declining quotes!")
            return False
        else:
            print(f"❌ Status update failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Status update failed: {e}")
        return False

def test_homeowner_individual_order():
    """Test homeowner can retrieve individual order details"""
    print("\n🔍 Testing Homeowner Individual Order Retrieval...")
    
    if not homeowner_token or not test_order_id:
        print("❌ Missing homeowner token or test order ID")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.get(
            f"{BACKEND_URL}/orders/{test_order_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            order = response.json()
            if "id" in order and order["id"] == test_order_id:
                print("✅ Homeowner can retrieve individual order details")
                return True
            else:
                print(f"❌ Invalid order data: {order}")
                return False
        else:
            print(f"❌ Individual order retrieval failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Individual order retrieval failed: {e}")
        return False

def test_order_data_structure():
    """Test order data structure matches frontend expectations"""
    print("\n🔍 Testing Order Data Structure...")
    
    if not homeowner_token:
        print("❌ No homeowner token available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.get(
            f"{BACKEND_URL}/orders",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            orders = response.json()
            if isinstance(orders, list) and len(orders) > 0:
                order = orders[0]
                
                # Check required fields for HomeownerQuotations.jsx
                required_fields = [
                    "id", "service_type", "description", "status", 
                    "provider_name", "homeowner_name", "request_date",
                    "preferred_date", "budget"
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in order:
                        missing_fields.append(field)
                
                if not missing_fields:
                    print("✅ Order data structure matches frontend expectations")
                    return True
                else:
                    print(f"❌ Missing required fields: {missing_fields}")
                    return False
            else:
                print("❌ No orders found to test data structure")
                return False
        else:
            print(f"❌ Data structure test failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Data structure test failed: {e}")
        return False

def test_provider_quote_workflow():
    """Test provider can provide quotes on orders"""
    print("\n🔍 Testing Provider Quote Workflow...")
    
    if not provider_token or not test_order_id:
        print("❌ Missing provider token or test order ID")
        return False
    
    try:
        # Provider updates order with quotation
        headers = {"Authorization": f"Bearer {provider_token}"}
        
        response = requests.put(
            f"{BACKEND_URL}/orders/{test_order_id}/status?status=quoted",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Provider can update order status to 'quoted'")
            return True
        else:
            print(f"❌ Provider quote workflow failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Provider quote workflow failed: {e}")
        return False

def run_homeowner_quotation_tests():
    """Run all homeowner quotation system tests"""
    print("=" * 80)
    print("🏠 HOMEOWNER QUOTATION SYSTEM TESTING STARTED")
    print("=" * 80)
    
    # Setup test users first
    if not setup_test_users():
        print("❌ Failed to setup test users")
        return False
    
    test_results = []
    
    # Test 1: Quotation Request Workflow
    test_results.append(("Quotation Request Workflow", test_quotation_request_workflow()))
    
    # Test 2: Homeowner Order Retrieval
    test_results.append(("Homeowner Order Retrieval", test_homeowner_order_retrieval()))
    
    # Test 3: Homeowner Order Filtering
    test_results.append(("Homeowner Order Filtering", test_homeowner_order_filtering()))
    
    # Test 4: Homeowner Individual Order Retrieval
    test_results.append(("Homeowner Individual Order", test_homeowner_individual_order()))
    
    # Test 5: Order Data Structure
    test_results.append(("Order Data Structure", test_order_data_structure()))
    
    # Test 6: Provider Quote Workflow
    test_results.append(("Provider Quote Workflow", test_provider_quote_workflow()))
    
    # Test 7: Homeowner Status Update (Critical Test)
    test_results.append(("Homeowner Status Update", test_homeowner_status_update()))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 HOMEOWNER QUOTATION TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    failed = 0
    critical_issues = []
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<35} {status}")
        if result:
            passed += 1
        else:
            failed += 1
            if "Status Update" in test_name:
                critical_issues.append("Homeowners cannot accept/decline quotes - API restriction")
    
    print(f"\nTotal Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if critical_issues:
        print("\n🚨 CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"   • {issue}")
    
    if failed == 0:
        print("\n🎉 ALL HOMEOWNER QUOTATION TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️ {failed} HOMEOWNER QUOTATION TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = run_homeowner_quotation_tests()
    exit(0 if success else 1)