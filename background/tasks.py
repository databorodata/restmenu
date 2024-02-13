import asyncio
import uuid

import gspread
from google.oauth2.service_account import Credentials
from sqlalchemy import delete

from app.database import async_session_maker, get_redis_connection
from app.models import Dish, Menu, Submenu
from app.repositories.cache_repository import CacheRepository
from app.services.dish_service import validate_price
from background.celery_app import celery_app
from background.sheet_parser import parse_sheet

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']


@celery_app.task(name='update_menu_from_sheet')
def update_menu_from_sheet():
    """Фоновая задача обновление меню из google sheets раз в 15 сек"""
    creds = Credentials.from_service_account_file('background/creds.json', scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open('restmenu_sheet').sheet1
    data = sheet.get_values()

    async def update_db():
        """Обновление меню из google sheets"""
        menus = parse_sheet(data)

        redis_connection = await get_redis_connection()
        cache_repository = CacheRepository(redis=redis_connection)

        async with async_session_maker() as session:
            async with session.begin():
                await session.execute(delete(Menu))

                discount_dishes = {}
                for menu in menus:
                    menu_id = uuid.uuid4()
                    session.add(Menu(id=menu_id, title=menu.title, description=menu.description))
                    for submenu in menu.submenus:
                        submenu_id = uuid.uuid4()
                        session.add(
                            Submenu(
                                id=submenu_id,
                                menu_id=menu_id,
                                title=submenu.title,
                                description=submenu.description,
                            )
                        )
                        for dish in submenu.dishes:
                            dish_id = uuid.uuid4()
                            if dish.discount:
                                discount_dishes[dish_id] = dish.discount

                            session.add(
                                Dish(
                                    id=dish_id,
                                    menu_id=menu_id,
                                    submenu_id=submenu_id,
                                    title=dish.title,
                                    description=dish.description,
                                    price=validate_price(dish.price),
                                )
                            )
                await cache_repository.delete_all()
                for dish_id, discount in discount_dishes.items():
                    await cache_repository.set(f'{str(dish_id)}_discount', discount, expire=15)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_db())
