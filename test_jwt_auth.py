#!/usr/bin/env python3
"""
Test script to verify JWT authentication is working
"""

import jwt
import json
from datetime import datetime, timedelta

# Create a test JWT token (for development/testing only)
def create_test_jwt_token(user_id: str = "test-user-123", email: str = "test@example.com"):
    """Create a test JWT token for development"""
    
    # Test payload (mimicking Google OAuth structure)
    payload = {
        "iss": "https://accounts.google.com",  # Issuer
        "aud": "your-client-id",  # Audience (your app's client ID)
        "sub": user_id,  # Subject (user ID)
        "email": email,
        "name": "Test User",
        "picture": "https://example.com/avatar.jpg",
        "iat": datetime.utcnow().timestamp(),  # Issued at
        "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp(),  # Expires
        "azp": "your-client-id",  # Authorized party
        "email_verified": True
    }
    
    # For testing, we'll create a token without signature verification
    # In production, this would be signed by Google
    token = jwt.encode(payload, "test-secret", algorithm="HS256")
    return token

def test_jwt_parsing():
    """Test JWT token parsing"""
    print("🧪 Testing JWT Authentication...")
    
    # Create test token
    test_token = create_test_jwt_token("test-user-123", "test@example.com")
    print(f"✅ Created test JWT token: {test_token[:50]}...")
    
    # Test token parsing
    try:
        # Decode without verification (for testing)
        decoded = jwt.decode(test_token, options={"verify_signature": False})
        print(f"✅ Successfully decoded token")
        print(f"   User ID: {decoded.get('sub')}")
        print(f"   Email: {decoded.get('email')}")
        print(f"   Expires: {datetime.fromtimestamp(decoded.get('exp'))}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to decode token: {e}")
        return False

def test_api_with_jwt():
    """Test API endpoints with JWT authentication"""
    print("\n🌐 Testing API with JWT...")
    
    import requests
    
    # Create test token
    test_token = create_test_jwt_token()
    
    # Test API endpoint
    try:
        headers = {
            "Authorization": f"Bearer {test_token}",
            "Content-Type": "application/json"
        }
        
        # Test the API (assuming it's running on localhost:8000)
        response = requests.get("http://localhost:8000/api/v1/goals", headers=headers)
        
        if response.status_code == 200:
            print("✅ API call with JWT successful!")
            print(f"   Response: {response.json()}")
        else:
            print(f"⚠️  API call returned status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️  API server not running. Start with: uvicorn api.main:app --reload")
    except Exception as e:
        print(f"❌ API test failed: {e}")

if __name__ == "__main__":
    print("🔐 JWT Authentication Test")
    print("=" * 40)
    
    # Test JWT parsing
    jwt_success = test_jwt_parsing()
    
    if jwt_success:
        # Test API integration
        test_api_with_jwt()
    
    print("\n📝 Next Steps:")
    print("1. Start the API server: uvicorn api.main:app --reload")
    print("2. Test with curl:")
    print(f"   curl -H 'Authorization: Bearer {create_test_jwt_token()}' http://localhost:8000/api/v1/goals")
    print("3. Update your frontend to send JWT tokens in Authorization header")
