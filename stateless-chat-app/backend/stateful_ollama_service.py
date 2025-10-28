"""
Stateful Ollama Service - Handles communication with local Ollama server with memory

This service maintains conversation history using Redis and sends
the full conversation context with each API call to the local Ollama server.

IMPORTANT: Redis is the single source of truth for conversation history.
"""
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
from memory_service import MemoryService

load_dotenv()

logger = logging.getLogger(__name__)


class StatefulOllamaService:
    """
    Stateful Ollama service that maintains conversation history in Redis.

    Unlike the stateless service, this one:
    - Stores all messages in Redis by session
    - Sends full conversation history with each request
    - Enables the LLM to maintain context and remember previous exchanges
    - Uses the Chat Completions API endpoint
    - Connects to a local Ollama server
    """

    def __init__(self, memory_service: MemoryService):
        """
        Initialize OpenAI client pointing to local Ollama server and memory service

        Args:
            memory_service: MemoryService instance for managing conversation history
        """
        # Ollama endpoint configuration (default: http://localhost:11434/v1)
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

        # Ollama doesn't require an API key, but the OpenAI client requires one
        # We use "ollama" as a dummy key for local Ollama
        api_key = os.getenv("OLLAMA_API_KEY", "ollama")

        self.client = OpenAI(
            base_url=ollama_base_url,
            api_key=api_key
        )

        # Model name from Ollama (e.g., qwen3:0.6b, llama3.2, mistral, etc.)
        self.model = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")
        self.memory = memory_service

        logger.info(f"Stateful Ollama Service (Chat Completions API) initialized with endpoint: {ollama_base_url}")
        logger.info(f"Using model: {self.model}")

    def get_response(self, session_id: str, user_message: str) -> str:
        """
        Send a message to the local Ollama server with full conversation history and get a response.

        This is STATEFUL - the entire conversation history is included!

        Args:
            session_id: Unique session identifier
            user_message: The current user message

        Returns:
            The LLM's response
        """
        try:
            # Add the user's message to memory
            self.memory.add_message(session_id, "user", user_message)

            # Get full conversation history
            messages = self.memory.get_messages(session_id)

            # STATEFUL CALL: Send the ENTIRE conversation history
            logger.info(f"Sending {len(messages)} messages to Ollama")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # Pass full conversation history from Redis
                temperature=0.7,
                max_tokens=500
            )

            assistant_response = response.choices[0].message.content
            logger.info(f"Ollama response: {assistant_response[:100]}...")

            # Store the assistant's response in memory
            self.memory.add_message(session_id, "assistant", assistant_response)

            return assistant_response

        except Exception as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            raise Exception(f"Error calling Ollama API: {str(e)}")

    def clear_conversation(self, session_id: str) -> None:
        """
        Clear conversation history for a session.

        Args:
            session_id: Unique session identifier
        """
        self.memory.clear_session(session_id)

    def get_message_count(self, session_id: str) -> int:
        """
        Get the number of messages in a conversation.

        Args:
            session_id: Unique session identifier

        Returns:
            Number of messages in the conversation
        """
        return self.memory.get_message_count(session_id)
