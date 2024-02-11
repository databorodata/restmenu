import asyncio
import uuid

import gspread
from google.oauth2.service_account import Credentials
from sqlalchemy import delete

from app.database import async_session_maker, get_redis_connection
from app.models import Dish, Menu, Submenu
from app.repositories.cache_repository import CacheRepository
from background.celery_app import celery_app
from background.sheet_parser import parse_sheet

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']


@celery_app.task(name='update_menu_from_sheet')
def update_menu_from_sheet():
    creds = Credentials.from_service_account_file('background/creds.json', scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open('restmenu_sheet').sheet1
    data = sheet.get_values()

    async def update_db():
        menus = parse_sheet(data)

        redis_connection = await get_redis_connection()
        cache_repository = CacheRepository(redis=redis_connection)

        async with async_session_maker() as session:
            async with session.begin():
                await session.execute(delete(Menu))

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
                            session.add(
                                Dish(
                                    id=uuid.uuid4(),
                                    menu_id=menu_id,
                                    submenu_id=submenu_id,
                                    title=dish.title,
                                    description=dish.description,
                                    price=dish.price,  # TODO: VALIDATE
                                )
                            )
                await cache_repository.delete_all()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_db())
