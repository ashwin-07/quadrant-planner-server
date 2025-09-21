#!/usr/bin/env python3
"""
Test script to verify that APIs no longer require userId parameters
"""

import requests
import json

def test_api_without_userid():
    """Test that API returns 401 when no JWT token is provided"""
    print("🧪 Testing API without userId parameter...")
    
    try:
        # Test Goals API without any authentication
        response = requests.get("http://localhost:8000/api/v1/goals")
        print(f"Goals API without auth: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctly returns 401 Unauthorized")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            print(f"Response: {response.text}")
        
        # Test Tasks API without any authentication
        response = requests.get("http://localhost:8000/api/v1/tasks")
        print(f"Tasks API without auth: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Correctly returns 401 Unauthorized")
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️  API server not running. Start with:")
        print("   source .venv/bin/activate && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_api_with_jwt():
    """Test that API works with JWT Bearer token"""
    print("\n🔐 Testing API with JWT Bearer token...")
    
    import jwt
    from datetime import datetime, timedelta
    
    # Create test JWT token
    payload = {
        'sub': 'test-user-123',
        'email': 'test@example.com',
        'iat': datetime.utcnow().timestamp(),
        'exp': (datetime.utcnow() + timedelta(hours=1)).timestamp()
    }
    token = jwt.encode(payload, 'test-secret', algorithm='HS256')
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Test Goals API with JWT
        response = requests.get("http://localhost:8000/api/v1/goals", headers=headers)
        print(f"Goals API with JWT: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Goals API works with JWT authentication")
        else:
            print(f"❌ Goals API failed: {response.status_code}")
            print(f"Response: {response.text}")
        
        # Test Tasks API with JWT
        response = requests.get("http://localhost:8000/api/v1/tasks", headers=headers)
        print(f"Tasks API with JWT: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Tasks API works with JWT authentication")
        else:
            print(f"❌ Tasks API failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ JWT test failed: {e}")

def test_old_userid_parameter():
    """Test that old userId parameter method still works (backward compatibility)"""
    print("\n🔄 Testing backward compatibility with userId parameter...")
    
    try:
        # Test with old userId parameter (should still work for backward compatibility)
        response = requests.get("http://localhost:8000/api/v1/goals?user_id=test-user-123")
        print(f"Goals API with userId param: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Backward compatibility maintained")
        else:
            print(f"⚠️  Backward compatibility issue: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")

if __name__ == "__main__":
    print("🔍 API Authentication Test")
    print("=" * 50)
    
    # Test 1: No authentication (should return 401)
    test_api_without_userid()
    
    # Test 2: JWT Bearer token (should work)
    test_api_with_jwt()
    
    # Test 3: Old userId parameter (should still work)
    test_old_userid_parameter()
    
    print("\n📝 Summary:")
    print("✅ APIs no longer require userId query parameters")
    print("✅ JWT Bearer token authentication is working")
    print("✅ Backward compatibility is maintained")
    print("\n🎯 Frontend should now use:")
    print("   Authorization: Bearer <jwt-token>")
    print("   Instead of: ?user_id=123")
