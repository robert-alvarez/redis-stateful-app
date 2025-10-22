"""
Chat Application - FastAPI Backend

This application supports TWO modes:
1. STATELESS: No memory - each request is independent (demonstrates the problem)
2. STATEFUL: Redis-backed memory - maintains conversation history

This demonstrates the difference between stateless and stateful LLM applications.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ChatRequest, ChatResponse, ChatMode
from llm_service import LLMService
from memory_service import MemoryService
from stateful_llm_service import StatefulLLMService
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
stateless_service = None
stateful_service = None
memory_service = None

try:
    # Initialize stateless service
    stateless_service = LLMService()
    logger.info("Stateless LLM Service initialized successfully")

    # Initialize Redis memory service
    memory_service = MemoryService()
    logger.info("Memory Service initialized successfully")

    # Initialize stateful service with memory
    stateful_service = StatefulLLMService(memory_service)
    logger.info("Stateful LLM Service initialized successfully")

except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    # Services will be None if initialization fails


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "app": "Chat Application - Stateless vs Stateful",
        "modes": {
            "stateless": "No memory - demonstrates the problem",
            "stateful": "Redis-backed memory - maintains conversation history"
        },
        "stateless_available": stateless_service is not None,
        "stateful_available": stateful_service is not None and memory_service is not None
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - sends a message to the LLM and returns a response.

    Supports TWO modes:

    STATELESS mode:
    - Each request is independent
    - No conversation history is maintained
    - The LLM will NOT remember previous messages
    - Demonstrates the problem with no memory

    STATEFUL mode:
    - Conversation history stored in Redis by session_id
    - Full context sent with each request
    - The LLM WILL remember previous messages
    - Demonstrates proper memory management

    Args:
        request: ChatRequest with message, mode, and optional session_id

    Returns:
        ChatResponse with response, mode, and session info
    """
    try:
        logger.info(f"Received {request.mode} message: {request.message[:50]}...")

        if request.mode == ChatMode.STATELESS:
            # STATELESS MODE: No memory
            if not stateless_service:
                raise HTTPException(
                    status_code=503,
                    detail="Stateless service not available. Check your OPENAI_API_KEY."
                )

            response = stateless_service.get_response(request.message)

            logger.info(f"Generated stateless response: {response[:50]}...")

            return ChatResponse(
                response=response,
                mode=ChatMode.STATELESS,
                session_id=None,
                message_count=None
            )

        else:  # STATEFUL MODE
            # STATEFUL MODE: With memory
            if not stateful_service or not memory_service:
                raise HTTPException(
                    status_code=503,
                    detail="Stateful service not available. Check Redis connection and OPENAI_API_KEY."
                )

            # Generate session_id if not provided
            session_id = request.session_id if request.session_id else str(uuid.uuid4())

            # Get response with conversation history
            response = stateful_service.get_response(session_id, request.message)

            # Get message count
            message_count = stateful_service.get_message_count(session_id)

            logger.info(f"Generated stateful response for session {session_id[:8]}...: {response[:50]}...")

            return ChatResponse(
                response=response,
                mode=ChatMode.STATEFUL,
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
