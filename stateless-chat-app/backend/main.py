"""
Chat Application - FastAPI Backend

This application supports TWO modes:
1. STATELESS: No memory - each request is independent (demonstrates the problem)
2. STATEFUL: Redis-backed memory - maintains conversation history

This demonstrates the difference between stateless and stateful LLM applications.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ChatRequest, ChatResponse, ChatMode, Provider
from llm_service import LLMService
from memory_service import MemoryService
from stateful_llm_service import StatefulLLMService
from ollama_service import OllamaService
from stateful_ollama_service import StatefulOllamaService
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Chat API - Stateless vs Stateful",
    description="A chat application demonstrating stateless and stateful LLM modes",
    version="2.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
# ChatGPT services (Responses API)
stateless_service = None
stateful_service = None
# Ollama services (Chat Completions API) - OPTIONAL
ollama_stateless_service = None
ollama_stateful_service = None
# Shared services
memory_service = None

try:
    # Initialize ChatGPT services (Responses API)
    stateless_service = LLMService()
    logger.info("ChatGPT Stateless Service initialized successfully")

    # Initialize Redis memory service
    memory_service = MemoryService()
    logger.info("Memory Service initialized successfully")

    # Initialize ChatGPT stateful service with memory
    stateful_service = StatefulLLMService(memory_service)
    logger.info("ChatGPT Stateful Service initialized successfully")

    # Initialize Ollama services (local inference) - OPTIONAL
    try:
        ollama_stateless_service = OllamaService()
        logger.info("Ollama Stateless Service initialized successfully")

        ollama_stateful_service = StatefulOllamaService(memory_service)
        logger.info("Ollama Stateful Service initialized successfully")
    except Exception as ollama_error:
        logger.warning(f"Ollama services not available: {ollama_error}")
        logger.info("Ollama services are optional. ChatGPT services will still work.")

except Exception as e:
    logger.error(f"Failed to initialize core services: {e}")
    # Services will be None if initialization fails


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "app": "Redis Memory Magic - Chat API Playground",
        "modes": {
            "stateless": "No memory - each message is independent",
            "stateful": "Redis-backed memory - maintains conversation history"
        },
        "providers": {
            "chatgpt": "OpenAI ChatGPT API (cloud)",
            "ollama": "Ollama local inference (on-premises)"
        },
        "services_available": {
            "chatgpt": {
                "stateless": stateless_service is not None,
                "stateful": stateful_service is not None and memory_service is not None
            },
            "ollama": {
                "stateless": ollama_stateless_service is not None,
                "stateful": ollama_stateful_service is not None and memory_service is not None
            }
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - sends a message to the LLM and returns a response.

    Supports TWO modes with seamless toggling:

    STATELESS mode:
    - Messages ARE logged to Redis (for seamless mode switching)
    - Only current message sent to API (no history)
    - The LLM will NOT remember previous messages
    - Demonstrates the problem with no memory
    - Allows toggling to stateful mode without losing history

    STATEFUL mode:
    - Messages logged to Redis AND full history sent to API
    - Full conversation context sent with each request
    - The LLM WILL remember previous messages
    - Demonstrates proper memory management

    Seamless Toggling:
    - Session ID maintained across both modes
    - Messages always logged to enable switching without restart
    - Toggle between modes anytime during conversation

    Args:
        request: ChatRequest with message, mode, and optional session_id

    Returns:
        ChatResponse with response, mode, and session info
    """
    try:
        logger.info(f"Received {request.mode} message from {request.provider}: {request.message[:50]}...")

        # Generate session_id if not provided
        session_id = request.session_id if request.session_id else str(uuid.uuid4())

        # Select the appropriate service based on provider and mode
        if request.mode == ChatMode.STATELESS:
            # STATELESS MODE: Store in Redis but DON'T send history to API
            # This allows seamless toggling to stateful mode later

            # Select service based on provider
            if request.provider == Provider.CHATGPT:
                service = stateless_service
                service_name = "ChatGPT"
            else:  # Provider.OLLAMA
                service = ollama_stateless_service
                service_name = "Ollama"

            if not service:
                raise HTTPException(
                    status_code=503,
                    detail=f"Stateless {service_name} service not available. Check configuration."
                )

            # Store user message in Redis (if memory service available)
            if memory_service:
                memory_service.add_message(session_id, "user", request.message)

            # Call API with ONLY the current message (no history)
            response = service.get_response(request.message)

            # Store assistant response in Redis (if memory service available)
            if memory_service:
                memory_service.add_message(session_id, "assistant", response)
                message_count = memory_service.get_message_count(session_id)
            else:
                message_count = None

            logger.info(f"Generated stateless response using {service_name} (logged to session {session_id[:8]}...): {response[:50]}...")

            return ChatResponse(
                response=response,
                mode=ChatMode.STATELESS,
                provider=request.provider,
                session_id=session_id,
                message_count=message_count
            )

        else:  # STATEFUL MODE
            # STATEFUL MODE: With memory

            # Select service based on provider
            if request.provider == Provider.CHATGPT:
                service = stateful_service
                service_name = "ChatGPT"
            else:  # Provider.OLLAMA
                service = ollama_stateful_service
                service_name = "Ollama"

            if not service or not memory_service:
                raise HTTPException(
                    status_code=503,
                    detail=f"Stateful {service_name} service not available. Check Redis connection and configuration."
                )

            # Get response with conversation history
            response = service.get_response(session_id, request.message)

            # Get message count
            message_count = service.get_message_count(session_id)

            logger.info(f"Generated stateful response using {service_name} for session {session_id[:8]}...: {response[:50]}...")

            return ChatResponse(
                response=response,
                mode=ChatMode.STATEFUL,
                provider=request.provider,
                session_id=session_id,
                message_count=message_count
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing your message: {str(e)}"
        )


@app.post("/clear-session")
async def clear_session(session_id: str):
    """
    Clear conversation history for a session.

    Args:
        session_id: Session ID to clear

    Returns:
        Success message
    """
    if not memory_service:
        raise HTTPException(
            status_code=503,
            detail="Memory service not available. Check Redis connection."
        )

    try:
        memory_service.clear_session(session_id)
        logger.info(f"Cleared session {session_id}")
        return {"status": "success", "message": f"Session {session_id} cleared"}
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing session: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9090)
