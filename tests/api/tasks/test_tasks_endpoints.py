"""
API tests for Tasks endpoints
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient


@pytest.mark.api
class TestTasksAPI:
    """Test Tasks API endpoints"""
    
    def test_get_tasks_success(self, client: TestClient, mock_db_dependency, sample_task_response):
        """Test successful retrieval of tasks list"""
        # Mock database response
        mock_execute_result = Mock()
        mock_execute_result.data = [sample_task_response]
        mock_execute_result.count = 1
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_execute_result
        
        # Make request
        response = client.get("/api/v1/tasks?user_id=test-user-123")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "tasks" in data["data"]
        assert len(data["data"]["tasks"]) == 1
        assert data["data"]["tasks"][0]["id"] == "task-123"
    
    def test_get_tasks_with_quadrant_filter(self, client: TestClient, mock_db_dependency, sample_task_response):
        """Test tasks retrieval with quadrant filter"""
        # Mock database response
        mock_execute_result = Mock()
        mock_execute_result.data = [sample_task_response]
        mock_execute_result.count = 1
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_execute_result
        
        # Make request with quadrant filter
        response = client.get("/api/v1/tasks?user_id=test-user-123&quadrant=Q1")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["tasks"]) == 1
        assert data["data"]["tasks"][0]["quadrant"] == "Q1"
    
    def test_get_tasks_invalid_quadrant(self, client: TestClient):
        """Test tasks retrieval with invalid quadrant filter"""
        response = client.get("/api/v1/tasks?user_id=test-user-123&quadrant=INVALID")
        assert response.status_code == 400  # Validation error
    
    def test_create_task_success(self, client: TestClient, mock_db_dependency, sample_task_data, sample_task_response):
        """Test successful task creation"""
        # Mock database response
        mock_execute_result = Mock()
        mock_execute_result.data = [sample_task_response]
        mock_db_dependency.table.return_value.insert.return_value.execute.return_value = mock_execute_result
        
        # Prepare request data
        request_data = {**sample_task_data, "user_id": "test-user-123"}
        
        # Make request
        response = client.post("/api/v1/tasks", json=request_data)
        
        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "task-123"
        assert data["data"]["title"] == sample_task_data["title"]
    
    def test_create_task_missing_title(self, client: TestClient):
        """Test task creation with missing title"""
        incomplete_data = {
            "user_id": "test-user-123",
            "quadrant": "Q1"
        }
        
        response = client.post("/api/v1/tasks", json=incomplete_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_task_staging_zone_full(self, client: TestClient, mock_db_dependency):
        """Test task creation when staging zone is full"""
        # Mock staging zone count (5 items = full)
        mock_count_result = Mock()
        mock_count_result.count = 5
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_count_result
        
        request_data = {
            "user_id": "test-user-123",
            "title": "Test Task",
            "quadrant": "staging",
            "is_staged": True
        }
        
        response = client.post("/api/v1/tasks", json=request_data)
        assert response.status_code == 400
        data = response.json()
        assert "staging zone is full" in data["detail"].lower()
    
    def test_get_task_by_id_success(self, client: TestClient, mock_db_dependency, sample_task_response):
        """Test successful retrieval of specific task"""
        # Mock database response
        mock_execute_result = Mock()
        mock_execute_result.data = [sample_task_response]
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_execute_result
        
        # Make request
        response = client.get("/api/v1/tasks/task-123?user_id=test-user-123")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "task-123"
        assert data["data"]["title"] == sample_task_response["title"]
    
    def test_toggle_task_completion_success(self, client: TestClient, mock_db_dependency, sample_task_response):
        """Test successful task completion toggle"""
        # Mock database responses
        mock_verify_result = Mock()
        mock_verify_result.data = [sample_task_response]
        
        completed_task = {**sample_task_response, "completed": True, "completed_at": "2024-01-01T12:00:00Z"}
        mock_update_result = Mock()
        mock_update_result.data = [completed_task]
        
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_verify_result
        mock_db_dependency.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_update_result
        
        # Make request
        toggle_data = {
            "user_id": "test-user-123",
            "completed": True
        }
        response = client.patch("/api/v1/tasks/task-123/toggle", json=toggle_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["completed"] is True
        assert data["data"]["completed_at"] is not None
    
    def test_move_task_success(self, client: TestClient, mock_db_dependency, sample_task_response):
        """Test successful task move (drag & drop)"""
        # Mock database responses
        mock_verify_result = Mock()
        mock_verify_result.data = [sample_task_response]
        
        moved_task = {**sample_task_response, "quadrant": "Q2", "position": 5}
        mock_update_result = Mock()
        mock_update_result.data = [moved_task]
        
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_verify_result
        mock_db_dependency.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_update_result
        
        # Make request
        move_data = {
            "user_id": "test-user-123",
            "new_quadrant": "Q2",
            "new_position": 5
        }
        response = client.patch("/api/v1/tasks/task-123/move", json=move_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["quadrant"] == "Q2"
        assert data["data"]["position"] == 5
    
    def test_move_task_invalid_quadrant(self, client: TestClient):
        """Test task move with invalid quadrant"""
        move_data = {
            "user_id": "test-user-123",
            "new_quadrant": "INVALID",
            "new_position": 0
        }
        response = client.patch("/api/v1/tasks/task-123/move", json=move_data)
        assert response.status_code == 400  # Validation error
    
    def test_get_staging_status_success(self, client: TestClient, mock_db_dependency):
        """Test successful staging zone status retrieval"""
        # Mock staging zone count
        mock_count_result = Mock()
        mock_count_result.count = 3
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_count_result
        
        # Make request
        response = client.get("/api/v1/tasks/staging/status?user_id=test-user-123")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["current_count"] == 3
        assert data["data"]["max_capacity"] == 5
        assert data["data"]["is_full"] is False
        assert data["data"]["available_slots"] == 2
    
    def test_get_task_stats_success(self, client: TestClient, mock_db_dependency):
        """Test successful task statistics retrieval"""
        # Mock task counts
        mock_total_result = Mock()
        mock_total_result.count = 10
        
        mock_completed_result = Mock()
        mock_completed_result.count = 6
        
        mock_overdue_result = Mock()
        mock_overdue_result.count = 2
        
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.execute.side_effect = [
            mock_total_result,    # Total tasks
            mock_completed_result, # Completed tasks
            mock_overdue_result   # Overdue tasks
        ]
        
        # Make request
        response = client.get("/api/v1/tasks/stats/summary?user_id=test-user-123")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_tasks"] == 10
        assert data["data"]["completed_tasks"] == 6
        assert data["data"]["active_tasks"] == 4
        assert data["data"]["overdue_tasks"] == 2
        assert data["data"]["completion_rate"] == 60.0
    
    def test_delete_task_success(self, client: TestClient, mock_db_dependency, sample_task_response):
        """Test successful task deletion"""
        # Mock database responses
        mock_verify_result = Mock()
        mock_verify_result.data = [sample_task_response]
        
        mock_delete_result = Mock()
        mock_delete_result.data = [sample_task_response]
        
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_verify_result
        mock_db_dependency.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = mock_delete_result
        
        # Make request
        response = client.delete("/api/v1/tasks/task-123?user_id=test-user-123")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Task deleted successfully"
    
    def test_update_task_success(self, client: TestClient, mock_db_dependency, sample_task_response):
        """Test successful task update"""
        # Mock database responses
        mock_verify_result = Mock()
        mock_verify_result.data = [sample_task_response]
        
        updated_task = {**sample_task_response, "title": "Updated Task Title", "priority": "medium"}
        mock_update_result = Mock()
        mock_update_result.data = [updated_task]
        
        mock_db_dependency.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_verify_result
        mock_db_dependency.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = mock_update_result
        
        # Prepare update data
        update_data = {
            "title": "Updated Task Title",
            "priority": "medium",
            "user_id": "test-user-123"
        }
        
        # Make request
        response = client.put("/api/v1/tasks/task-123", json=update_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["title"] == "Updated Task Title"
        assert data["data"]["priority"] == "medium"
