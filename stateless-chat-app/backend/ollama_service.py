"""
Ollama Service - Handles communication with local Ollama server using Chat Completions API
IMPORTANT: This is intentionally stateless - no conversation history is maintained!
"""
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class OllamaService:
    """
    Stateless Ollama service that sends only the current message to a local Ollama server.
    This demonstrates the problem: each request is independent with no memory.

    Ollama provides an OpenAI-compatible API endpoint.
    """

    def __init__(self):
        """Initialize OpenAI client pointing to local Ollama server"""
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

        logger.info(f"Ollama Service (Chat Completions API) initialized with endpoint: {ollama_base_url}")
        logger.info(f"Using model: {self.model}")

    def get_response(self, user_message: str) -> str:
        """
        Send a single message to the local Ollama server and get a response.

        NOTE: This is STATELESS - only the current message is sent.
        No conversation history is included, so the LLM won't remember
        anything from previous messages.

        Args:
            user_message: The current user message

        Returns:
            The LLM's response
        """
        try:
            logger.info(f"Sending stateless message to Ollama: {user_message[:50]}...")

            # STATELESS CALL: Only sending the current message, no history!
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500
            )

            assistant_response = response.choices[0].message.content
            logger.info(f"Ollama response: {assistant_response[:100]}...")

            return assistant_response

        except Exception as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            raise Exception(f"Error calling Ollama API: {str(e)}")
