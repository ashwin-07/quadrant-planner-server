"""
Test configuration and fixtures for Quadrant Planner API
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import the main app
from api.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    Create a test client for synchronous API testing
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async test client for asynchronous API testing
    """
    async with AsyncClient(app=app, base_url="http://test") as async_test_client:
        yield async_test_client


@pytest.fixture
def mock_supabase_client():
    """
    Mock Supabase client for testing without database dependencies
    """
    mock_client = Mock()
    
    # Mock table method chain
    mock_table = Mock()
    mock_client.table.return_value = mock_table
    
    # Mock common query methods
    mock_table.select.return_value = mock_table
    mock_table.insert.return_value = mock_table
    mock_table.update.return_value = mock_table
    mock_table.delete.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.filter.return_value = mock_table
    mock_table.order.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.offset.return_value = mock_table
    mock_table.range.return_value = mock_table
    
    # Mock execute method
    mock_execute_result = Mock()
    mock_execute_result.data = []
    mock_execute_result.count = 0
    mock_table.execute.return_value = mock_execute_result
    
    return mock_client


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing"""
    return "test-user-123"


@pytest.fixture 
def sample_goal_data():
    """Sample goal data for testing"""
    return {
        "title": "Test Goal",
        "description": "A test goal for testing purposes",
        "category": "personal",
        "timeframe": "short_term",
        "color": "#3B82F6",
        "is_favorite": False,
        "archived": False
    }


@pytest.fixture
def sample_task_data():
    """Sample task data for testing"""
    return {
        "title": "Test Task",
        "description": "A test task for testing purposes",
        "quadrant": "Q1",
        "priority": "high",
        "position": 0,
        "completed": False,
        "is_staged": False,
        "tags": ["test", "api"]
    }


@pytest.fixture
def sample_goal_response():
    """Sample goal response from database"""
    return {
        "id": "goal-123",
        "user_id": "test-user-123",
        "title": "Test Goal",
        "description": "A test goal for testing purposes",
        "category": "personal",
        "timeframe": "short_term",
        "color": "#3B82F6",
        "is_favorite": False,
        "archived": False,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_task_response():
    """Sample task response from database"""
    return {
        "id": "task-123",
        "user_id": "test-user-123",
        "goal_id": "goal-123",
        "title": "Test Task",
        "description": "A test task for testing purposes",
        "quadrant": "Q1",
        "priority": "high",
        "position": 0,
        "completed": False,
        "is_staged": False,
        "tags": ["test", "api"],
        "due_date": None,
        "completed_at": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_db_dependency(mock_supabase_client):
    """
    Mock the database dependency injection
    """
    from api.dependencies import get_db
    
    def override_get_db():
        return mock_supabase_client
    
    app.dependency_overrides[get_db] = override_get_db
    yield mock_supabase_client
    # Clean up
    app.dependency_overrides = {}


# Pytest markers for organizing tests
pytestmark = pytest.mark.asyncio
