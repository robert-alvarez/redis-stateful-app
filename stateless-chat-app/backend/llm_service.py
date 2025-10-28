"""
LLM Service - Handles communication with OpenAI Responses API
IMPORTANT: This is intentionally stateless - no conversation history is maintained!
Uses the new Responses API endpoint instead of Chat Completions.
"""
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class LLMService:
    """
    Stateless LLM service that sends only the current message to OpenAI using the Responses API.
    This demonstrates the problem: each request is independent with no memory.
    """

    def __init__(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-5-mini")

    def get_response(self, user_message: str) -> str:
        """
        Send a single message to the LLM and get a response using the Responses API.

        NOTE: This is STATELESS - only the current message is sent.
        No conversation history is included, so the LLM won't remember
        anything from previous messages.

        Args:
            user_message: The current user message

        Returns:
            The LLM's response
        """
        try:
            logger.info(f"Sending stateless message to OpenAI: {user_message[:50]}...")

            # STATELESS CALL: Only sending the current message, no history!
            # Using the new Responses API with store=false to ensure no state is kept
            response = self.client.responses.create(
                model=self.model,
                input=user_message,  # Use 'input' instead of 'messages'
                store=False,  # Explicitly disable storage for stateless operation
                reasoning={"effort":"minimal"},
                max_output_tokens=200  # Higher limit for GPT-5 reasoning + output tokens
            )

            logger.info(f"OpenAI response: {response}")
            # Use the output_text helper for easy access to the response
            assistant_response = response.output_text
            logger.info(f"Assistant response content: {assistant_response}")

            return assistant_response

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise Exception(f"Error calling OpenAI API: {str(e)}")
