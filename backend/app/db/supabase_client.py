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
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
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

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._client:
            self._initialize_client()

    def _initialize_client(self):
        """Initialize Supabase client"""
        try:
            if settings.SUPABASE_URL and settings.SUPABASE_KEY:
                logger.info("Initializing Supabase client...")
                self._client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
                logger.info("Supabase client initialized successfully")
            else:
                logger.error("Supabase URL or Key is missing")
                raise Exception("Supabase configuration missing")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise

    @property
    def client(self) -> Client:
        """Get Supabase client"""
        if not self._client:
            raise Exception("Supabase client not initialized")
        return self._client

    @handle_supabase_errors
    def select(
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

        return query.execute()

    @handle_supabase_errors
    def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> Dict:
        """Insert data into a table"""
        return self.client.from_(table).insert(data).execute()

    @handle_supabase_errors
    def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Dict[str, Any]
    ) -> Dict:
        """Update data in a table"""
        query = self.client.from_(table).update(data)

        for key, value in filters.items():
            query = query.eq(key, value)

        return query.execute()

    @handle_supabase_errors
    def delete(
        self,
        table: str,
        filters: Dict[str, Any]
    ) -> Dict:
        """Delete data from a table"""
        query = self.client.from_(table).delete()

        for key, value in filters.items():
            query = query.eq(key, value)

        return query.execute()

    @handle_supabase_errors
    def rpc(
        self,
        function_name: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """Call a Postgres function"""
        return self.client.rpc(function_name, params or {}).execute()

    # Leaderboard specific methods
    def get_global_leaderboard(self) -> Dict:
        """Get global leaderboard data"""
        return self.rpc('get_global_leaderboard')

    def get_challenge_leaderboard(self, challenge_id: str) -> Dict:
        """Get challenge-specific leaderboard data"""
        return self.rpc(
            'get_challenge_leaderboard',
            {'challenge_id_param': challenge_id}
        )

    def get_user_challenge_rank(self, challenge_id: str, user_id: str) -> Dict:
        """Get user's rank in a specific challenge"""
        return self.rpc(
            'get_user_challenge_rank',
            {
                'challenge_id_param': challenge_id,
                'user_id_param': user_id
            }
        )

    def update_score(self, challenge_id: str, user_id: str, score: int) -> Dict:
        """Update or insert a user's score"""
        data = {
            'challenge_id': challenge_id,
            'user_id': user_id,
            'score': score,
        }
        return self.insert('score_history', data)

    def get_user_scores(self, user_id: str) -> Dict:
        """Get all scores for a specific user"""
        return self.select(
            'score_history',
            '*',
            {'user_id': user_id}
        )

    def get_challenge_scores(self, challenge_id: str) -> Dict:
        """Get all scores for a specific challenge"""
        return self.select(
            'score_history',
            '*',
            {'challenge_id': challenge_id}
        )

    def delete_scores_after_date(self, user_id: str, date: str) -> Dict:
        """Delete scores for a user after a specific date"""
        return self.delete(
            'score_history',
            {
                'user_id': user_id,
                'last_updated': {'gt': date}
            }
        )

# Create a singleton instance
supabase = SupabaseClient()
