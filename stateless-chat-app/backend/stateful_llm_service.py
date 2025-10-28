"""
Stateful LLM Service - Handles communication with OpenAI Responses API with memory

This service maintains conversation history using Redis and sends
the full conversation context with each API call using the new Responses API.

IMPORTANT: We use store=False to ensure Redis is the single source of truth
for conversation history, not OpenAI's internal state management.
"""
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
from memory_service import MemoryService

load_dotenv()

logger = logging.getLogger(__name__)


class StatefulLLMService:
    """
    Stateful LLM service that maintains conversation history in Redis using the Responses API.

    Unlike the stateless service, this one:
    - Stores all messages in Redis by session
    - Sends full conversation history with each request
    - Enables the LLM to maintain context and remember previous exchanges
    - Uses the Responses API endpoint
    """

    def __init__(self, memory_service: MemoryService):
        """
        Initialize OpenAI client and memory service

        Args:
            memory_service: MemoryService instance for managing conversation history
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-5")
        self.memory = memory_service

    def get_response(self, session_id: str, user_message: str) -> str:
        """
        Send a message to the LLM with full conversation history and get a response.

        This is STATEFUL - the entire conversation history is included!
        Uses the Responses API which provides better performance and lower costs.

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
            logger.info(f"Sending {len(messages)} messages to OpenAI Responses API")
            logger.info(f"Messages: {messages}")

            # Using the new Responses API with store=false to ensure Redis is the single source of truth
            # We manually manage conversation history via Redis, not OpenAI's state management
            response = self.client.responses.create(
                model=self.model,
                input=messages,  # Pass full conversation history from Redis as input
                store=False,  # Disable OpenAI storage - Redis manages our conversation history
                reasoning={"effort":"minimal"},
                max_output_tokens=200  # Higher limit for GPT-5 reasoning + output tokens
            )

            logger.info(f"OpenAI response: {response}")

            # Use the output_text helper for easy access to the response
            assistant_response = response.output_text
            logger.info(f"Assistant response content: {assistant_response}")

            # Store the assistant's response in memory
            self.memory.add_message(session_id, "assistant", assistant_response)

            return assistant_response

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise Exception(f"Error calling OpenAI API: {str(e)}")

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
