class CacheRepository:
    def __init__(self, redis):
        self.redis = redis

    async def get(self, key):
        return await self.redis.get(key)

    async def set(self, key, value, expire=None):
        await self.redis.set(key, value, ex=expire)

    async def delete(self, key):
        await self.redis.delete(key)

    async def delete_pattern(self, pattern: str):
        cursor = '0'
        while cursor:
            cursor, keys = await self.redis.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await self.redis.delete(*keys)