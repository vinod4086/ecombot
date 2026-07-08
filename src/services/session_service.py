"""Session service for Redis-based session persistence - Day 04 implementation"""
import json
import logging
from typing import Optional, Dict, Any
import redis
from src.config.settings import settings

logger = logging.getLogger(__name__)


class SessionService:
    """Redis-based session service for eComBot"""

    def __init__(self):
        """Initialize Redis connection"""
        self.redis_client: Optional[redis.Redis] = None
        self.initialize()

    def initialize(self) -> None:
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                decode_responses=True,
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise

    def set_session(self, session_id: str, data: Dict[str, Any], ttl: int = 86400) -> None:
        """
        Store session data in Redis.
        
        Args:
            session_id: Unique session identifier
            data: Session data dictionary
            ttl: Time to live in seconds (default: 24 hours)
        """
        try:
            self.redis_client.setex(
                f"session:{session_id}",
                ttl,
                json.dumps(data),
            )
            logger.info(f"Session stored: {session_id}")
        except Exception as e:
            logger.error(f"Failed to store session: {e}")
            raise

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve session data from Redis.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Session data dictionary or empty dict if not found
        """
        try:
            data = self.redis_client.get(f"session:{session_id}")
            if data:
                return json.loads(data)
            return {}
        except Exception as e:
            logger.error(f"Failed to retrieve session: {e}")
            return {}

    def update_session(self, session_id: str, key: str, value: Any) -> None:
        """
        Update a specific key in session data.
        
        Args:
            session_id: Unique session identifier
            key: Key to update
            value: New value
        """
        try:
            session_data = self.get_session(session_id)
            session_data[key] = value
            ttl = self.redis_client.ttl(f"session:{session_id}")
            if ttl == -1:
                ttl = 86400
            self.set_session(session_id, session_data, ttl)
            logger.info(f"Session updated: {session_id}.{key} = {value}")
        except Exception as e:
            logger.error(f"Failed to update session: {e}")
            raise

    def delete_session(self, session_id: str) -> None:
        """Delete a session from Redis"""
        try:
            self.redis_client.delete(f"session:{session_id}")
            logger.info(f"Session deleted: {session_id}")
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            raise

    def close(self) -> None:
        """Close Redis connection"""
        if self.redis_client:
            self.redis_client.close()
            logger.info("Redis connection closed")


# Global session service instance
session_service_instance: Optional[SessionService] = None


def get_session_service() -> SessionService:
    """Get or create the global session service instance"""
    global session_service_instance
    if session_service_instance is None:
        session_service_instance = SessionService()
    return session_service_instance
