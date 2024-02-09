from app.database import async_session_maker
from celery_app import celery_app
import gspread
from google.oauth2.service_account import Credentials
import asyncio
from app.models import Menu, Submenu, Dish  # Импорт моделей из вашего файла моделей
from asgiref.sync import async_to_sync

from celery import shared_task


SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']


@celery_app.task(name="update_menu_from_sheet")
def update_menu_from_sheet():
    print("Starting update_menu_from_sheet task")
    creds = Credentials.from_service_account_file('app/backprocess/creds.json', scopes=SCOPES)
    print(creds)
    client = gspread.authorize(creds)
    print(client)
    sheet = client.open("restmenu_sheet").sheet1
    print(sheet)
    # data = sheet.get_all_records()
    data = sheet.get_values()
    print(data)

    async def update_db():
        print('update_db started')
        async with async_session_maker() as session:
            print(f'session: {session}')
            for row in data:
                menu_title, submenu_title, dish_title, dish_description, dish_price, discount = \
                    row['Menu'], row['Submenu'], row['Dish'], row['Description'], row['Price'], row['Discount']
                print('data: ', menu_title, submenu_title, dish_title, dish_description, dish_price, discount)
                # Обработка меню
                menu = await session.get(Menu, {"title": menu_title})
                if not menu:
                    menu = Menu(title=menu_title)
                    session.add(menu)
                    await session.commit()

                # Обработка подменю
                submenu = await session.get(Submenu, {"title": submenu_title, "menu_id": menu.id})
                if not submenu:
                    submenu = Submenu(title=submenu_title, menu_id=menu.id)
                    session.add(submenu)
                    await session.commit()

                # Обработка блюда
                dish = await session.get(Dish, {"title": dish_title, "submenu_id": submenu.id})
                if dish:
                    dish.description = dish_description
                    dish.price = dish_price  # Обработайте скидку, если это необходимо
                else:
                    dish = Dish(title=dish_title, description=dish_description, price=dish_price, submenu_id=submenu.id)
                    session.add(dish)
                await session.commit()

    # async_to_sync(update_db)()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_db())

# @celery_app.task(name="update_menu_from_sheet")
# def update_menu_from_sheet():
# # @shared_task(bind=True, name="update_menu_from_sheet")
# # async def update_menu_from_sheet(self):
#     print("Starting update_menu_from_sheet task")
#     creds = Credentials.from_service_account_file('app/backprocess/creds.json', scopes=SCOPES)
#     print(f"creds  {creds}")
#     client = gspread.authorize(creds)
#     print(f"client   {client}")
#     sheet = client.open("restmenu_sheet").sheet1
#     print(f"sheet, {sheet}")
#     # data = sheet.get_all_records()
#     data = sheet.get_values()
#     print("!!!!!!!! data")
#     # print("&&&&&&", data)
#     print("!!!!!!!! data")

    # async with async_session_maker() as session:
    #     for row in data:
    #         # Доступ к данным в row с проверкой наличия и типа данных
    #         try:
    #             menu_title, submenu_title, dish_title, dish_description, dish_price, discount = row
    #             # Ваш код для обновления БД
    #         except IndexError as e:
    #             print(f"Error processing row {row}: {e}")

    # async def update_db():
    #     print('update_db started')
    #     async with async_session_maker() as session:
    #         print(f'session: {session}')
    #
    #         for row in data[1:]:  # Пропускаем заголовок
    #             menu_title, submenu_title, dish_title, dish_description, dish_price, discount = row[:6]
    #             dish_price = float(dish_price) if dish_price else 0
    #             discount = float(discount) if discount else 0
    #             final_price = dish_price * (1 - discount / 100)
    #
    #             print(
    #                 f"Processing: Menu: {menu_title}, Submenu: {submenu_title}, Dish: {dish_title}, Final Price: {final_price}")

    #
    #
    #         for row in data:
    #             menu_title, submenu_title, dish_title, dish_description, dish_price, discount = \
    #                 row['Menu'], row['Submenu'], row['Dish'], row['Description'], row['Price'], row['Discount']
    #             print('data: ', menu_title, submenu_title, dish_title, dish_description, dish_price, discount)
    #             # Обработка меню
    #             menu = await session.get(Menu, {"title": menu_title})
    #             if not menu:
    #                 menu = Menu(title=menu_title)
    #                 session.add(menu)
    #                 await session.commit()
    #
    #             # Обработка подменю
    #             submenu = await session.get(Submenu, {"title": submenu_title, "menu_id": menu.id})
    #             if not submenu:
    #                 submenu = Submenu(title=submenu_title, menu_id=menu.id)
    #                 session.add(submenu)
    #                 await session.commit()
    #
    #             # Обработка блюда
    #             dish = await session.get(Dish, {"title": dish_title, "submenu_id": submenu.id})
    #             if dish:
    #                 dish.description = dish_description
    #                 dish.price = dish_price  # Обработайте скидку, если это необходимо
    #             else:
    #                 dish = Dish(title=dish_title, description=dish_description, price=dish_price, submenu_id=submenu.id)
    #                 session.add(dish)
    #             await session.commit()
    #
    # # asyncio.run(update_db())
    #
    #
    # # async_to_sync(update_db)()
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(update_db())




