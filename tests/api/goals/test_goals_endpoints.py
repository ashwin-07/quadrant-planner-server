"""
API tests for Goals endpoints
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient


@pytest.mark.api
class TestGoalsAPI:
    """Test Goals API endpoints"""
    
    def test_get_goals_success(self, client: TestClient, mock_db_dependency, sample_goal_response):
        """Test successful retrieval of goals list"""
        # Mock database response
        mock_execute_result = Mock()
        mock_execute_result.data = [sample_goal_response]
        mock_execute_result.count = 1
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_execute_result
        
        # Make request
        response = client.get("/api/v1/goals?user_id=test-user-123")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "goals" in data["data"]
        assert len(data["data"]["goals"]) == 1
        assert data["data"]["goals"][0]["id"] == "goal-123"
    
    def test_get_goals_missing_user_id(self, client: TestClient):
        """Test goals retrieval without user_id parameter"""
        response = client.get("/api/v1/goals")
        assert response.status_code == 422  # Validation error
    
    def test_get_goals_with_filters(self, client: TestClient, mock_db_dependency, sample_goal_response):
        """Test goals retrieval with category filter"""
        # Mock database response
        mock_execute_result = Mock()
        mock_execute_result.data = [sample_goal_response]
        mock_execute_result.count = 1
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_execute_result
        
        # Make request with filters
        response = client.get("/api/v1/goals?user_id=test-user-123&category=personal&timeframe=short_term")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["goals"]) == 1
    
    def test_create_goal_success(self, client: TestClient, mock_db_dependency, sample_goal_data, sample_goal_response):
        """Test successful goal creation"""
        # Mock database response
        mock_execute_result = Mock()
        mock_execute_result.data = [sample_goal_response]
        mock_db_dependency.table.return_value.insert.return_value.execute.return_value = mock_execute_result
        
        # Prepare request data
        request_data = {**sample_goal_data, "user_id": "test-user-123"}
        
        # Make request
        response = client.post("/api/v1/goals", json=request_data)
        
        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "goal-123"
        assert data["data"]["title"] == sample_goal_data["title"]
    
    def test_create_goal_missing_required_fields(self, client: TestClient):
        """Test goal creation with missing required fields"""
        incomplete_data = {"user_id": "test-user-123"}
        
        response = client.post("/api/v1/goals", json=incomplete_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_goal_invalid_category(self, client: TestClient):
        """Test goal creation with invalid category"""
        invalid_data = {
            "user_id": "test-user-123",
            "title": "Test Goal",
            "category": "invalid_category",
            "timeframe": "short_term"
        }
        
        response = client.post("/api/v1/goals", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_get_goal_by_id_success(self, client: TestClient, mock_db_dependency, sample_goal_response):
        """Test successful retrieval of specific goal"""
        # Mock database response
        mock_execute_result = Mock()
        mock_execute_result.data = [sample_goal_response]
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_execute_result
        
        # Make request
        response = client.get("/api/v1/goals/goal-123?user_id=test-user-123")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "goal-123"
        assert data["data"]["title"] == sample_goal_response["title"]
    
    def test_get_goal_by_id_not_found(self, client: TestClient, mock_db_dependency):
        """Test retrieval of non-existent goal"""
        # Mock database response (empty)
        mock_execute_result = Mock()
        mock_execute_result.data = []
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_execute_result
        
        # Make request
        response = client.get("/api/v1/goals/non-existent?user_id=test-user-123")
        
        # Assertions
        assert response.status_code == 404
    
    def test_update_goal_success(self, client: TestClient, mock_db_dependency, sample_goal_response):
        """Test successful goal update"""
        # Mock database responses
        # First call for verification
        mock_verify_result = Mock()
        mock_verify_result.data = [sample_goal_response]
        
        # Second call for update
        updated_goal = {**sample_goal_response, "title": "Updated Goal Title"}
        mock_update_result = Mock()
        mock_update_result.data = [updated_goal]
        
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.side_effect = [mock_verify_result]
        mock_db_dependency.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_update_result
        
        # Prepare update data
        update_data = {
            "title": "Updated Goal Title",
            "user_id": "test-user-123"
        }
        
        # Make request
        response = client.put("/api/v1/goals/goal-123", json=update_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["title"] == "Updated Goal Title"
    
    def test_update_goal_not_found(self, client: TestClient, mock_db_dependency):
        """Test update of non-existent goal"""
        # Mock database response (empty)
        mock_execute_result = Mock()
        mock_execute_result.data = []
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_execute_result
        
        # Prepare update data
        update_data = {
            "title": "Updated Goal Title",
            "user_id": "test-user-123"
        }
        
        # Make request
        response = client.put("/api/v1/goals/non-existent", json=update_data)
        
        # Assertions
        assert response.status_code == 404
    
    def test_delete_goal_success(self, client: TestClient, mock_db_dependency, sample_goal_response):
        """Test successful goal deletion"""
        # Mock database responses
        mock_verify_result = Mock()
        mock_verify_result.data = [sample_goal_response]
        
        mock_delete_result = Mock()
        mock_delete_result.data = [sample_goal_response]
        
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_verify_result
        mock_db_dependency.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = mock_delete_result
        
        # Make request
        response = client.delete("/api/v1/goals/goal-123?user_id=test-user-123")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Goal deleted successfully"
    
    def test_delete_goal_not_found(self, client: TestClient, mock_db_dependency):
        """Test deletion of non-existent goal"""
        # Mock database response (empty)
        mock_execute_result = Mock()
        mock_execute_result.data = []
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_execute_result
        
        # Make request
        response = client.delete("/api/v1/goals/non-existent?user_id=test-user-123")
        
        # Assertions
        assert response.status_code == 404
