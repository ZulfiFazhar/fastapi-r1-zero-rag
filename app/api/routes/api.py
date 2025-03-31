from fastapi import APIRouter
from app.api.routes import documents, embedding, search, chat

router = APIRouter()
router.include_router(documents.router, prefix="/documents", tags=["documents"])
router.include_router(embedding.router, prefix="/embedding", tags=["embedding"])
router.include_router(search.router, prefix="/search", tags=["search"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])