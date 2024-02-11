import asyncio
import uuid

import gspread
from google.oauth2.service_account import Credentials
from sqlalchemy import delete

from app.database import DATABASE_URL, async_session_maker, get_redis_connection
from app.models import Dish, Menu, Submenu
from app.repositories.cache_repository import CacheRepository
from background.celery_app import celery_app
from background.sheet_parser import parse_sheet

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']


@celery_app.task(name='update_menu_from_sheet')
def update_menu_from_sheet():
    print('Starting update_menu_from_sheet task')
    # creds = Credentials.from_service_account_file('../app/backprocess/creds.json', scopes=SCOPES)
    creds = Credentials.from_service_account_file('app/backprocess/creds.json', scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open('restmenu_sheet').sheet1
    # data = sheet.get_all_records()
    data = sheet.get_values()
    print(data)

    async def update_db():
        print('update_db started')
        print(DATABASE_URL)

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

                # menu_id = uuid.uuid4()
                # submenu_id = uuid.uuid4()
                # session.add(Menu(id=menu_id, title="olo", description="111"))
                # session.add(Submenu(id=submenu_id, menu_id=menu_id, title="submenu olo", description="222"))
                # session.add(
                #     Dish(id=uuid.uuid4(), menu_id=menu_id, submenu_id=submenu_id, title="dish", description="ddd",
                #          price="11"))

        # async with async_session_maker() as session:
        #     async with session.begin():
        #
        #         redis_connection = await get_redis_connection()
        #         menu_repository = MenuRepository(session=session)
        #         submenu_repository = SubmenuRepository(session=session)
        #         dish_repository = DishRepository(session=session)
        #         cache_repository = CacheRepository(redis=redis_connection)
        #         menu_service = MenuService(menu_repository=menu_repository, cache_repository=cache_repository)
        #         submenu_service = SubmenuService(submenu_repository=submenu_repository,
        #                                          cache_repository=cache_repository)
        #         dish_service = DishService(dish_repository=dish_repository, cache_repository=cache_repository)
        #
        #         current_col = 0
        #         current_row = 0
        #         for i in range(len(data)):
        #             if data[current_row][current_col]:
        #                 print(data[current_row][current_col + 1])
        #                 menu_data = CreateEditMenuModel(
        #                     title=data[current_row][current_col + 1],
        #                     description=data[current_row][current_col + 2]
        #                 )
        #                 print(menu_data)
        #                 menu: MenuDict = await menu_service.create_menu(menu_data.model_dump())
        #                 # menu = await app.url_path_for("create_menu", menu_data)
        #                 menu_id = uuid.UUID(menu['id'])
        #                 print(menu)
        #                 current_col += 1
        #                 current_row += 1
        #                 # session.add(menu)
        #                 while get_int(data[current_row][current_col]) or not data[current_row][current_col]:
        #                     if data[current_row][current_col]:
        #                         submenu_data = CreateEditSubmenuModel(title=data[current_row][current_col + 1],
        #                                                               description=data[current_row][current_col + 2])
        #                         submenu = await submenu_service.create_submenu(menu_id, submenu_data.model_dump())
        #                         submenu_id = uuid.UUID(submenu['id'])
        #                         print(submenu)
        #                         # session.add(submenu)
        #                         current_col += 1
        #                         current_row += 1
        #                         while get_int(data[current_row][current_col]) or not data[current_row][current_col]:
        #                             if data[current_row][current_col]:
        #                                 dish_data = CreateEditDishModel(title=data[current_row][current_col + 1],
        #                                                                 description=data[current_row][current_col + 2],
        #                                                                 price=data[current_row][current_col + 3])
        #                                 dish = await dish_service.create_dish(
        #                                     menu_id,
        #                                     submenu_id,
        #                                     dish_data.model_dump()
        #                                 )
        #
        #                                 print(dish)
        #                                 # session.add(dish)
        #
        #                             current_row += 1
        #                     current_row += 1
        #             current_row = i + 1
        #             current_col = 0
        #         # await session.commit()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_db())

    # asyncio.run(update_db())
