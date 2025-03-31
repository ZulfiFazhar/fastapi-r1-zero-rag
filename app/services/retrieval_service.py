from typing import List, Dict, Any, Optional
from app.core.chroma_client import chroma
from app.core.database import db
from app.core.openrouter import OpenRouterClient
from app.models.embedding import DocumentChunk
from app.schemas.search import SearchResult

class RetrievalService:
    """Service for handling vector retrieval operations."""
    
    async def search(self, query: str, top_k: int = 5, filter_metadata: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """Search for relevant document chunks based on query."""
        # Generate query embedding
        openrouter_client = OpenRouterClient()
        embedding_response = await openrouter_client.generate_embeddings([query])
        query_embedding = embedding_response["data"][0]["embedding"]
        
        # Query ChromaDB
        results = chroma.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )
        
        # Process results
        search_results = []
        
        if results and results['ids'][0]:
            for i, vector_id in enumerate(results['ids'][0]):
                # Get score (distance)
                score = results['distances'][0][i] if 'distances' in results else 0.0
                # Convert cosine distance to similarity score (1 - distance)
                similarity_score = 1.0 - score
                
                # Get metadata
                metadata = results['metadatas'][0][i] if 'metadatas' in results else {}
                document_id = metadata.get('document_id', '')
                
                # Get text
                chunk_text = results['documents'][0][i] if 'documents' in results else ''
                
                # Find the corresponding chunk in MongoDB
                chunk = await db.db.document_chunks.find_one({"vector_id": vector_id})
                chunk_id = str(chunk['_id']) if chunk else ""
                
                search_results.append(SearchResult(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    chunk_text=chunk_text,
                    metadata=metadata,
                    score=similarity_score
                ))
        
        return search_results