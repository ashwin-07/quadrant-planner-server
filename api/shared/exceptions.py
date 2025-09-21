"""
Custom exceptions for the Quadrant Planner API
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException


class QuadrantPlannerException(HTTPException):
    """Base exception class for Quadrant Planner API"""
    
    def __init__(
        self,
        status_code: int,
        message: str,
        code: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        
        super().__init__(
            status_code=status_code,
            detail={
                "success": False,
                "error": {
                    "message": message,
                    "code": code,
                    "details": self.details
                }
            }
        )


class ValidationError(QuadrantPlannerException):
    """Validation error exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=400,
            message=message,
            code="VALIDATION_ERROR",
            details=details
        )


class NotFoundError(QuadrantPlannerException):
    """Resource not found exception"""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=404,
            message=f"{resource} not found",
            code=f"{resource.upper()}_NOT_FOUND",
            details={"identifier": identifier}
        )


class ConflictError(QuadrantPlannerException):
    """Resource conflict exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=409,
            message=message,
            code="CONFLICT_ERROR",
            details=details
        )


class UnauthorizedError(QuadrantPlannerException):
    """Unauthorized access exception"""
    
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            status_code=401,
            message=message,
            code="UNAUTHORIZED",
            details={}
        )


class ForbiddenError(QuadrantPlannerException):
    """Forbidden access exception"""
    
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(
            status_code=403,
            message=message,
            code="FORBIDDEN",
            details={}
        )


class RateLimitError(QuadrantPlannerException):
    """Rate limit exceeded exception"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            status_code=429,
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            details={}
        )


class DatabaseError(QuadrantPlannerException):
    """Database operation error"""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            status_code=500,
            message=message,
            code="DATABASE_ERROR",
            details={}
        )
