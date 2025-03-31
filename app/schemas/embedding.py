from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class DocumentChunkBase(BaseModel):
    document_id: str
    chunk_text: str
    chunk_index: int
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class DocumentChunkCreate(DocumentChunkBase):
    pass

class DocumentChunkResponse(DocumentChunkBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    vector_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        validate_by_name = True
        json_encoders = {
            ObjectId: str
        }

class ChunkList(BaseModel):
    chunks: List[DocumentChunkResponse]
    total: int
    page: int
    size: int