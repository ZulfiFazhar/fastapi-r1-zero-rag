from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from app.schemas.embedding import DocumentChunkResponse, ChunkList
from app.services.embedding_service import EmbeddingService

router = APIRouter()

@router.get("/chunks/{document_id}", response_model=ChunkList)
async def get_document_chunks(
    document_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get all chunks for a specific document."""
    embedding_service = EmbeddingService()
    chunks = await embedding_service.get_chunks_by_document(document_id)
    
    # Apply pagination manually since we're getting all chunks first
    # (In a real app, you'd modify the service to handle pagination directly)
    total = len(chunks)
    paginated_chunks = chunks[skip:skip+limit]
    
    return ChunkList(
        chunks=paginated_chunks,
        total=total,
        page=(skip // limit) + 1,
        size=limit
    )