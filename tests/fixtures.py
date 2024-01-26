# import pytest_asyncio
# from httpx import AsyncClient
# from sqlalchemy import NullPool
# from sqlalchemy.ext.asyncio import create_async_engine
# from sqlalchemy.orm import declarative_base
#
# from app.main import app
# from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
#
# # Настройка асинхронного движка для тестовой БД
# TEST_DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# Base = declarative_base()
# engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
#
#
# @pytest_asyncio.fixture(scope="session", autouse=True)
# async def init_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)


# @pytest_asyncio.fixture(scope="session")
# async def db_session(init_db):
#     async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
#     async with async_session_maker() as session:
#         yield session


# # Фикстура для подключения к БД
# @pytest.fixture(scope="session", autouse=True)
# async def create_test_database():
#     async with engine.begin() as conn:
#         # Создание всех таблиц
#         await conn.run_sync(Base.metadata.create_all)
#     # Здесь можно добавить предварительное заполнение БД, если необходимо
#     yield
#     # async with engine.begin() as conn:
#     #     print('delete!!!!!!!!!!!!!')
#     #     # Удаление всех таблиц
#     #     await conn.run_sync(Base.metadata.drop_all)
#
# # Фикстура для сессии БД
# @pytest.fixture
# async def db_session():
#     async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
#     async with async_session_maker() as session:
#         yield session


# @pytest_asyncio.fixture
# async def client():
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         yield client
