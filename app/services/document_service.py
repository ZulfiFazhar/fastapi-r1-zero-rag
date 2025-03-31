from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime

from app.core.database import db
from app.models.document import Document
from app.schemas.document import DocumentCreate
from app.services.embedding_service import EmbeddingService
from app.utils.chunking import chunk_document

class DocumentService:
    """Service for handling document-related operations."""
    
    async def create_document(self, document_data: DocumentCreate, process_embeddings: bool = True) -> Document:
        """Create a new document and optionally process it for embeddings."""
        document = Document(
            title=document_data.title,
            content=document_data.content,
            metadata=document_data.metadata
        )
        
        # Insert document into MongoDB
        result = await db.db.documents.insert_one(document.to_mongo())
        document.id = result.inserted_id
        
        # Process document for embeddings if requested
        if process_embeddings:
            embedding_service = EmbeddingService()
            document_chunks = chunk_document(
                document_id=str(document.id),
                text=document.content,
                metadata={
                    "title": document.title,
                    **document.metadata
                }
            )
            
            # Process chunks and store embeddings
            chunk_ids = await embedding_service.process_document_chunks(document_chunks)
            
            # Update document with chunk IDs
            document.chunk_ids = chunk_ids
            await db.db.documents.update_one(
                {"_id": document.id},
                {"$set": {"chunk_ids": chunk_ids}}
            )
        
        return document
    
    async def get_documents(self, skip: int = 0, limit: int = 10, 
                           filters: Optional[Dict[str, Any]] = None) -> List[Document]:
        """Get all documents with pagination and filtering."""
        filters = filters or {}
        documents = []
        cursor = db.db.documents.find(filters).skip(skip).limit(limit).sort("created_at", -1)
        
        async for doc in cursor:
            documents.append(Document.from_mongo(doc))
            
        return documents
    
    async def count_documents(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count documents matching filters."""
        filters = filters or {}
        return await db.db.documents.count_documents(filters)
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a single document by id."""
        doc = await db.db.documents.find_one({"_id": ObjectId(document_id)})
        if doc:
            return Document.from_mongo(doc)
        return None
    
    async def update_document(self, document_id: str, document_data: DocumentCreate, 
                             reprocess_embeddings: bool = True) -> Optional[Document]:
        """Update a document and optionally reprocess embeddings."""
        # Get existing document to access chunk IDs
        existing_document = await self.get_document(document_id)
        if not existing_document:
            return None
        
        update_data = {
            "title": document_data.title,
            "content": document_data.content,
            "metadata": document_data.metadata,
            "updated_at": datetime.utcnow()
        }
        
        # Update document in MongoDB
        result = await db.db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": update_data}
        )
        
        # Reprocess embeddings if content changed and reprocessing is requested
        if reprocess_embeddings and result.modified_count:
            embedding_service = EmbeddingService()
            
            # Delete existing chunks and their vectors
            if existing_document.chunk_ids:
                await embedding_service.delete_document_chunks(str(existing_document.id))
            
            # Create new chunks
            document_chunks = chunk_document(
                document_id=document_id,
                text=document_data.content,
                metadata={
                    "title": document_data.title,
                    **document_data.metadata
                }
            )
            
            # Process new chunks and store embeddings
            chunk_ids = await embedding_service.process_document_chunks(document_chunks)
            
            # Update document with new chunk IDs
            await db.db.documents.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": {"chunk_ids": chunk_ids}}
            )
            
            update_data["chunk_ids"] = chunk_ids
        
        if result.modified_count:
            return await self.get_document(document_id)
        
        return None
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and its associated chunks and vectors."""
        # Delete associated chunks and vectors first
        embedding_service = EmbeddingService()
        await embedding_service.delete_document_chunks(document_id)
        
        # Delete the document
        result = await db.db.documents.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0