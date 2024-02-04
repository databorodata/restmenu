from typing import AsyncGenerator

import aioredis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

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
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_redis_connection() -> aioredis.Redis:
    """Создание соединения с Redis."""
    redis = aioredis.from_url(f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}', encoding='utf-8', decode_responses=True)
    return redis


async def create_db_and_tables() -> None:
    """Создание базы данных и таблиц при запуске."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Получение асинхронной сессии для работы с базой данных."""
    async with async_session_maker() as session:
        yield session
