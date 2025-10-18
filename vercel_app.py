"""
Vercel serverless entry point for Quadrant Planner API
This file is specifically for Vercel deployment
"""

# Import the FastAPI application
from api.main import app as application

# Vercel looks for 'app' or 'application' variable
# Export it so Vercel can find it
app = application

