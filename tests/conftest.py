import asyncio

import pytest

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine

from app.main import app
from app.database import Base
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER


TEST_DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)


@pytest.fixture(scope="session")
def event_loop():
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! LOOP")
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def init_db():
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ DB")
    print(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(init_db):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client