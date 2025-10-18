"""
Vercel serverless entry point for Quadrant Planner API
"""

from mangum import Mangum
from api.main import app

# Mangum adapter for AWS Lambda/Vercel
handler = Mangum(app, lifespan="off")

# Also expose app for local development
__all__ = ['app', 'handler']

