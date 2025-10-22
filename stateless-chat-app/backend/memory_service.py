"""
Memory Service - Manages conversation history using Redis

This service provides session-scoped working memory for chat conversations.
It stores message history in Redis with session-based keys.
"""
import os
import json
import logging
from typing import List, Dict, Optional
from datetime import timedelta
import redis
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Redis-based memory service for storing conversation history.

    Each conversation session has a unique session_id, and messages are
    stored as a list in Redis with automatic expiration.
    """

    def __init__(self):
        """Initialize Redis connection"""
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_db = int(os.getenv("REDIS_DB", 0))
        redis_password = os.getenv("REDIS_PASSWORD", None)

        # Session TTL (Time To Live) - default 1 hour
        self.session_ttl = int(os.getenv("SESSION_TTL_SECONDS", 3600))

        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True  # Automatically decode bytes to strings
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def _get_session_key(self, session_id: str) -> str:
        """Generate Redis key for a session"""
        return f"chat:session:{session_id}:messages"

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Add a message to the conversation history.

        Args:
            session_id: Unique session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        key = self._get_session_key(session_id)

        message = {
            "role": role,
            "content": content
        }

        # Append message to the list
        self.redis_client.rpush(key, json.dumps(message))

        # Set/reset expiration
        self.redis_client.expire(key, self.session_ttl)

        logger.info(f"Added {role} message to session {session_id}")

    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Retrieve conversation history for a session.

        Args:
            session_id: Unique session identifier
            limit: Optional limit on number of recent messages to return

        Returns:
            List of messages in OpenAI format [{"role": "user", "content": "..."}, ...]
        """
        key = self._get_session_key(session_id)

        # Get messages from Redis
        if limit:
            # Get last N messages
            raw_messages = self.redis_client.lrange(key, -limit, -1)
        else:
            # Get all messages
            raw_messages = self.redis_client.lrange(key, 0, -1)

        # Parse JSON messages
        messages = [json.loads(msg) for msg in raw_messages]

        logger.info(f"Retrieved {len(messages)} messages from session {session_id}")
        return messages

    def clear_session(self, session_id: str) -> None:
        """
        Clear all messages for a session.

        Args:
            session_id: Unique session identifier
        """
        key = self._get_session_key(session_id)
        self.redis_client.delete(key)
        logger.info(f"Cleared session {session_id}")

    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists in Redis.

        Args:
            session_id: Unique session identifier

        Returns:
            True if session has messages, False otherwise
        """
        key = self._get_session_key(session_id)
        return self.redis_client.exists(key) > 0

    def get_message_count(self, session_id: str) -> int:
        """
        Get the number of messages in a session.

        Args:
            session_id: Unique session identifier

        Returns:
            Number of messages in the session
        """
        key = self._get_session_key(session_id)
        return self.redis_client.llen(key)
