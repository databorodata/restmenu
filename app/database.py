from typing import AsyncGenerator

import aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker

from config import (
    DB_HOST,
    DB_NAME,
    DB_PASS,
    DB_PORT,
    DB_USER,
    REDIS_DB,
    REDIS_HOST,
    REDIS_PORT,
)

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
Base = declarative_base()

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_redis_connection():
    # Создаём экземпляр Redis с пулом соединений
    redis = aioredis.from_url(f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}', encoding='utf-8', decode_responses=True)
    return redis


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
