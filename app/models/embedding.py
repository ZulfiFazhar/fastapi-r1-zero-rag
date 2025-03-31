from datetime import datetime
from bson import ObjectId
from typing import Optional, Dict, Any, List

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class DocumentChunk:
    def __init__(self, document_id: str, chunk_text: str, chunk_index: int,
                 metadata: Optional[Dict[str, Any]] = None,
                 id: Optional[PyObjectId] = None, created_at: Optional[datetime] = None,
                 vector_id: Optional[str] = None):
        self.id = id or PyObjectId()
        self.document_id = document_id
        self.chunk_text = chunk_text
        self.chunk_index = chunk_index
        self.metadata = metadata or {}
        self.vector_id = vector_id
        self.created_at = created_at or datetime.utcnow()
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> 'DocumentChunk':
        """Convert MongoDB document to DocumentChunk object."""
        if not data:
            return None
        
        chunk = cls(
            id=data.get('_id'),
            document_id=data.get('document_id'),
            chunk_text=data.get('chunk_text'),
            chunk_index=data.get('chunk_index'),
            metadata=data.get('metadata'),
            vector_id=data.get('vector_id'),
            created_at=data.get('created_at')
        )
        return chunk
    
    def to_mongo(self) -> Dict[str, Any]:
        """Convert DocumentChunk object to MongoDB document."""
        return {
            "document_id": self.document_id,
            "chunk_text": self.chunk_text,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata,
            "vector_id": self.vector_id,
            "created_at": self.created_at
        }