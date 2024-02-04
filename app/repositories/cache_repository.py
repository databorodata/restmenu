from aioredis import Redis


class CacheRepository:
    def __init__(self, redis: Redis) -> None:
        """Инициализация репозитория кэша с экземпляром Redis."""
        self.redis = redis

    async def get(self, key: str) -> str | None:
        """Получение значения по ключу из Redis."""
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expire: int | None = None) -> None:
        """Установка значения по ключу в Redis с опциональным временем истечения."""
        if expire is not None:
            await self.redis.set(key, value, ex=expire)
        else:
            await self.redis.set(key, value)

    async def delete(self, key: str) -> None:
        """Удаление значения по ключу из Redis."""
        await self.redis.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        """Удаление значений по шаблону ключа из Redis."""
        has_next = True
        cursor = 0
        while has_next:
            cursor, keys = await self.redis.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await self.redis.delete(*keys)
            has_next = (cursor != 0)
