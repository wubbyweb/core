# backend/app/db/redis_client.py
import redis
from typing import Optional, Any
import json
from ..core.config import settings

class RedisClient:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True  # Automatically decode responses to Python strings
        )

    def get(self, key: str) -> Optional[str]:
        """Get value from Redis"""
        try:
            return self.redis_client.get(key)
        except Exception as e:
            print(f"Redis get error: {str(e)}")
            return None

    def set(self, key: str, value: str) -> bool:
        """Set value in Redis"""
        try:
            return self.redis_client.set(key, value)
        except Exception as e:
            print(f"Redis set error: {str(e)}")
            return False

    def setex(self, key: str, expiry: int, value: str) -> bool:
        """Set value with expiration in Redis"""
        try:
            return self.redis_client.setex(key, expiry, value)
        except Exception as e:
            print(f"Redis setex error: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Redis delete error: {str(e)}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            print(f"Redis exists error: {str(e)}")
            return False

# Create a singleton instance
redis_client = RedisClient()