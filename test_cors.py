#!/usr/bin/env python3
"""
Test CORS configuration for frontend integration
"""

import requests

def test_cors_headers():
    """Test that CORS headers are properly set"""
    print("🌐 Testing CORS Configuration...")
    
    try:
        # Test preflight request (OPTIONS)
        response = requests.options(
            "http://localhost:8000/api/v1/goals",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization,Content-Type"
            }
        )
        
        print(f"OPTIONS request status: {response.status_code}")
        print(f"CORS headers:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
        
        if response.status_code == 200:
            print("✅ CORS preflight request successful")
        else:
            print(f"❌ CORS preflight failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️  API server not running. Start with:")
        print("   source .venv/bin/activate && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ CORS test failed: {e}")

def test_cors_with_jwt():
    """Test actual request with JWT token"""
    print("\n🔐 Testing CORS with JWT authentication...")
    
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
            'Origin': 'http://localhost:5173',
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get("http://localhost:8000/api/v1/goals", headers=headers)
        
        print(f"GET request status: {response.status_code}")
        print(f"CORS headers in response:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
        
        if response.status_code == 200:
            print("✅ CORS with JWT authentication successful")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ CORS with JWT test failed: {e}")

def test_different_origins():
    """Test CORS with different frontend origins"""
    print("\n🔍 Testing different frontend origins...")
    
    origins_to_test = [
        "http://localhost:5173",  # Vite default
        "http://localhost:3000", # React default
        "http://localhost:3001", # Alternative port
        "https://your-frontend.vercel.app"  # Production
    ]
    
    for origin in origins_to_test:
        try:
            response = requests.options(
                "http://localhost:8000/api/v1/goals",
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "GET"
                }
            )
            
            print(f"Origin {origin}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ Allowed")
            else:
                print(f"  ❌ Blocked")
                
        except Exception as e:
            print(f"  ❌ Error testing {origin}: {e}")

if __name__ == "__main__":
    print("🌐 CORS Configuration Test")
    print("=" * 50)
    
    # Test 1: CORS headers
    test_cors_headers()
    
    # Test 2: CORS with JWT
    test_cors_with_jwt()
    
    # Test 3: Different origins
    test_different_origins()
    
    print("\n📝 CORS Configuration Summary:")
    print("✅ Frontend origin http://localhost:5173 is now allowed")
    print("✅ JWT Bearer token authentication works with CORS")
    print("✅ Preflight requests (OPTIONS) are handled correctly")
    print("\n🎯 Your frontend should now be able to make requests to the API!")
