from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    filter_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class SearchResult(BaseModel):
    chunk_id: str
    document_id: str
    chunk_text: str
    metadata: Dict[str, Any]
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    total: int