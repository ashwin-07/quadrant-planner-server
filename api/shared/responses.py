"""
Standard response models for consistent API responses
"""

from typing import Any, Dict, Optional, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar('T')


class ErrorDetail(BaseModel):
    """Error detail model"""
    message: str
    code: str
    details: Dict[str, Any] = Field(default_factory=dict)


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response model"""
    success: bool = True
    data: T
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Standard error response model"""
    success: bool = False
    error: ErrorDetail
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model"""
    success: bool = True
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def __init__(self, items: list[T], total: int, has_more: bool, **kwargs: Any):
        data = {
            "items": items,
            "total": total,
            "has_more": has_more
        }
        super().__init__(data=data, **kwargs)


def success_response(data: T, message: Optional[str] = None) -> SuccessResponse[T]:
    """Create a success response"""
    return SuccessResponse(data=data, message=message)


def error_response(
    message: str, 
    code: str, 
    details: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """Create an error response"""
    return ErrorResponse(
        error=ErrorDetail(
            message=message,
            code=code,
            details=details or {}
        )
    )


def paginated_response(
    items: list[T], 
    total: int, 
    has_more: bool,
    message: Optional[str] = None
) -> PaginatedResponse[T]:
    """Create a paginated response"""
    return PaginatedResponse(
        items=items,
        total=total,
        has_more=has_more,
        message=message
    )
