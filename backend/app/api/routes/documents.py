"""
Document management endpoints.

Provides authenticated listing and deletion of uploaded documents
backed by Supabase Storage and the documents table.
"""

import logging
import traceback

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.services.document_db_service import DocumentDBService
from app.services.storage_service import StorageService
from app.services.faiss_index_service import FaissIndexService
from app.services.faiss_storage_service import FaissStorageService
from app.services.contract_analysis_service import ContractAnalysisService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentResponse(BaseModel):
    id: str = Field(description="Primary key UUID of the document record")
    document_id: str = Field(description="UUID used for FAISS multi-document retrieval")
    filename: str = Field(description="Original filename")
    storage_path: str = Field(description="Path in the contracts bucket")
    file_size: int = Field(description="File size in bytes")
    indexed: bool = Field(description="Whether the document has been indexed")
    uploaded_at: str = Field(description="ISO 8601 upload timestamp")


@router.get("", response_model=list[DocumentResponse])
async def list_documents(user_id: str = Depends(get_current_user)) -> list[DocumentResponse]:
    """
    Return all documents belonging to the authenticated user.

    Results are ordered by upload date descending.
    """
    db = DocumentDBService()
    docs = db.get_user_documents(user_id)
    return [
        DocumentResponse(
            id=doc["id"],
            document_id=doc["document_id"],
            filename=doc["filename"],
            storage_path=doc["storage_path"],
            file_size=doc["file_size"],
            indexed=doc["indexed"],
            uploaded_at=doc["uploaded_at"],
        )
        for doc in docs
    ]


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    user_id: str = Depends(get_current_user),
) -> None:
    """
    Delete a document by its primary key UUID.

    Verifies ownership, deletes the file from Supabase Storage,
    then removes the row from the documents table.
    """
    db = DocumentDBService()

    doc = db.get_document(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    if doc["user_id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete this document.",
        )

    try:
        storage = StorageService()
        storage.delete_file(doc["storage_path"])
    except Exception as e:
        logger.error(
            "Failed to delete file from storage: path=%s, error=%s\n%s",
            doc["storage_path"],
            e,
            traceback.format_exc(),
        )

    db.delete_document(document_id)


class HealthResponse(BaseModel):
    health_score: float = Field(description="Contract health score from 0.0 to 10.0")
    risk_level: str = Field(description="One of: Low, Medium, High, Critical")
    present_clauses: list[str] = Field(default_factory=list, description="Clauses detected in the document")
    missing_clauses: list[str] = Field(default_factory=list, description="Important clauses not found")
    deductions: list[dict] = Field(default_factory=list, description="Penalty deductions for each missing clause with weight")
    recommendations: list[str] = Field(default_factory=list, description="Suggestions based on missing clauses")


@router.get("/{document_id}/health", response_model=HealthResponse)
async def document_health(
    document_id: str,
    user_id: str = Depends(get_current_user),
) -> HealthResponse:
    """
    Analyze a document's clause coverage and return a health assessment.

    Downloads the authenticated user's FAISS index from Supabase Storage,
    retrieves the document's chunk texts, runs keyword-based clause
    detection, computes a health score, and generates recommendations
    for missing clauses.
    """
    logger.info("[Health] user=%s document_id=%s", user_id, document_id)

    faiss_storage = FaissStorageService()

    exists = faiss_storage.index_exists(user_id)
    logger.info("[Health] index_exists=%s", exists)
    if not exists:
        return HealthResponse(
            health_score=0.0,
            risk_level="Critical",
            present_clauses=[],
            missing_clauses=list(ContractAnalysisService.CLAUSE_PATTERNS.keys()),
            recommendations=[],
        )

    temp_dir = faiss_storage.create_temp_dir()
    try:
        faiss_storage.download_user_index(user_id, temp_dir)
        index_faiss = temp_dir / "index.faiss"
        index_pkl = temp_dir / "index.pkl"
        logger.info(
            "[Health] Download: faiss_exists=%s (size=%d) pkl_exists=%s (size=%d)",
            index_faiss.exists(),
            index_faiss.stat().st_size if index_faiss.exists() else 0,
            index_pkl.exists(),
            index_pkl.stat().st_size if index_pkl.exists() else 0,
        )

        idx_service = FaissIndexService.load(index_faiss, index_pkl)
        logger.info(
            "[Health] Load: vectors=%d docs=%d",
            idx_service.size,
            len(idx_service.get_unique_document_ids()),
        )

        doc_exists = idx_service.document_exists(document_id)
        logger.info("[Health] document_exists(%s)=%s", document_id, doc_exists)
        if not doc_exists:
            return HealthResponse(
                health_score=0.0,
                risk_level="Critical",
                present_clauses=[],
                missing_clauses=list(ContractAnalysisService.CLAUSE_PATTERNS.keys()),
                recommendations=[],
            )

        chunks = idx_service.get_chunks_by_document_id(document_id)
        logger.info("[Health] chunks=%d", len(chunks))
        if chunks:
            logger.info("[Health] first_chunk: len=%d preview=%s", len(chunks[0]), chunks[0][:200])
        else:
            return HealthResponse(
                health_score=0.0,
                risk_level="Critical",
                present_clauses=[],
                missing_clauses=list(ContractAnalysisService.CLAUSE_PATTERNS.keys()),
                recommendations=[],
            )

        combined = " ".join(chunks)
        logger.info("[Health] analyze_input: chunks=%d text_len=%d", len(chunks), len(combined))
        analyzer = ContractAnalysisService()
        result = analyzer.analyze(chunks)
        logger.info(
            "[Health] result: score=%s risk=%s missing=%d",
            result.get("health_score"),
            result.get("risk_level"),
            len(result.get("missing_clauses", [])),
        )

        return HealthResponse(**result)

    except Exception:
        logger.error("[Health] pipeline failed", exc_info=True)
        return HealthResponse(
            health_score=0.0,
            risk_level="Critical",
            present_clauses=[],
            missing_clauses=list(ContractAnalysisService.CLAUSE_PATTERNS.keys()),
            recommendations=[],
        )
    finally:
        faiss_storage.cleanup_temp_dir(temp_dir)
