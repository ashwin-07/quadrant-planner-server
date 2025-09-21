"""
Database connection and Supabase client setup
"""

import os
import logging
from typing import Optional
from supabase import create_client, Client
from api.shared.exceptions import DatabaseError

logger = logging.getLogger(__name__)

# Global Supabase client
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create Supabase client"""
    global _supabase_client
    
    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            raise DatabaseError("Supabase configuration missing")
        
        try:
            _supabase_client = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise DatabaseError("Failed to connect to database")
    
    return _supabase_client


def get_service_client() -> Client:
    """Get Supabase client with service role key for admin operations"""
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not service_key:
        raise DatabaseError("Supabase service configuration missing")
    
    try:
        return create_client(supabase_url, service_key)
    except Exception as e:
        logger.error(f"Failed to initialize Supabase service client: {e}")
        raise DatabaseError("Failed to connect to database with service role")


class DatabaseManager:
    """Database manager for handling database operations"""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.service_client = get_service_client()
    
    async def health_check(self) -> bool:
        """Check database connection health"""
        try:
            # Simple query to test connection
            result = self.client.table("goals").select("count", count="exact").limit(1).execute()
            logger.info("Database health check passed")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_client(self, use_service_role: bool = False) -> Client:
        """Get the appropriate Supabase client"""
        return self.service_client if use_service_role else self.client
    
    def set_user_context(self, user_id: str) -> None:
        """Set user context for RLS policies when using service role"""
        try:
            # This would be used with service role for operations that need to bypass RLS
            # while still maintaining user context for logging/auditing
            logger.debug(f"Setting user context: {user_id}")
        except Exception as e:
            logger.error(f"Failed to set user context: {e}")
            raise DatabaseError("Failed to set user context")
    
    def verify_tables_exist(self) -> bool:
        """Verify that required tables exist"""
        try:
            required_tables = ['goals', 'tasks']
            for table in required_tables:
                self.client.table(table).select("count", count="exact").limit(1).execute()
            logger.info("All required tables verified")
            return True
        except Exception as e:
            logger.error(f"Table verification failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()
