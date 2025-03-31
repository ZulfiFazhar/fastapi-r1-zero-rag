from typing import List, Dict, Any, Optional
from app.core.database import db
from app.core.chroma_client import chroma
from app.core.openrouter import OpenRouterClient
from app.models.embedding import DocumentChunk
import uuid

class EmbeddingService:
    """Service for handling embedding-related operations."""
    
    async def process_document_chunks(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """Process document chunks and store them with embeddings."""
        chunk_ids = []
        
        if not chunks:
            return chunk_ids
        
        # Extract text for embedding
        texts = [chunk["text"] for chunk in chunks]
        
        # Generate embeddings
        openrouter_client = OpenRouterClient()
        embedding_response = await openrouter_client.generate_embeddings(texts)
        
        # Get embeddings from response
        embeddings = [item["embedding"] for item in embedding_response["data"]]
        
        # Process chunks and store in ChromaDB and MongoDB
        chroma_ids = []
        chroma_metadatas = []
        chroma_documents = []
        chroma_embeddings = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Generate a unique ID for the vector
            vector_id = str(uuid.uuid4())
            chroma_ids.append(vector_id)
            
            # Prepare metadata for ChromaDB
            metadata = {
                "document_id": chunk["document_id"],
                "chunk_index": i,
                **chunk["metadata"]
            }
            chroma_metadatas.append(metadata)
            
            # Add text and embedding
            chroma_documents.append(chunk["text"])
            chroma_embeddings.append(embedding)
            
            # Create document chunk in MongoDB
            doc_chunk = DocumentChunk(
                document_id=chunk["document_id"],
                chunk_text=chunk["text"],
                chunk_index=i,
                metadata=chunk["metadata"],
                vector_id=vector_id
            )
            
            # Insert into MongoDB
            result = await db.db.document_chunks.insert_one(doc_chunk.to_mongo())
            chunk_ids.append(str(result.inserted_id))
        
        # Add to ChromaDB
        chroma.collection.add(
            ids=chroma_ids,
            embeddings=chroma_embeddings,
            documents=chroma_documents,
            metadatas=chroma_metadatas
        )
        
        return chunk_ids
    
    async def get_chunks_by_document(self, document_id: str) -> List[DocumentChunk]:
        """Get all chunks for a specific document."""
        chunks = []
        cursor = db.db.document_chunks.find({"document_id": document_id}).sort("chunk_index", 1)
        
        async for doc in cursor:
            chunks.append(DocumentChunk.from_mongo(doc))
            
        return chunks
    
    async def delete_document_chunks(self, document_id: str) -> bool:
        """Delete all chunks and vectors associated with a document."""
        # Get chunks to find vector IDs
        chunks = await self.get_chunks_by_document(document_id)
        vector_ids = [chunk.vector_id for chunk in chunks if chunk.vector_id]
        
        # Delete from ChromaDB
        if vector_ids:
            chroma.collection.delete(ids=vector_ids)
        
        # Delete from MongoDB
        result = await db.db.document_chunks.delete_many({"document_id": document_id})
        return result.deleted_count > 0