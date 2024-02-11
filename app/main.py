from fastapi import BackgroundTasks, FastAPI

from app.database import create_db_and_tables
from app.routers import router_dish, router_full_menu, router_menu, router_submenu

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


@app.get('/menus/')
async def get_menus(background_tasks: BackgroundTasks):
    # Добавьте логику для вывода всех меню
    # Используйте background_tasks.add_task() для асинхронного вызова задачи инвалидации кэша
    pass


@app.on_event('startup')
async def on_startup() -> None:
    """Инициализирует базу данных при запуске приложения."""
    await create_db_and_tables()
    # result = update_menu_from_sheet()
    # print(f"ready? {result}")


app.include_router(router_menu.router)
app.include_router(router_submenu.router)
app.include_router(router_dish.router)
app.include_router(router_full_menu.router)


@app.get('/')
async def read_root() -> dict:
    """Корневой эндпоинт API."""
    return {'message': 'Добро пожаловать в API управления рестораном'}
