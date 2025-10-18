"""
Vercel serverless entry point for Quadrant Planner API
"""

from api.main import app

# Vercel expects the ASGI app to be named 'app'
__all__ = ['app']

