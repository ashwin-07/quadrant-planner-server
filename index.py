"""
Vercel serverless entry point for Quadrant Planner API
"""

from api.main import app

# Vercel's Python runtime supports ASGI apps directly
# Just export the FastAPI app instance
app = app

