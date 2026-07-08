"""History service for conversation persistence - Day 04 implementation"""
import json
import logging
from typing import List, Dict, Any
from datetime import datetime
from src.services.db import get_database

logger = logging.getLogger(__name__)


class HistoryService:
    """Service for storing and retrieving conversation history from PostgreSQL"""

    def __init__(self):
        """Initialize history service"""
        self.db = get_database()

    def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_calls: List[Dict[str, Any]] = None,
    ) -> int:
        """
        Save a message to conversation history.
        
        Args:
            session_id: Unique session identifier
            role: Message role (user, assistant, system)
            content: Message content
            tool_calls: Optional tool calls metadata
            
        Returns:
            ID of inserted record
        """
        try:
            query = """
                INSERT INTO session_history 
                (session_id, role, content, tool_calls, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """
            tool_calls_json = json.dumps(tool_calls) if tool_calls else None
            result = self.db.execute_query(
                query,
                (session_id, role, content, tool_calls_json, datetime.utcnow()),
            )
            logger.info(f"Message saved to history: session={session_id}, role={role}")
            return result[0]["id"] if result else None
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            raise

    def get_conversation_history(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a session.
        
        Args:
            session_id: Unique session identifier
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages in chronological order
        """
        try:
            query = """
                SELECT id, session_id, role, content, tool_calls, created_at
                FROM session_history
                WHERE session_id = %s
                ORDER BY created_at ASC
                LIMIT %s
            """
            results = self.db.execute_query(query, (session_id, limit))
            logger.info(f"Retrieved {len(results)} messages from history")
            return results
        except Exception as e:
            logger.error(f"Failed to retrieve history: {e}")
            return []

    def clear_history(self, session_id: str) -> None:
        """Clear all messages for a session"""
        try:
            query = "DELETE FROM session_history WHERE session_id = %s"
            self.db.execute_update(query, (session_id,))
            logger.info(f"History cleared for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            raise


# Global history service instance
history_service_instance: HistoryService = HistoryService()


def get_history_service() -> HistoryService:
    """Get the history service instance"""
    return history_service_instance
