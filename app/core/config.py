import os
from typing import List
from pydantic import BaseModel, AnyHttpUrl
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    # Project settings
    PROJECT_NAME: str = "RAG API with OpenRouter and ChromaDB"
    PROJECT_DESCRIPTION: str = "A FastAPI project for RAG using OpenRouter and ChromaDB"
    PROJECT_VERSION: str = "0.1.0"
    
    # API settings
    API_PREFIX: str = os.getenv("API_PREFIX", "/api/v1")
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    SECRET_KEY: str = os.getenv("API_SECRET_KEY", "your_secret_key")
    
    # MongoDB settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "rag_db")
    
    # ChromaDB settings
    CHROMADB_HOST: str = os.getenv("CHROMADB_HOST", "localhost")
    CHROMADB_PORT: int = int(os.getenv("CHROMADB_PORT", "8000"))
    CHROMADB_COLLECTION: str = os.getenv("CHROMADB_COLLECTION", "documents")
    
    # OpenRouter settings
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_API_URL: str = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1")
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "anthropic/claude-3-opus-20240229")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-small")
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["*"]

settings = Settings()