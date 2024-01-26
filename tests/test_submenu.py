# import pytest
# from httpx import AsyncClient
# from app.main import app
# from app.models import Menu, Submenu
# from app.schemas import CreateEditMenuModel, CreateEditSubmenuModel
# from test_fixtures import create_test_database, db_session
#
# @pytest.mark.usefixtures("db_session", "create_test_database")
# class TestSubmenuAPI:
#     menu_id = None
#     submenu_id = None
#
#     @pytest.fixture(autouse=True)
#     async def setup(self, db_session):
#         # Создание меню для тестирования подменю
#         new_menu = Menu(title="Test Menu", description="Test Description")
#         db_session.add(new_menu)
#         await db_session.commit()
#         TestSubmenuAPI.menu_id = new_menu.id
#         print(new_menu.id)
#
#         yield  # После завершения тестов
#
#         # Очистка данных
#         await db_session.delete(new_menu)
#         await db_session.commit()
#
#     @pytest.mark.asyncio
#     async def test_1_get_submenus_empty(self):
#         async with AsyncClient(app=app, base_url="http://test") as client:
#             yield client
#         response = await client.get(f"/api/v1/menus/{self.menu_id}/submenus")
#         assert response.status_code == 200
#         assert response.json() == []
#
#     @pytest.mark.asyncio
#     async def test_2_create_submenu(self):
#         async with AsyncClient(app=app, base_url="http://test") as client:
#             yield client
#         data = {"title": "Test Submenu", "description": "Test Submenu Description"}
#         response = await client.post(f"/api/v1/menus/{self.menu_id}/submenus", json=data)
#         assert response.status_code == 201
#         TestSubmenuAPI.submenu_id = response.json()["id"]
#
#     @pytest.mark.asyncio
#     async def test_3_get_all_submenus(self):
#         async with AsyncClient(app=app, base_url="http://test") as client:
#             yield client
#         response = await client.get(f"/api/v1/menus/{self.menu_id}/submenus")
#         assert response.status_code == 200
#         assert TestSubmenuAPI.submenu_id in [submenu["id"] for submenu in response.json()]
#
#     @pytest.mark.asyncio
#     async def test_4_get_specific_submenu(self):
#         async with AsyncClient(app=app, base_url="http://test") as client:
#             yield client
#         response = await client.get(f"/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}")
#         assert response.status_code == 200
#         assert response.json()["id"] == TestSubmenuAPI.submenu_id
#
#     @pytest.mark.asyncio
#     async def test_5_update_submenu(self):
#         async with AsyncClient(app=app, base_url="http://test") as client:
#             yield client
#         update_data = {"title": "Updated Submenu", "description": "Updated Description"}
#         response = await client.patch(f"/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}", json=update_data)
#         assert response.status_code == 200
#
#     @pytest.mark.asyncio
#     async def test_6_get_specific_submenu_after_update(self):
#         async with AsyncClient(app=app, base_url="http://test") as client:
#             yield client
#         response = await client.get(f"/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}")
#         assert response.status_code == 200
#         assert response.json()["title"] == "Updated Submenu"
#
#     @pytest.mark.asyncio
#     async def test_7_delete_submenu(self):
#         async with AsyncClient(app=app, base_url="http://test") as client:
#             yield client
#         response = await client.delete(f"/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}")
#         assert response.status_code == 200
#
#     @pytest.mark.asyncio
#     async def test_8_get_submenus_empty_after_delete(self):
#         async with AsyncClient(app=app, base_url="http://test") as client:
#             yield client
#         response = await client.get(f"/api/v1/menus/{self.menu_id}/submenus")
#         assert response.status_code == 200
#         assert TestSubmenuAPI.submenu_id not in [submenu["id"] for submenu in response.json()]