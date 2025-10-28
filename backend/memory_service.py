"""
Memory Service - Manages conversation history using Redis

This service provides session-scoped working memory for chat conversations.
It stores message history in Redis with session-based keys using RedisVL's
MessageHistory for LLM-optimized conversation management.
"""
import os
import json
import logging
from typing import List, Dict, Optional
from datetime import timedelta
import redis
from redisvl.extensions.message_history import MessageHistory
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Redis-based memory service for storing conversation history using RedisVL.

    Each conversation session has a unique session_id, and messages are
    stored using MessageHistory for optimized LLM conversation management.
    Uses session_tag parameter to manage multiple concurrent sessions.
    """

    def __init__(self):
        """Initialize Redis connection and MessageHistory"""
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        redis_db = int(os.getenv("REDIS_DB", 0))
        redis_password = os.getenv("REDIS_PASSWORD", None)

        # Session TTL (Time To Live) - default 1 hour
        self.session_ttl = int(os.getenv("SESSION_TTL_SECONDS", 3600))

        # Build Redis URL
        redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"
        if redis_password:
            redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"

        try:
            # Initialize raw Redis client for utility operations
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

            # Initialize MessageHistory for LLM-optimized message storage
            # Using a single instance with session_tag for multi-session management
            self.message_history = MessageHistory(
                name="chat_history",
                redis_url=redis_url
            )
            logger.info("MessageHistory initialized successfully")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def _get_session_key(self, session_id: str) -> str:
        """Generate Redis key for a session"""
        return f"chat:session:{session_id}:messages"

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Add a message to the conversation history using MessageHistory.

        Args:
            session_id: Unique session identifier
            role: Message role ('user' or 'assistant')
            content: Message content

        Note:
            Internally maps 'assistant' role to 'llm' for MessageHistory compatibility.
        """
        # Map 'assistant' role to 'llm' for MessageHistory API
        message_history_role = "llm" if role == "assistant" else role

        message = {
            "role": message_history_role,
            "content": content
        }

        # Add message to MessageHistory with session_tag
        self.message_history.add_message(
            message=message,
            session_tag=session_id
        )

        # Set/reset expiration on the session key for TTL management
        key = self._get_session_key(session_id)
        # Get all keys associated with this session in MessageHistory
        # MessageHistory creates keys with pattern: {name}:{session_tag}:*
        pattern = f"chat_history:{session_id}:*"
        session_keys = self.redis_client.keys(pattern)
        for key in session_keys:
            self.redis_client.expire(key, self.session_ttl)

        logger.info(f"Added {role} message to session {session_id} using MessageHistory")

    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Retrieve conversation history for a session using MessageHistory.

        Args:
            session_id: Unique session identifier
            limit: Optional limit on number of recent messages to return

        Returns:
            List of messages in OpenAI format [{"role": "user", "content": "..."}, ...]

        Note:
            Internally maps 'llm' role back to 'assistant' for backwards compatibility.
        """
        try:
            # Get messages from MessageHistory
            if limit:
                # Get last N messages
                messages = self.message_history.get_recent(
                    top_k=limit,
                    session_tag=session_id
                )
            else:
                # Get all messages by using a very large top_k
                # MessageHistory doesn't have a "get all" option, so we use a large number
                messages = self.message_history.get_recent(
                    session_tag=session_id
                )

            # Map 'llm' role back to 'assistant' for backwards compatibility
            for msg in messages:
                if msg.get("role") == "llm":
                    msg["role"] = "assistant"

            logger.info(f"Retrieved {len(messages)} messages from session {session_id} using MessageHistory")
            return messages

        except Exception as e:
            logger.warning(f"Error retrieving messages from MessageHistory: {e}")
            # Return empty list if no messages found
            return []

    def clear_session(self, session_id: str) -> None:
        """
        Clear all messages for a session using MessageHistory.

        Args:
            session_id: Unique session identifier
        """
        # Delete all keys associated with this session in MessageHistory
        # MessageHistory creates keys with pattern: {name}:{session_tag}:*
        pattern = f"chat_history:{session_id}:*"
        session_keys = self.redis_client.keys(pattern)

        if session_keys:
            self.redis_client.delete(*session_keys)
            logger.info(f"Cleared {len(session_keys)} keys for session {session_id}")
        else:
            logger.info(f"No keys found for session {session_id}")

    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists in Redis using MessageHistory key pattern.

        Args:
            session_id: Unique session identifier

        Returns:
            True if session has messages, False otherwise
        """
        # Check for keys with MessageHistory pattern
        pattern = f"chat_history:{session_id}:*"
        session_keys = self.redis_client.keys(pattern)
        return len(session_keys) > 0

    def get_message_count(self, session_id: str) -> int:
        """
        Get the number of messages in a session from MessageHistory.

        Args:
            session_id: Unique session identifier

        Returns:
            Number of messages in the session
        """
        try:
            # Get all messages and count them
            messages = self.get_messages(session_id)
            return len(messages)
        except Exception as e:
            logger.warning(f"Error counting messages for session {session_id}: {e}")
            return 0
