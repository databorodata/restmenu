import asyncio
from asyncio import AbstractEventLoop
from typing import AsyncGenerator, Generator

import aioredis
import pytest
import pytest_asyncio
from aioredis import Redis
from httpx import AsyncClient
from sqlalchemy import NullPool, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from app.database import REDIS_URL, Base
from app.main import app
from app.models import Menu
from app.repositories.cache_repository import CacheRepository
from app.repositories.dish_repository import DishRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.submenu_repository import SubmenuRepository

TEST_DB_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture(scope='session')
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def init_db() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def client(init_db: None) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client


@pytest_asyncio.fixture
async def menu_repo(db_session: AsyncSession) -> AsyncGenerator[MenuRepository, None]:
    yield MenuRepository(db_session)


@pytest_asyncio.fixture
async def submenu_repo(db_session: AsyncSession) -> AsyncGenerator[SubmenuRepository, None]:
    yield SubmenuRepository(db_session)


@pytest_asyncio.fixture
async def dish_repo(db_session: AsyncSession) -> AsyncGenerator[DishRepository, None]:
    yield DishRepository(db_session)


@pytest_asyncio.fixture
async def redis() -> AsyncGenerator[Redis, None]:
    yield aioredis.from_url(REDIS_URL, encoding='utf-8', decode_responses=True)


@pytest_asyncio.fixture
async def cache_repo(redis: Redis) -> AsyncGenerator[CacheRepository, None]:
    yield CacheRepository(redis)


@pytest.fixture(scope='function')
async def cleanup_db(db_session: AsyncSession, cache_repo: CacheRepository) -> AsyncGenerator[None, None]:
    await db_session.execute(delete(Menu))
    await cache_repo.delete_all()
    yield
