from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import complex as complex_query
from app.routers import router_dish, router_menu, router_submenu

app = FastAPI(
    title='Меню ресторана',
    description='REST API по работе с меню ресторана',
    version='1.0.0',
)


@app.on_event('startup')
async def on_startup() -> None:
    """Инициализирует базу данных при запуске приложения."""
    await create_db_and_tables()

app.include_router(router_menu.router)
app.include_router(router_submenu.router)
app.include_router(router_dish.router)
app.include_router(complex_query.router)


@app.get('/')
async def read_root() -> dict:
    """Корневой эндпоинт API."""
    return {'message': 'Welcome to the Rest Menu API'}
