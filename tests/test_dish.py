# import pytest
# from httpx import AsyncClient
# from app.main import app
# from app.models import Menu, Submenu, Dish
# from app.schemas import CreateEditMenuModel, CreateEditSubmenuModel, CreateEditDishModel
# from test_fixtures import create_test_database, db_session
#
# @pytest.mark.usefixtures("db_session", "create_test_database")
# class TestDishAPI:
#     menu_id = None
#     submenu_id = None
#     dish_id = None
#
#     @pytest.fixture(autouse=True)
#     async def setup(self, db_session):
#         # Создание меню и подменю для тестирования блюд
#         new_menu = Menu(title="Test Menu", description="Test Description")
#         new_submenu = Submenu(title="Test Submenu", description="Test Submenu Description", menu_id=new_menu.id)
#         db_session.add(new_menu)
#         db_session.add(new_submenu)
#         await db_session.commit()
#         TestDishAPI.menu_id = new_menu.id
#         TestDishAPI.submenu_id = new_submenu.id
#
#         yield  # После завершения тестов
#
#         # Очистка данных
#         await db_session.delete(new_menu)
#         print('!!!!!!!!!!!!!!!!!!!!!!delete')
#         await db_session.delete(new_submenu)
#         await db_session.commit()
#
#     @pytest.mark.asyncio
#     async def test_1_get_dishes_empty(self):
#         async with AsyncClient(app=app, base_url="http://test") as client:
#             yield client
#         response = await client.get(f"/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}/dishes")
#         assert response.status_code == 200
#         assert response.json() == []
#
#     @pytest.mark.asyncio
#     async def test_2_create_dish(self):
#         async with AsyncClient(app=app, base_url="http://test") as client:
#             yield client
#         data = {"title": "Test Dish", "description": "Test Dish Description", "price": "10.99"}
#         response = await client.post(f"/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}/dishes", json=data)
#         assert response.status_code == 201
#         TestDishAPI.dish_id = response.json()["id"]
#
#     @pytest.mark.asyncio
#     async def test_3_get_all_dishes(self):
#         async with AsyncClient(app=app, base_url="http://test") as client:
#             yield client
#         response = await client.get(f"/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}/dishes")
#         assert response.status_code == 200
#         assert TestDishAPI.dish_id in [dish["id"] for dish in response.json()]
#
#     @pytest.mark.asyncio
#     async def test_4_get_specific_dish(self):
#         async with AsyncClient(app=app, base_url="http://test") as client:
#             yield client
#         response = await client.get(f"/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}/dishes/{self.dish_id}")
#         assert response.status_code == 200
#         assert response.json()["id"] == TestDishAPI.dish_id
#
#     @pytest.mark.asyncio
#     async def test_5_update_dish(self):
#         async with AsyncClient(app=app, base_url="http://test") as client:
#             yield client
#         update_data = {"title": "Updated Dish", "description": "Updated Description", "price": "15.99"}
#         response = await client.patch(f"/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}/dishes/{self.dish_id}",
#                                       json=update_data)
#         assert response.status_code == 200
#
#     @pytest.mark.asyncio
#     async def test_6_get_specific_dish_after_update(self):
#         async with AsyncClient(app=app, base_url="http://test") as client:
#             yield client
#         response = await client.get(f"/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}/dishes/{self.dish_id}")
#         assert response.status_code == 200
#         assert response.json()["title"] == "Updated Dish"
#
#     @pytest.mark.asyncio
#     async def test_7_delete_dish(self):
#         async with AsyncClient(app=app, base_url="http://test") as client:
#             yield client
#         response = await client.delete(f"/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}/dishes/{self.dish_id}")
#         assert response.status_code == 200
#
#     @pytest.mark.asyncio
#     async def test_8_get_dishes_empty_after_delete(self):
#         async with AsyncClient(app=app, base_url="http://test") as client:
#             yield client
#         response = await client.get(f"/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}/dishes")
#         assert response.status_code == 200
#         assert TestDishAPI.dish_id not in [dish["id"] for dish in response.json()]