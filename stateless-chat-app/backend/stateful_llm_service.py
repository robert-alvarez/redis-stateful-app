"""
Stateful LLM Service - Handles communication with OpenAI API with memory

This service maintains conversation history using Redis and sends
the full conversation context with each API call.
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
from memory_service import MemoryService

load_dotenv()


class StatefulLLMService:
    """
    Stateful LLM service that maintains conversation history in Redis.

    Unlike the stateless service, this one:
    - Stores all messages in Redis by session
    - Sends full conversation history with each request
    - Enables the LLM to maintain context and remember previous exchanges
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

            # STATEFUL CALL: Send the ENTIRE conversation history!
            # This is the key difference from the stateless service
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # Full conversation history!
                max_completion_tokens=500
            )

            assistant_response = response.choices[0].message.content

            # Store the assistant's response in memory
            self.memory.add_message(session_id, "assistant", assistant_response)

            return assistant_response

        except Exception as e:
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
