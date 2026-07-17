"""
Chat and document Q&A endpoints.

Handles user queries against uploaded legal documents
by orchestrating the RAG pipeline. Supports optional
document_id scoping for multi-document retrieval.

Each request loads the authenticated user's FAISS index
from Supabase Storage into a temporary directory.
"""

import logging
import traceback

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.search_result import SearchResult
from app.services.faiss_index_service import FaissIndexService
from app.services.faiss_storage_service import FaissStorageService
from app.services.rag_pipeline_service import RAGPipelineService
from app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    query: str = Field(description="The user's legal question")
    document_id: str | None = Field(
        default=None,
        description="Optional document UUID to scope retrieval to a single uploaded contract",
    )


class ChatResponse(BaseModel):
    query: str = Field(description="The original user question")
    answer: str = Field(description="Generated answer from the LLM")
    context: str = Field(description="Retrieved context provided to the LLM")
    sources: list[SearchResult] = Field(default_factory=list, description="Supporting document chunks used for the answer")
    model: str = Field(description="LLM model identifier used for generation")


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
) -> ChatResponse:
    """
    Accept a user question, retrieve relevant contract clauses
    from the authenticated user's FAISS index, and return a
    generated answer grounded in the retrieved context.

    The user's FAISS index is downloaded from Supabase Storage
    into a temporary directory, loaded, queried, and cleaned up
    on every request.

    If *document_id* is provided, retrieval is scoped to chunks
    belonging to that document.  If the document does not exist,
    a 404 is returned.  If the document has no indexed chunks,
    a 400 is returned.

    When *document_id* is omitted, the entire index is searched.
    """
    faiss_storage = FaissStorageService()

    if not faiss_storage.index_exists(user_id):
        raise HTTPException(
            status_code=404,
            detail="No index found. Upload a document first.",
        )

    temp_dir = faiss_storage.create_temp_dir()
    try:
        logger.info("Downloading FAISS index for user=%s from FAISS/%s/", user_id, user_id)
        faiss_storage.download_user_index(user_id, temp_dir)
        index_path = temp_dir / "index.faiss"
        metadata_path = temp_dir / "index.pkl"
        logger.info(
            "Downloaded FAISS index for user=%s: temp_dir=%s, index.faiss exists=%s, index.pkl exists=%s",
            user_id,
            temp_dir,
            index_path.exists(),
            metadata_path.exists(),
        )
        idx_service = FaissIndexService.load(index_path, metadata_path)
        logger.info(
            "FAISS index loaded for user=%s: size=%d, dimension=%d",
            user_id,
            idx_service.size,
            idx_service._index.d if idx_service._index else 0,
        )

        # Validate document_id if provided
        if request.document_id:
            if not idx_service.document_exists(request.document_id):
                raise HTTPException(status_code=404, detail="Document not found.")

            doc_chunks = [
                m.get("document_id")
                for m in idx_service._metadata_list
                if m.get("document_id") == request.document_id
            ]
            if not doc_chunks:
                raise HTTPException(
                    status_code=400,
                    detail="Document has not been indexed.",
                )

        logger.info(
            "Chat request: user=%s, query='%s', document_id=%s",
            user_id,
            request.query[:80],
            request.document_id,
        )

        # Build retrieval and RAG pipeline with this user's index
        retrieval_service = RetrievalService(index_service=idx_service)
        rag_service = RAGPipelineService(retrieval_service=retrieval_service)
        result = rag_service.answer(request.query, document_id=request.document_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Chat pipeline failed for user %s: %s\n%s",
            user_id,
            e,
            traceback.format_exc(),
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process your question: {str(e)}",
        )
    finally:
        faiss_storage.cleanup_temp_dir(temp_dir)

    logger.info(
        "Chat response for user %s: answer_len=%d, sources=%d, model=%s",
        user_id,
        len(result.answer),
        len(result.sources),
        result.model,
    )

    return ChatResponse(
        query=result.query,
        answer=result.answer,
        context=result.context,
        sources=result.sources,
        model=result.model,
    )
