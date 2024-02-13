import asyncio

import gspread
from google.oauth2.service_account import Credentials
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert

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
                discount_dishes = {}
                updated_menus = []
                updated_submenus = []
                updated_dishes = []
                for menu in menus:
                    updated_menus.append(menu.id)
                    stmt = insert(Menu).values(
                        id=menu.id,
                        title=menu.title,
                        description=menu.description
                    ).on_conflict_do_update(
                        index_elements=['id'],
                        set_=dict(title=menu.title, description=menu.description)
                    )
                    await session.execute(stmt)

                    for submenu in menu.submenus:
                        updated_submenus.append(submenu.id)
                        stmt = insert(Submenu).values(
                            id=submenu.id,
                            menu_id=menu.id,
                            title=submenu.title,
                            description=submenu.description
                        ).on_conflict_do_update(
                            index_elements=['id'],
                            set_=dict(menu_id=menu.id, title=submenu.title, description=submenu.description)
                        )
                        await session.execute(stmt)

                        for dish in submenu.dishes:
                            updated_dishes.append(dish.id)
                            if dish.discount:
                                discount_dishes[dish.id] = dish.discount

                            stmt = insert(Dish).values(
                                id=dish.id,
                                submenu_id=submenu.id,
                                title=dish.title,
                                description=dish.description,
                                price=validate_price(dish.price)
                            ).on_conflict_do_update(
                                index_elements=['id'],
                                set_=dict(submenu_id=submenu.id, title=dish.title, description=dish.description,
                                          price=validate_price(dish.price))
                            )
                            await session.execute(stmt)

                await session.execute(delete(Dish).where(Dish.id.notin_(updated_dishes)))
                await session.execute(delete(Submenu).where(Submenu.id.notin_(updated_submenus)))
                await session.execute(delete(Menu).where(Menu.id.notin_(updated_menus)))

                await cache_repository.delete_all()
                for dish_id, discount in discount_dishes.items():
                    await cache_repository.set(f'{str(dish_id)}_discount', discount, expire=15)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_db())
