from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentList
from app.services.document_service import DocumentService

router = APIRouter()

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(document: DocumentCreate, process_embeddings: bool = True):
    """Create a new document and optionally process it for embeddings."""
    document_service = DocumentService()
    created_document = await document_service.create_document(document, process_embeddings)
    return created_document

@router.get("/", response_model=DocumentList)
async def read_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    title: Optional[str] = None
):
    """Get all documents with pagination and optional filtering."""
    document_service = DocumentService()
    
    # Build filters
    filters = {}
    if title:
        filters["title"] = {"$regex": title, "$options": "i"}  # Case-insensitive search
    
    # Get documents
    documents = await document_service.get_documents(skip, limit, filters)
    
    # Count total
    total = await document_service.count_documents(filters)
    
    return DocumentList(
        documents=documents,
        total=total,
        page=(skip // limit) + 1,
        size=limit
    )

@router.get("/{document_id}", response_model=DocumentResponse)
async def read_document(document_id: str):
    """Get a specific document by ID."""
    document_service = DocumentService()
    document = await document_service.get_document(document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
        
    return document

@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(document_id: str, document: DocumentCreate, reprocess_embeddings: bool = True):
    """Update a document and optionally reprocess embeddings."""
    document_service = DocumentService()
    updated_document = await document_service.update_document(
        document_id, document, reprocess_embeddings
    )
    
    if not updated_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
        
    return updated_document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str):
    """Delete a document and its associated chunks and vectors."""
    document_service = DocumentService()
    deleted = await document_service.delete_document(document_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
        
    return None