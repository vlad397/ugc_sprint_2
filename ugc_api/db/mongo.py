from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient

mongo: Optional[AsyncIOMotorClient] = None


async def get_mongo_client() -> Optional[AsyncIOMotorClient]:
    return mongo
