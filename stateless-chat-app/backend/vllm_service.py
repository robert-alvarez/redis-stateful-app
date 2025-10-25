"""
vLLM Service - Handles communication with local vLLM server using Responses API
IMPORTANT: This is intentionally stateless - no conversation history is maintained!
"""
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class VLLMService:
    """
    Stateless vLLM service that sends only the current message to a local vLLM server.
    This demonstrates the problem: each request is independent with no memory.

    vLLM provides an OpenAI-compatible API, including support for the Responses API.
    """

    def __init__(self):
        """Initialize OpenAI client pointing to local vLLM server"""
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

        logger.info(f"vLLM Service (Responses API) initialized with endpoint: {vllm_base_url}")
        logger.info(f"Using model: {self.model}")

    def get_response(self, user_message: str) -> str:
        """
        Send a single message to the local vLLM server and get a response using Responses API.

        NOTE: This is STATELESS - only the current message is sent.
        No conversation history is included, so the LLM won't remember
        anything from previous messages.

        Args:
            user_message: The current user message

        Returns:
            The LLM's response
        """
        try:
            logger.info(f"Sending stateless message to vLLM (Responses API): {user_message[:50]}...")

            # STATELESS CALL: Only sending the current message, no history!
            # Using the Responses API with store=false to ensure no state is kept
            response = self.client.responses.create(
                model=self.model,
                input=user_message,  # Use 'input' instead of 'messages'
                store=False,  # Explicitly disable storage for stateless operation
                max_output_tokens=2500  # Higher limit for reasoning + output tokens
            )

            logger.info(f"vLLM response: {response}")
            # Use the output_text helper for easy access to the response
            assistant_response = response.output_text
            logger.info(f"Assistant response content: {assistant_response}")

            return assistant_response

        except Exception as e:
            logger.error(f"Error calling vLLM API: {str(e)}")
            raise Exception(f"Error calling vLLM API: {str(e)}")
