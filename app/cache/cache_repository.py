import aioredis

class CacheRepository:
    def __init__(self, redis_url):
        self.redis_url = redis_url
        self.redis = None

    async def get_redis_connection(self):
        if not self.redis:
            self.redis = await aioredis.create_redis_pool(self.redis_url)
        return self.redis

    async def get(self, key):
        redis = await self.get_redis_connection()
        return await redis.get(key)

    async def set(self, key, value, expire=None):
        redis = await self.get_redis_connection()
        await redis.set(key, value, expire=expire)

    async def delete(self, key):
        redis = await self.get_redis_connection()
        await redis.delete(key)
