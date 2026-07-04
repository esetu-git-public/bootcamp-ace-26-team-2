"""
Chat and document Q&A endpoints.

Handles user queries against uploaded legal documents
by orchestrating the RAG pipeline.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask")
async def ask_question():
    """
    Accept a user question and return an answer grounded in the uploaded document.
    Future: Accept ChatRequest schema, invoke RAG service, return ChatResponse.
    """
    pass