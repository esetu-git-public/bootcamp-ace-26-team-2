"""
Health check endpoint.

Provides a simple liveness probe for monitoring
and container orchestration systems.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Return application health status.
    Future: Add dependency checks (DB, vector store, etc.).
    """
    return {"status": "healthy", "version": "0.1.0"}