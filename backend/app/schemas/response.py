"""
Response schemas (Pydantic models).

Defines the structure of API responses to ensure
consistent serialization across all endpoints.
"""

from pydantic import BaseModel
from typing import Optional


class HealthResponse(BaseModel):
    """Response schema for the health check endpoint."""
    status: str
    version: str


class ChatResponse(BaseModel):
    """
    Response schema for a chat / Q&A request.
    Future: Add fields like answer, sources, confidence, etc.
    """
    pass


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    detail: str
    error_code: Optional[str] = None