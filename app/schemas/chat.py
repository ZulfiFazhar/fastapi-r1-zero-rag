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

class ChatMessageBase(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    session_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    references: List[str] = Field(default_factory=list)  # References to document chunks
    created_at: datetime
    
    class Config:
        from_attributes = True
        validate_by_name = True
        json_encoders = {
            ObjectId: str
        }

class ChatSessionBase(BaseModel):
    title: Optional[str] = "New Chat"
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionResponse(ChatSessionBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        validate_by_name = True
        json_encoders = {
            ObjectId: str
        }

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    system_prompt: Optional[str] = None
    retrieval_options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

class ChatResponse(BaseModel):
    session_id: str
    message: ChatMessageResponse
    references: List[Dict[str, Any]] = Field(default_factory=list)