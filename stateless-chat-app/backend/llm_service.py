"""
LLM Service - Handles communication with OpenAI API
IMPORTANT: This is intentionally stateless - no conversation history is maintained!
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMService:
    """
    Stateless LLM service that sends only the current message to OpenAI.
    This demonstrates the problem: each request is independent with no memory.
    """

    def __init__(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    def get_response(self, user_message: str) -> str:
        """
        Send a single message to the LLM and get a response.

        NOTE: This is STATELESS - only the current message is sent.
        No conversation history is included, so the LLM won't remember
        anything from previous messages.

        Args:
            user_message: The current user message

        Returns:
            The LLM's response
        """
        try:
            # STATELESS CALL: Only sending the current message, no history!
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                max_completion_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")
