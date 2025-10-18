"""
Quadrant Planner API - Main FastAPI application
Philosophy-driven productivity backend server
"""

import os
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI app with camelCase JSON response
app = FastAPI(
    title="Quadrant Planner API",
    description="Backend API for Quadrant Planner - A philosophy-driven productivity application implementing Stephen Covey's Time Management Matrix",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    # Use camelCase for JSON responses to match frontend conventions
    # Pydantic models use populate_by_name=True to accept both formats and serialize_by_alias for responses
)

# Add JWT Bearer token security scheme
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add JWT Bearer token security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Bearer token from Google OAuth authentication. Example: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`"
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # Add example JWT token for testing
    if "info" not in openapi_schema:
        openapi_schema["info"] = {}
    
    openapi_schema["info"]["x-examples"] = {
        "jwt_token_example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhdWQiOiJ5b3VyLWNsaWVudC1pZCIsInN1YiI6InRlc3QtdXNlci0xMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJuYW1lIjoiVGVzdCBVc2VyIiwicGljdHVyZSI6Imh0dHBzOi8vZXhhbXBsZS5jb20vYXZhdGFyLmpwZyIsImlhdCI6MTc1ODQ1MzkxMSwiZXhwIjoxNzU4NDU3NTExLCJhenAiOiJ5b3VyLWNsaWVudC1pZCIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlfQ.w_AxIxdXBmpFZeReHpy0YQAlgxnjsbvDI9lFtrxVDoQ"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS Configuration
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:3001").split(",")
# Clean up any whitespace
origins = [origin.strip() for origin in origins]

logger.info(f"CORS allowed origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Import routers
from api.goals.routes import router as goals_router
from api.tasks.routes import router as tasks_router
# Analytics router temporarily disabled due to circular dependency in Pydantic models
# from api.analytics.routes import router as analytics_router

# Include routers with API versioning
api_version = os.getenv("API_VERSION", "v1")
app.include_router(goals_router, prefix=f"/api/{api_version}/goals", tags=["goals"])
app.include_router(tasks_router, prefix=f"/api/{api_version}/tasks", tags=["tasks"])
# app.include_router(analytics_router, prefix=f"/api/{api_version}/analytics", tags=["analytics"])


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint - API health check"""
    return {
        "success": True,
        "message": "Quadrant Planner API is running",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "docs": "/api/docs"
    }


@app.get("/api")
async def api_root() -> Dict[str, Any]:
    """API root endpoint"""
    return {
        "success": True,
        "message": "Welcome to Quadrant Planner API",
        "version": api_version,
        "status": "Development",
        "implemented_endpoints": {
            "goals": f"/api/{api_version}/goals",
            "tasks": f"/api/{api_version}/tasks"
        },
        "coming_soon": {
            "analytics": f"/api/{api_version}/analytics (circular dependency fix needed)"
        },
        "features": {
            "goal_management": "Create, update, and track goals with progress analytics",
            "task_quadrants": "Organize tasks using Eisenhower Matrix (Q1-Q4) with staging zone",
            "staging_zone": "Temporary holding area for unorganized tasks (max 5 items)",
            "real_time_sync": "Real-time updates with Supabase integration"
        },
        "documentation": "/api/docs"
    }


@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for monitoring"""
    return {
        "success": True,
        "status": "healthy",
        "timestamp": "2025-09-20T00:00:00Z",
        "version": "1.0.0"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "message": "Internal server error",
                "code": "INTERNAL_SERVER_ERROR",
                "details": {}
            },
            "timestamp": "2025-09-20T00:00:00Z"
        }
    )


# Vercel serverless function handler
def handler(request: Request) -> Any:
    """Vercel serverless function handler"""
    return app(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("ENVIRONMENT") == "development"
    )
