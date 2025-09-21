"""
Tests for main API application
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.api
class TestMainAPI:
    """Test main API application endpoints"""
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns API information"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Quadrant Planner API is running"
        assert "version" in data
        assert "environment" in data
        assert data["docs"] == "/api/docs"
    
    def test_api_root_endpoint(self, client: TestClient):
        """Test API root endpoint returns API overview"""
        response = client.get("/api")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Welcome to Quadrant Planner API"
        assert "version" in data
        assert "implemented_endpoints" in data
        assert "features" in data
        
        # Check implemented endpoints
        endpoints = data["implemented_endpoints"]
        assert "goals" in endpoints
        assert "tasks" in endpoints
        assert "/api/v1/goals" in endpoints["goals"]
        assert "/api/v1/tasks" in endpoints["tasks"]
        
        # Check features
        features = data["features"]
        assert "goal_management" in features
        assert "task_quadrants" in features
        assert "staging_zone" in features
        assert "real_time_sync" in features
    
    def test_health_check_endpoint(self, client: TestClient):
        """Test health check endpoint"""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_docs_endpoint_accessible(self, client: TestClient):
        """Test that API documentation is accessible"""
        response = client.get("/docs")
        
        # Should return HTML for Swagger UI
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_schema_accessible(self, client: TestClient):
        """Test that OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "Quadrant Planner API"
    
    def test_cors_headers(self, client: TestClient):
        """Test CORS headers are properly set"""
        # Test preflight request
        response = client.options("/api", headers={"Origin": "https://example.com"})
        
        # Should handle OPTIONS request
        assert response.status_code == 200
    
    def test_404_endpoint(self, client: TestClient):
        """Test 404 response for non-existent endpoint"""
        response = client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404
