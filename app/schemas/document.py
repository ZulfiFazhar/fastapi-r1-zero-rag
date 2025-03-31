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

class DocumentBase(BaseModel):
    title: str
    content: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    chunk_ids: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        validate_by_name = True
        json_encoders = {
            ObjectId: str
        }

class DocumentList(BaseModel):
    documents: List[DocumentResponse]
    total: int
    page: int
    size: int
