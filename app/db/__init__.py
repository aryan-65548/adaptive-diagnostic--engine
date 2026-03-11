from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient = None
db = None

async def connect_db():
    global client, db
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.db_name]
    print("✅ Connected to MongoDB")

async def close_db():
    global client
    if client:
        client.close()
        print("✅ MongoDB connection closed")

def get_db():
    return db