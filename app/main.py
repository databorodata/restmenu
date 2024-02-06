from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import router_dish, router_menu, router_submenu

app = FastAPI(
    title='Меню ресторана',
    description='Это API позволяет управлять меню ресторана.',
    version='1.0.0',
    openapi_tags=[{
        'name': 'Menus',
        'description': 'Операции с меню.',
    }, {
        'name': 'Submenus',
        'description': 'Операции с подменю.',
    }, {
        'name': 'Dishes',
        'description': 'Операции с блюдами.',
    }]
)


@app.on_event('startup')
async def on_startup() -> None:
    """Инициализирует базу данных при запуске приложения."""
    await create_db_and_tables()

app.include_router(router_menu.router)
app.include_router(router_submenu.router)
app.include_router(router_dish.router)


@app.get('/')
async def read_root() -> dict:
    """Корневой эндпоинт API."""
    return {'message': 'Добро пожаловать в API управления рестораном'}
