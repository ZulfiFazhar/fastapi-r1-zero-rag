from typing import List, Dict, Any, Optional
from app.core.openrouter import OpenRouterClient
from app.core.config import settings
from app.services.retrieval_service import RetrievalService
from app.models.chat import ChatMessage, ChatSession
from app.core.database import db
from bson import ObjectId
import logging

class GenerationService:
    """Service for handling LLM generation operations."""
    
    async def create_chat_session(self, title: Optional[str] = None) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(title=title)
        result = await db.db.chat_sessions.insert_one(session.to_mongo())
        session.id = result.inserted_id
        return session
    
    async def get_session_messages(self, session_id: str) -> List[ChatMessage]:
        """Get all messages for a specific chat session."""
        messages = []
        cursor = db.db.chat_messages.find({"session_id": session_id}).sort("created_at", 1)
        
        async for msg in cursor:
            messages.append(ChatMessage.from_mongo(msg))
            
        return messages
    
    async def generate_response(self, session_id: str, user_message: str, 
                               system_prompt: Optional[str] = None,
                               retrieval_options: Optional[Dict[str, Any]] = None,
                               model: Optional[str] = None,
                               temperature: float = 0.7,
                               max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate a response using RAG."""
        # Create session if not exists
        if not session_id:
            session = await self.create_chat_session()
            session_id = str(session.id)
        else:
            # Verify session exists
            session = await db.db.chat_sessions.find_one({"_id": ObjectId(session_id)})
            if not session:
                session = await self.create_chat_session()
                session_id = str(session.id)
        
        # Save user message
        user_chat_msg = ChatMessage(
            role="user",
            content=user_message,
            session_id=session_id
        )
        user_result = await db.db.chat_messages.insert_one(user_chat_msg.to_mongo())
        user_chat_msg.id = user_result.inserted_id
        
        # Get conversation history
        conversation_history = await self.get_session_messages(session_id)
        
        # Format messages for LLM
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add conversation history (limit to last 10 messages for context)
        history_limit = 10
        for msg in conversation_history[-history_limit:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Perform retrieval if requested
        references = []
        retrieval_options = retrieval_options or {}
        
        if retrieval_options.get("enabled", True):
            retrieval_service = RetrievalService()
            search_results = await retrieval_service.search(
                user_message,
                top_k=retrieval_options.get("top_k", 5),
                filter_metadata=retrieval_options.get("filter_metadata")
            )
            
            # Add retrieval context to system prompt
            if search_results:
                context_docs = [f"[{i+1}] {res.chunk_text}" for i, res in enumerate(search_results)]
                context_text = "\n\n".join(context_docs)
                
                retrieval_prompt = f"""Use the following information from the knowledge base to help answer the user's question.
If the information is not relevant to the user's question, ignore it:

{context_text}

When referring to the information, don't mention the source numbers or explicitly state that you're using the knowledge base."""
                
                # Add or update the system message with retrieval context
                if messages and messages[0]["role"] == "system":
                    messages[0]["content"] = f"{messages[0]['content']}\n\n{retrieval_prompt}"
                else:
                    messages.insert(0, {
                        "role": "system",
                        "content": retrieval_prompt
                    })
                
                # Track references for metadata
                references = [
                    {
                        "chunk_id": res.chunk_id,
                        "document_id": res.document_id,
                        "score": res.score
                    } for res in search_results
                ]
        
        # Generate completion with OpenRouter
        openrouter_client = OpenRouterClient()
        response = await openrouter_client.generate_completion(
            messages=messages,
            model=model or settings.DEFAULT_LLM_MODEL,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Extract assistant message
        assistant_content = response["choices"][0]["message"]["content"]
        
        # Save assistant message with references
        assistant_chat_msg = ChatMessage(
            role="assistant",
            content=assistant_content,
            session_id=session_id,
            references=[ref["chunk_id"] for ref in references]
        )
        assistant_result = await db.db.chat_messages.insert_one(assistant_chat_msg.to_mongo())
        assistant_chat_msg.id = assistant_result.inserted_id
        
        # Update session metadata
        await db.db.chat_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"updated_at": assistant_chat_msg.created_at}}
        )
        
        # Return response with session info and references
        return {
            "session_id": session_id,
            "message": assistant_chat_msg,
            "references": references
        }