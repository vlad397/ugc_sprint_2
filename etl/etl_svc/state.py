from typing import Optional

from aioredis import Redis
from etl_models.state import State


class EtlStateRedis:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_state(self, topik) -> Optional[State]:
        ans = await self.redis.get(topik)
        if ans is None:
            return None
        return State(**ans)

    async def set_state(self, topik: str, state: State):
        await self.redis.set(name=topik, value=state.json())
