"""
Input validation utilities for the Quadrant Planner API
"""

import re
from typing import Any, List, Optional, Tuple
from datetime import datetime
from pydantic import validator
from api.shared.exceptions import ValidationError


def validate_user_id(user_id: str) -> str:
    """Validate user ID format"""
    if not user_id or not user_id.strip():
        raise ValidationError("User ID is required")
    
    if len(user_id) > 255:
        raise ValidationError("User ID must be 255 characters or less")
    
    return user_id.strip()


def validate_goal_title(title: str) -> str:
    """Validate goal title"""
    if not title or not title.strip():
        raise ValidationError("Goal title is required")
    
    title = title.strip()
    if len(title) > 200:
        raise ValidationError("Goal title must be 200 characters or less")
    
    return title


def validate_goal_description(description: Optional[str]) -> Optional[str]:
    """Validate goal description"""
    if description is None:
        return None
    
    description = description.strip()
    if len(description) > 1000:
        raise ValidationError("Goal description must be 1000 characters or less")
    
    return description if description else None


def validate_task_title(title: str) -> str:
    """Validate task title"""
    if not title or not title.strip():
        raise ValidationError("Task title is required")
    
    title = title.strip()
    if len(title) > 200:
        raise ValidationError("Task title must be 200 characters or less")
    
    return title


def validate_task_description(description: Optional[str]) -> Optional[str]:
    """Validate task description"""
    if description is None:
        return None
    
    description = description.strip()
    if len(description) > 1000:
        raise ValidationError("Task description must be 1000 characters or less")
    
    return description if description else None


def validate_estimated_minutes(minutes: Optional[int]) -> Optional[int]:
    """Validate estimated minutes"""
    if minutes is None:
        return None
    
    if minutes < 1 or minutes > 480:  # 1 minute to 8 hours
        raise ValidationError("Estimated minutes must be between 1 and 480")
    
    return minutes


def validate_tags(tags: Optional[List[str]]) -> List[str]:
    """Validate task tags"""
    if tags is None:
        return []
    
    if len(tags) > 10:
        raise ValidationError("Maximum 10 tags allowed")
    
    validated_tags = []
    for tag in tags:
        if not isinstance(tag, str):
            raise ValidationError("Tags must be strings")
        
        tag = tag.strip()
        if len(tag) > 50:
            raise ValidationError("Each tag must be 50 characters or less")
        
        if tag and tag not in validated_tags:
            validated_tags.append(tag)
    
    return validated_tags


def validate_color(color: Optional[str]) -> Optional[str]:
    """Validate color format (hex or color name)"""
    if color is None:
        return None
    
    color = color.strip()
    
    # Check if it's a valid hex color
    if re.match(r'^#[0-9A-Fa-f]{6}$', color):
        return color
    
    # Check if it's a valid color name (basic validation)
    valid_colors = {
        'red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink',
        'cyan', 'magenta', 'lime', 'indigo', 'violet', 'brown', 'gray',
        'black', 'white', 'navy', 'teal', 'maroon', 'olive'
    }
    
    if color.lower() in valid_colors:
        return color.lower()
    
    raise ValidationError("Invalid color format. Use hex color (#FFFFFF) or color name")


def validate_pagination(limit: Optional[int], offset: Optional[int]) -> Tuple[int, int]:
    """Validate pagination parameters"""
    if limit is None:
        limit = 50
    if offset is None:
        offset = 0
    
    if limit < 1 or limit > 200:
        raise ValidationError("Limit must be an integer between 1 and 200")
    
    if offset < 0:
        raise ValidationError("Offset must be a non-negative integer")
    
    return limit, offset


def validate_task_title(title: str) -> str:
    """Validate task title"""
    if not title or not title.strip():
        raise ValidationError("Task title is required")
    
    title = title.strip()
    if len(title) > 200:
        raise ValidationError("Task title must be 200 characters or less")
    
    return title


def validate_task_description(description: Optional[str]) -> Optional[str]:
    """Validate task description"""
    if description is None:
        return None
    
    description = description.strip()
    if len(description) > 1000:
        raise ValidationError("Task description must be 1000 characters or less")
    
    return description if description else None


def validate_position(position: Optional[int]) -> int:
    """Validate task position"""
    if position is None:
        return 0
    
    if position < 0:
        raise ValidationError("Position must be 0 or greater")
    
    return position


class BaseValidator:
    """Base validator class with common validation methods"""
    
    @staticmethod
    def validate_required_string(value: Any, field_name: str, max_length: Optional[int] = None) -> str:
        """Validate a required string field"""
        if not value or not str(value).strip():
            raise ValidationError(f"{field_name} is required")
        
        value = str(value).strip()
        if max_length and len(value) > max_length:
            raise ValidationError(f"{field_name} must be {max_length} characters or less")
        
        return value
    
    @staticmethod
    def validate_optional_string(value: Any, field_name: str, max_length: Optional[int] = None) -> Optional[str]:
        """Validate an optional string field"""
        if value is None:
            return None
        
        value = str(value).strip()
        if not value:
            return None
        
        if max_length and len(value) > max_length:
            raise ValidationError(f"{field_name} must be {max_length} characters or less")
        
        return value
    
    @staticmethod
    def validate_enum(value: Any, field_name: str, allowed_values: List[str]) -> str:
        """Validate enum field"""
        if value not in allowed_values:
            raise ValidationError(f"{field_name} must be one of: {', '.join(allowed_values)}")
        
        return value
