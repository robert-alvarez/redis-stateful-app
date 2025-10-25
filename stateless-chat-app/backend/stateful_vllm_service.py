"""
Stateful vLLM Service - Handles communication with local vLLM server using Responses API with memory

This service maintains conversation history using Redis and sends
the full conversation context with each API call to the local vLLM server.

IMPORTANT: We use store=False to ensure Redis is the single source of truth
for conversation history, not vLLM's internal state management.
"""
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
from memory_service import MemoryService

load_dotenv()

logger = logging.getLogger(__name__)


class StatefulVLLMService:
    """
    Stateful vLLM service that maintains conversation history in Redis using the Responses API.

    Unlike the stateless service, this one:
    - Stores all messages in Redis by session
    - Sends full conversation history with each request
    - Enables the LLM to maintain context and remember previous exchanges
    - Uses the Responses API endpoint
    - Connects to a local vLLM server instead of OpenAI
    """

    def __init__(self, memory_service: MemoryService):
        """
        Initialize OpenAI client pointing to local vLLM server and memory service

        Args:
            memory_service: MemoryService instance for managing conversation history
        """
        # vLLM endpoint configuration
        vllm_base_url = os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1")

        # vLLM doesn't require an API key, but the OpenAI client requires one
        # We can use "EMPTY" or a dummy key for local vLLM
        api_key = os.getenv("VLLM_API_KEY", "EMPTY")

        self.client = OpenAI(
            base_url=vllm_base_url,
            api_key=api_key
        )

        # Model name from vLLM server (e.g., the model you're hosting)
        self.model = os.getenv("VLLM_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
        self.memory = memory_service

        logger.info(f"Stateful vLLM Service (Responses API) initialized with endpoint: {vllm_base_url}")
        logger.info(f"Using model: {self.model}")

    def get_response(self, session_id: str, user_message: str) -> str:
        """
        Send a message to the local vLLM server with full conversation history and get a response.

        This is STATEFUL - the entire conversation history is included!
        Uses the Responses API which provides better performance.

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

            # STATEFUL CALL: Send the ENTIRE conversation history using Responses API
            # The Responses API accepts messages in the same format as Chat Completions
            logger.info(f"Sending {len(messages)} messages to vLLM Responses API")
            logger.info(f"Messages: {messages}")

            # Using the Responses API with store=false to ensure Redis is the single source of truth
            # We manually manage conversation history via Redis, not vLLM's state management
            response = self.client.responses.create(
                model=self.model,
                input=messages,  # Pass full conversation history from Redis as input
                store=False,  # Disable vLLM storage - Redis manages our conversation history
                max_output_tokens=2500  # Higher limit for reasoning + output tokens
            )

            logger.info(f"vLLM response: {response}")

            # Use the output_text helper for easy access to the response
            assistant_response = response.output_text
            logger.info(f"Assistant response content: {assistant_response}")

            # Store the assistant's response in memory
            self.memory.add_message(session_id, "assistant", assistant_response)

            return assistant_response

        except Exception as e:
            logger.error(f"Error calling vLLM API: {str(e)}")
            raise Exception(f"Error calling vLLM API: {str(e)}")

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
