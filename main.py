import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes.api import router as api_router
from app.core.database import connect_to_mongodb, close_mongodb_connection
from app.core.chroma_client import initialize_chroma, close_chroma_connection

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VERSION,
        debug=settings.DEBUG
    )
    
    # Set up CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API router
    application.include_router(api_router, prefix=settings.API_PREFIX)
    
    # Set up event handlers
    application.add_event_handler("startup", connect_to_mongodb)
    application.add_event_handler("startup", initialize_chroma)
    application.add_event_handler("shutdown", close_mongodb_connection)
    application.add_event_handler("shutdown", close_chroma_connection)
    
    return application

app = create_application()

@app.get("/")
async def root():
    return {"message": "Welcome to RAG API with OpenRouter and ChromaDB"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)