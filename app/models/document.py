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

class Document:
    def __init__(self, title: str, content: str, metadata: Optional[Dict[str, Any]] = None,
                 id: Optional[PyObjectId] = None, created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None, chunk_ids: Optional[List[str]] = None):
        self.id = id or PyObjectId()
        self.title = title
        self.content = content
        self.metadata = metadata or {}
        self.chunk_ids = chunk_ids or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> 'Document':
        """Convert MongoDB document to Document object."""
        if not data:
            return None
        
        document = cls(
            id=data.get('_id'),
            title=data.get('title'),
            content=data.get('content'),
            metadata=data.get('metadata'),
            chunk_ids=data.get('chunk_ids'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
        return document
    
    def to_mongo(self) -> Dict[str, Any]:
        """Convert Document object to MongoDB document."""
        return {
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
            "chunk_ids": self.chunk_ids,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }