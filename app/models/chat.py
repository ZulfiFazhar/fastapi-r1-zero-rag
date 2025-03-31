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

class ChatMessage:
    def __init__(self, role: str, content: str, session_id: str,
                 id: Optional[PyObjectId] = None, created_at: Optional[datetime] = None,
                 metadata: Optional[Dict[str, Any]] = None, references: Optional[List[str]] = None):
        self.id = id or PyObjectId()
        self.role = role  # "user", "assistant", "system"
        self.content = content
        self.session_id = session_id
        self.metadata = metadata or {}
        self.references = references or []  # References to document chunks
        self.created_at = created_at or datetime.utcnow()
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Convert MongoDB document to ChatMessage object."""
        if not data:
            return None
        
        message = cls(
            id=data.get('_id'),
            role=data.get('role'),
            content=data.get('content'),
            session_id=data.get('session_id'),
            metadata=data.get('metadata'),
            references=data.get('references'),
            created_at=data.get('created_at')
        )
        return message
    
    def to_mongo(self) -> Dict[str, Any]:
        """Convert ChatMessage object to MongoDB document."""
        return {
            "role": self.role,
            "content": self.content,
            "session_id": self.session_id,
            "metadata": self.metadata,
            "references": self.references,
            "created_at": self.created_at
        }

class ChatSession:
    def __init__(self, title: Optional[str] = None, 
                 id: Optional[PyObjectId] = None, created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None, metadata: Optional[Dict[str, Any]] = None):
        self.id = id or PyObjectId()
        self.title = title or "New Chat"
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> 'ChatSession':
        """Convert MongoDB document to ChatSession object."""
        if not data:
            return None
        
        session = cls(
            id=data.get('_id'),
            title=data.get('title'),
            metadata=data.get('metadata'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
        return session
    
    def to_mongo(self) -> Dict[str, Any]:
        """Convert ChatSession object to MongoDB document."""
        return {
            "title": self.title,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }