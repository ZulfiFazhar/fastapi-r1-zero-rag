from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.chat import (
    ChatSessionCreate, ChatSessionResponse, 
    ChatRequest, ChatResponse, ChatMessageResponse
)
from app.services.generation_service import GenerationService
from app.core.database import db
from bson import ObjectId

router = APIRouter()

@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(session: ChatSessionCreate):
    """Create a new chat session."""
    generation_service = GenerationService()
    created_session = await generation_service.create_chat_session(session.title)
    return created_session

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions():
    """Get all chat sessions."""
    cursor = db.db.chat_sessions.find().sort("updated_at", -1)
    sessions = []
    
    async for session in cursor:
        session['_id'] = str(session['_id'])
        sessions.append(session)
        
    return sessions

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(session_id: str):
    """Get all messages for a specific chat session."""
    generation_service = GenerationService()
    messages = await generation_service.get_session_messages(session_id)
    
    # Convert message objects to response model format
    response_messages = []
    for msg in messages:
        msg_dict = {
            "_id": str(msg.id),
            "role": msg.role,
            "content": msg.content,
            "session_id": msg.session_id,
            "metadata": msg.metadata,
            "references": msg.references,
            "created_at": msg.created_at
        }
        response_messages.append(msg_dict)
        
    return response_messages

@router.post("/generate", response_model=ChatResponse)
async def generate_chat_response(request: ChatRequest):
    """Generate a response using RAG."""
    generation_service = GenerationService()
    response = await generation_service.generate_response(
        session_id=request.session_id,
        user_message=request.message,
        system_prompt=request.system_prompt,
        retrieval_options=request.retrieval_options,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )
    
    # Convert response to expected format
    message_dict = {
        "_id": str(response["message"].id),
        "role": response["message"].role,
        "content": response["message"].content,
        "session_id": response["message"].session_id,
        "metadata": response["message"].metadata,
        "references": response["message"].references,
        "created_at": response["message"].created_at
    }
    
    return ChatResponse(
        session_id=response["session_id"],
        message=message_dict,
        references=response["references"]
    )

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(session_id: str):
    """Delete a chat session and all associated messages."""
    # Delete all messages in the session
    await db.db.chat_messages.delete_many({"session_id": session_id})
    
    # Delete the session
    result = await db.db.chat_sessions.delete_one({"_id": ObjectId(session_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session with ID {session_id} not found"
        )
        
    return None