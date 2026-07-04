"""
Request schemas (Pydantic models).

Defines the structure and validation rules for incoming
API request payloads.
"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """
    Schema for a chat / Q&A request.
    Future: Add fields like question, document_id, session_id, etc.
    """
    pass


class UploadRequest(BaseModel):
    """
    Schema for a document upload request.
    Future: Add fields like file metadata, user_id, etc.
    """
    pass