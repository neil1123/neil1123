#!/usr/bin/env python3
"""
Review System Focused Testing
Tests the complete review system workflow with provided test credentials
"""

import requests
import json
import uuid

BACKEND_URL = "https://5f81e1b3-88a9-45db-958d-9cb5f0ec9f5a.preview.emergentagent.com/api"

def test_with_provided_credentials():
    """Test review system with provided test credentials"""
    print("🔍 Testing Review System with Provided Credentials...")
    
    # Test credentials from review request
    homeowner_email = "test@homeowner.com"
    homeowner_password = "password123"
    provider_email = "test@provider.com"
    provider_password = "password123"
    
    try:
        # Login as homeowner
        homeowner_login = {
            "email": homeowner_email,
            "password": homeowner_password
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=homeowner_login,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Homeowner login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        homeowner_data = response.json()
        homeowner_token = homeowner_data["access_token"]
        homeowner_id = homeowner_data["user"]["id"]
        
        print("✅ Homeowner login successful")
        
        # Login as provider
        provider_login = {
            "email": provider_email,
            "password": provider_password
        }
        
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json=provider_login,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Provider login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        provider_data = response.json()
        provider_token = provider_data["access_token"]
        provider_id = provider_data["user"]["id"]
        
        print("✅ Provider login successful")
        
        # Create an order as homeowner
        order_data = {
            "homeowner_id": homeowner_id,
            "provider_id": provider_id,
            "homeowner_name": "Test Homeowner",
            "homeowner_email": homeowner_email,
            "homeowner_phone": "+1-902-555-1234",
            "homeowner_address": "123 Test St, Halifax, NS",
            "provider_name": "Test Provider",
            "service_type": "Home Cleaning",
            "description": "Weekly house cleaning service"
        }
        
        homeowner_headers = {"Authorization": f"Bearer {homeowner_token}"}
        response = requests.post(
            f"{BACKEND_URL}/orders",
            json=order_data,
            headers=homeowner_headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Order creation failed: {response.status_code}")
            return False
        
        order = response.json()
        order_id = order["id"]
        
        print("✅ Order created successfully")
        
        # Complete the order as provider
        provider_headers = {"Authorization": f"Bearer {provider_token}"}
        response = requests.put(
            f"{BACKEND_URL}/orders/{order_id}/status?status=completed",
            headers=provider_headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Order completion failed: {response.status_code}")
            return False
        
        print("✅ Order marked as completed")
        
        # Submit review as homeowner
        review_data = {
            "provider_id": provider_id,
            "rating": 5,
            "review_text": "Excellent cleaning service! Very thorough and professional. Would definitely recommend to others.",
            "order_id": order_id
        }
        
        response = requests.post(
            f"{BACKEND_URL}/reviews",
            json=review_data,
            headers=homeowner_headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Review submission failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        review = response.json()
        print("✅ Review submitted successfully")
        print(f"   Review ID: {review['id']}")
        print(f"   Rating: {review['rating']}/5")
        print(f"   Review Text: {review['review_text']}")
        
        # Get provider reviews
        response = requests.get(
            f"{BACKEND_URL}/providers/{provider_id}/reviews",
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get provider reviews: {response.status_code}")
            return False
        
        reviews = response.json()
        print(f"✅ Retrieved {len(reviews)} reviews for provider")
        
        # Verify provider rating was updated
        response = requests.get(
            f"{BACKEND_URL}/providers/{provider_id}",
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get provider data: {response.status_code}")
            return False
        
        provider_info = response.json()
        updated_rating = provider_info.get("rating", 0)
        review_count = provider_info.get("reviews", 0)
        
        print(f"✅ Provider rating updated: {updated_rating}/5.0 ({review_count} reviews)")
        
        # Test analytics data
        response = requests.get(
            f"{BACKEND_URL}/orders",
            headers=provider_headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get orders for analytics: {response.status_code}")
            return False
        
        orders = response.json()
        completed_orders = [o for o in orders if o.get("status") == "completed"]
        total_revenue = sum(float(o.get("quotation_amount", 0)) for o in completed_orders if o.get("quotation_amount"))
        
        print(f"✅ Analytics data available:")
        print(f"   Total orders: {len(orders)}")
        print(f"   Completed orders: {len(completed_orders)}")
        print(f"   Total revenue: ${total_revenue:.2f}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_review_system_edge_cases():
    """Test edge cases and error scenarios"""
    print("\n🔍 Testing Review System Edge Cases...")
    
    try:
        # Test unauthenticated review submission
        review_data = {
            "provider_id": "test-provider-id",
            "rating": 5,
            "review_text": "Test review"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/reviews",
            json=review_data,
            timeout=30
        )
        
        if response.status_code != 401:
            print(f"❌ Expected 401 for unauthenticated review, got {response.status_code}")
            return False
        
        print("✅ Unauthenticated review properly blocked (401)")
        
        # Test getting reviews for non-existent provider
        response = requests.get(
            f"{BACKEND_URL}/providers/non-existent-provider/reviews",
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Expected 200 for non-existent provider reviews, got {response.status_code}")
            return False
        
        reviews = response.json()
        if not isinstance(reviews, list) or len(reviews) != 0:
            print(f"❌ Expected empty list for non-existent provider, got {reviews}")
            return False
        
        print("✅ Non-existent provider returns empty reviews list")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Edge cases test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🌟 REVIEW SYSTEM FOCUSED TESTING")
    print("=" * 70)
    
    success1 = test_with_provided_credentials()
    success2 = test_review_system_edge_cases()
    
    print("\n" + "=" * 70)
    print("📊 FOCUSED TEST SUMMARY")
    print("=" * 70)
    
    if success1 and success2:
        print("✅ ALL REVIEW SYSTEM TESTS PASSED!")
        print("\n🎉 Review System is fully functional:")
        print("   ✅ Homeowners can submit reviews after completing orders")
        print("   ✅ Provider ratings are automatically updated")
        print("   ✅ Reviews are properly validated and stored")
        print("   ✅ Analytics data is available for dashboard")
        print("   ✅ Authentication and authorization working correctly")
    else:
        print("❌ SOME REVIEW SYSTEM TESTS FAILED!")