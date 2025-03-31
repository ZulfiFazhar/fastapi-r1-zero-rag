from fastapi import APIRouter, status
from app.schemas.search import SearchQuery, SearchResponse
from app.services.retrieval_service import RetrievalService

router = APIRouter()

@router.post("/", response_model=SearchResponse)
async def search_documents(query: SearchQuery):
    """Search for relevant document chunks based on query."""
    retrieval_service = RetrievalService()
    results = await retrieval_service.search(
        query=query.query,
        top_k=query.top_k,
        filter_metadata=query.filter_metadata
    )
    
    return SearchResponse(
        results=results,
        query=query.query,
        total=len(results)
    )
