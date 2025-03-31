import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongodb():
    """Create database connection."""
    logging.info("Connecting to MongoDB...")
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.db = db.client[settings.MONGODB_DB_NAME]
    logging.info("Connected to MongoDB!")

async def close_mongodb_connection():
    """Close database connection."""
    logging.info("Closing connection to MongoDB...")
    if db.client:
        db.client.close()
    logging.info("MongoDB connection closed!")