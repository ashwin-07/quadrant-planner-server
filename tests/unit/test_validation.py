"""
Unit tests for validation utilities
"""

import pytest
from api.shared.validation import (
    validate_user_id,
    validate_pagination,
    validate_goal_title,
    validate_goal_description,
    validate_task_title,
    validate_task_description,
    validate_position
)
from api.shared.exceptions import ValidationError


class TestUserIdValidation:
    """Test user ID validation"""
    
    def test_valid_user_id(self):
        """Test valid user ID"""
        valid_id = "user-123-abc"
        result = validate_user_id(valid_id)
        assert result == valid_id
    
    def test_empty_user_id(self):
        """Test empty user ID raises error"""
        with pytest.raises(ValidationError, match="User ID is required"):
            validate_user_id("")
    
    def test_none_user_id(self):
        """Test None user ID raises error"""
        with pytest.raises(ValidationError, match="User ID is required"):
            validate_user_id(None)
    
    def test_whitespace_user_id(self):
        """Test whitespace-only user ID raises error"""
        with pytest.raises(ValidationError, match="User ID is required"):
            validate_user_id("   ")
    
    def test_long_user_id(self):
        """Test overly long user ID raises error"""
        long_id = "a" * 256
        with pytest.raises(ValidationError, match="User ID must be 255 characters or less"):
            validate_user_id(long_id)


class TestPaginationValidation:
    """Test pagination validation"""
    
    def test_valid_pagination(self):
        """Test valid pagination parameters"""
        limit, offset = validate_pagination(10, 20)
        assert limit == 10
        assert offset == 20
    
    def test_none_values_default(self):
        """Test None values use defaults"""
        limit, offset = validate_pagination(None, None)
        assert limit == 50
        assert offset == 0
    
    def test_invalid_limit_too_small(self):
        """Test limit too small raises error"""
        with pytest.raises(ValidationError, match="Limit must be an integer between 1 and 200"):
            validate_pagination(0, 0)
    
    def test_invalid_limit_too_large(self):
        """Test limit too large raises error"""
        with pytest.raises(ValidationError, match="Limit must be an integer between 1 and 200"):
            validate_pagination(201, 0)
    
    def test_invalid_offset_negative(self):
        """Test negative offset raises error"""
        with pytest.raises(ValidationError, match="Offset must be a non-negative integer"):
            validate_pagination(10, -1)


class TestGoalValidation:
    """Test goal validation functions"""
    
    def test_valid_goal_title(self):
        """Test valid goal title"""
        title = "My Test Goal"
        result = validate_goal_title(title)
        assert result == title
    
    def test_empty_goal_title(self):
        """Test empty goal title raises error"""
        with pytest.raises(ValidationError, match="Goal title is required"):
            validate_goal_title("")
    
    def test_whitespace_goal_title(self):
        """Test whitespace-only goal title raises error"""
        with pytest.raises(ValidationError, match="Goal title is required"):
            validate_goal_title("   ")
    
    def test_long_goal_title(self):
        """Test overly long goal title raises error"""
        long_title = "a" * 201
        with pytest.raises(ValidationError, match="Goal title must be 200 characters or less"):
            validate_goal_title(long_title)
    
    def test_valid_goal_description(self):
        """Test valid goal description"""
        description = "This is a test goal description"
        result = validate_goal_description(description)
        assert result == description
    
    def test_none_goal_description(self):
        """Test None goal description returns None"""
        result = validate_goal_description(None)
        assert result is None
    
    def test_empty_goal_description(self):
        """Test empty goal description returns None"""
        result = validate_goal_description("")
        assert result is None
    
    def test_long_goal_description(self):
        """Test overly long goal description raises error"""
        long_description = "a" * 1001
        with pytest.raises(ValidationError, match="Goal description must be 1000 characters or less"):
            validate_goal_description(long_description)


class TestTaskValidation:
    """Test task validation functions"""
    
    def test_valid_task_title(self):
        """Test valid task title"""
        title = "My Test Task"
        result = validate_task_title(title)
        assert result == title
    
    def test_empty_task_title(self):
        """Test empty task title raises error"""
        with pytest.raises(ValidationError, match="Task title is required"):
            validate_task_title("")
    
    def test_long_task_title(self):
        """Test overly long task title raises error"""
        long_title = "a" * 201
        with pytest.raises(ValidationError, match="Task title must be 200 characters or less"):
            validate_task_title(long_title)
    
    def test_valid_task_description(self):
        """Test valid task description"""
        description = "This is a test task description"
        result = validate_task_description(description)
        assert result == description
    
    def test_none_task_description(self):
        """Test None task description returns None"""
        result = validate_task_description(None)
        assert result is None
    
    def test_long_task_description(self):
        """Test overly long task description raises error"""
        long_description = "a" * 1001
        with pytest.raises(ValidationError, match="Task description must be 1000 characters or less"):
            validate_task_description(long_description)
    
    def test_valid_position(self):
        """Test valid position"""
        result = validate_position(5)
        assert result == 5
    
    def test_none_position_defaults(self):
        """Test None position defaults to 0"""
        result = validate_position(None)
        assert result == 0
    
    def test_negative_position(self):
        """Test negative position raises error"""
        with pytest.raises(ValidationError, match="Position must be 0 or greater"):
            validate_position(-1)
