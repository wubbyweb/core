# backend/app/db/supabase_client.py
from supabase import create_client, Client
from typing import Optional, Dict, Any
from ..core.config import settings
import logging
from functools import wraps
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def handle_supabase_errors(func):
    """Decorator to handle Supabase errors"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Supabase error in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Database operation failed: {str(e)}"
            )
    return wrapper

class SupabaseClient:
    _instance = None
    _client: Optional[Client] = None
    _admin_client: Optional[Client] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._client:
            self._initialize_clients()

    def _initialize_clients(self):
        """Initialize both regular and admin Supabase clients"""
        try:
            # Initialize regular client
            if settings.SUPABASE_URL and settings.SUPABASE_KEY:
                logger.info("Initializing Supabase client...")
                self._client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
                logger.info("Supabase client initialized successfully")
            else:
                logger.error("Supabase URL or Key is missing")

            # Initialize admin client
            if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
                logger.info("Initializing Supabase admin client...")
                self._admin_client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_SERVICE_ROLE_KEY
                )
                logger.info("Supabase admin client initialized successfully")
            else:
                logger.error("Supabase URL or Service Role Key is missing")

        except Exception as e:
            logger.error(f"Failed to initialize Supabase clients: {str(e)}")
            raise

    @property
    def client(self) -> Client:
        """Get regular Supabase client"""
        if not self._client:
            raise Exception("Supabase client not initialized")
        return self._client

    @property
    def admin_client(self) -> Client:
        """Get admin Supabase client"""
        if not self._admin_client:
            raise Exception("Supabase admin client not initialized")
        return self._admin_client

    @handle_supabase_errors
    async def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """Select data from a table"""
        query = self.client.from_(table).select(columns)

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        return await query.execute()

    @handle_supabase_errors
    async def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> Dict:
        """Insert data into a table"""
        return await self.client.from_(table).insert(data).execute()

    @handle_supabase_errors
    async def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Dict[str, Any]
    ) -> Dict:
        """Update data in a table"""
        query = self.client.from_(table).update(data)

        for key, value in filters.items():
            query = query.eq(key, value)

        return await query.execute()

    @handle_supabase_errors
    async def delete(
        self,
        table: str,
        filters: Dict[str, Any]
    ) -> Dict:
        """Delete data from a table"""
        query = self.client.from_(table).delete()

        for key, value in filters.items():
            query = query.eq(key, value)

        return await query.execute()

    @handle_supabase_errors
    async def rpc(
        self,
        function_name: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """Call a Postgres function"""
        return await self.client.rpc(function_name, params or {}).execute()

    @handle_supabase_errors
    async def admin_rpc(
        self,
        function_name: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """Call a Postgres function with admin privileges"""
        return await self.admin_client.rpc(function_name, params or {}).execute()

# Create a singleton instance
supabase = SupabaseClient()