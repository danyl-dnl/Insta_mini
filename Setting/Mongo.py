from motor.motor_asyncio import AsyncIOMotorClient
from Setting.Config import MONGO_URL

mongo_client = AsyncIOMotorClient(MONGO_URL)
mongo_db = mongo_client.instagram_db

def get_mongo_db():
    return mongo_db

async def init_mongo():
    await mongo_db.reel_likes.create_index(
        [("reel_id", 1), ("user_id", 1)],
        unique=True
    )
    print("MongoDB indexes initialized successfully.")
