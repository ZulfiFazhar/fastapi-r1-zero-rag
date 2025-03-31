import logging
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings

class ChromaClient:
    client = None
    collection = None

chroma = ChromaClient()

async def initialize_chroma():
    """Initialize ChromaDB client."""
    logging.info("Initializing ChromaDB client...")
    
    # For HTTP client (when using ChromaDB as a service)
    if settings.CHROMADB_HOST and settings.CHROMADB_PORT:
        chroma.client = chromadb.HttpClient(
            host=settings.CHROMADB_HOST,
            port=settings.CHROMADB_PORT
        )
    # For persistent client (when using ChromaDB embedded)
    else:
        chroma.client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )
    
    # Create or get collection
    chroma.collection = chroma.client.get_or_create_collection(
        name=settings.CHROMADB_COLLECTION,
        metadata={"hnsw:space": "cosine"}
    )
    
    logging.info(f"ChromaDB collection '{settings.CHROMADB_COLLECTION}' initialized")

async def close_chroma_connection():
    """Close ChromaDB connection."""
    logging.info("Closing ChromaDB connection...")
    # No explicit close method in ChromaDB client
    chroma.client = None
    chroma.collection = None
    logging.info("ChromaDB connection closed!")