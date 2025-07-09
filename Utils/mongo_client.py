# BackEnd/Utils/mongo_client.py
import os
import certifi
import logging
from datetime import datetime
from typing import Dict
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from BackEnd.Utils.config import settings

# Setup asynchronous MongoDB client with TLS/SSL
client = AsyncIOMotorClient(
    str(settings.MONGO_URL),
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000
)

mongo_db = client[settings.MONGO_DB_NAME]
chat_sessions_collection = mongo_db["chat_sessions"]
recommendations_collection = mongo_db["recommendations"]


async def ensure_indexes():
    """Create required indexes asynchronously on chat_sessions collection."""
    try:
        await chat_sessions_collection.create_index([("user_id", ASCENDING)])
        await chat_sessions_collection.create_index([("child_id", ASCENDING)])
        await chat_sessions_collection.create_index([("timestamp", ASCENDING)])
        await chat_sessions_collection.create_index(
            [("user_id", ASCENDING), ("child_id", ASCENDING)],
            name="user_child_composite"
        )
        logging.info("MongoDB indexes ensured successfully.")
    except Exception as e:
        logging.warning(f"Could not create MongoDB indexes: {e}")


class MongoDBClient:
    def __init__(self):
        self.client = client
        self.db = mongo_db

    def connect(self, db_name: str):
        """Switch to a particular database."""
        self.db = self.client[db_name]
        logging.info(f"Connected to MongoDB database: {db_name}")
        return self.db

    def get_collection(self, collection_name: str):
        """Get a collection from the current database."""
        if not self.db:
            raise Exception("Database not selected. Call connect() first.")
        return self.db[collection_name]

    async def insert_session(self, data: Dict):
        """Insert a chat session document with timestamp into chat_sessions collection."""
        data = data.copy()
        data["timestamp"] = datetime.utcnow()
        await chat_sessions_collection.insert_one(data)

    async def ping(self) -> Dict[str, str]:
        """Ping MongoDB to check connection health."""
        try:
            result = await self.client.admin.command("ping")
            if result.get("ok") == 1:
                return {"status": "ok"}
            return {"status": "error", "details": result}
        except Exception as e:
            logging.error(f"MongoDB ping error: {e}")
            return {"status": "error", "details": str(e)}


# Create a singleton client for app-wide use
mongo_client = MongoDBClient()
