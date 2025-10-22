"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ChatMode(str, Enum):
    """Chat mode enum"""
    STATELESS = "stateless"
    STATEFUL = "stateful"


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    mode: ChatMode = Field(default=ChatMode.STATELESS, description="Chat mode: stateless or stateful")
    session_id: Optional[str] = Field(default=None, description="Session ID for stateful mode")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="LLM generated response")
    mode: ChatMode = Field(..., description="Mode used for this response")
    session_id: Optional[str] = Field(default=None, description="Session ID (for stateful mode)")
    message_count: Optional[int] = Field(default=None, description="Total messages in conversation (stateful only)")
