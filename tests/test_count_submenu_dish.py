# import pytest
# from httpx import AsyncClient
# from app.main import app
# from app.models import Menu, Submenu
# from app.schemas import CreateEditMenuModel, CreateEditSubmenuModel
# from test_fixtures import create_test_database, db_session
#
# @pytest.mark.usefixtures("db_session", "create_test_database")
# class TestCountSubmenuDishAPI:
#     menu_id = None
#     submenu_id = None
#     dish1_id = None
#     dish2_id = None
#
#     @pytest.mark.asyncio
#     async def test_1_create_menu(self, client):
#         data = {"title": "Test Menu", "description": "Test Description"}
#         response = await client.post("/api/v1/menus/", json=data)
#         assert response.status_code == 201
#         TestCountSubmenuDishAPI.menu_id = response.json()["id"]
#
#     @pytest.mark.asyncio
#     async def test_2_create_submenu(self, client):
#         data = {"title": "Test Submenu", "description": "Test Submenu Description"}
#         response = await client.post(f"/api/v1/menus/{self.menu_id}/submenus", json=data)
#         assert response.status_code == 201
#         TestCountSubmenuDishAPI.submenu_id = response.json()["id"]
#
#     @pytest.mark.asyncio
#     async def test_3_create_dish_1(self, client):
#         data = {"title": "Test Dish 1", "description": "Dish Description 1", "price": "10.99"}
#         response = await client.post(f"/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}/dishes", json=data)
#         assert response.status_code == 201
#         TestCountSubmenuDishAPI.dish1_id = response.json()["id"]
#
#     @pytest.mark.asyncio
#     async def test_4_create_dish_2(self, client):
#         data = {"title": "Test Dish 2", "description": "Dish Description 2", "price": "12.99"}
#         response = await client.post(f"/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}/dishes", json=data)
#         assert response.status_code == 201
#         TestCountSubmenuDishAPI.dish2_id = response.json()["id"]
#
#     @pytest.mark.asyncio
#     async def test_5_get_specific_menu(self, client):
#         response = await client.get(f"/api/v1/menus/{self.menu_id}")
#         assert response.status_code == 200
#         menu_data = response.json()
#         assert menu_data["id"] == TestCountSubmenuDishAPI.menu_id
#         assert menu_data["submenus_count"] == 1
#         assert menu_data["dishes_count"] == 2
#
#     @pytest.mark.asyncio
#     async def test_6_get_specific_submenu(self, client):
#         response = await client.get(f"/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}")
#         assert response.status_code == 200
#         submenu_data = response.json()
#         assert submenu_data["id"] == TestCountSubmenuDishAPI.submenu_id
#         assert submenu_data["dishes_count"] == 2
#
#     @pytest.mark.asyncio
#     async def test_7_delete_submenu(self, client):
#         response = await client.delete(f"/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}")
#         assert response.status_code == 200
#
#     @pytest.mark.asyncio
#     async def test_8_get_submenus_empty(self, client):
#         response = await client.get(f"/api/v1/menus/{self.menu_id}/submenus")
#         assert response.status_code == 200
#         assert response.json() == []
#
#     @pytest.mark.asyncio
#     async def test_9_get_dishes_empty(self, client):
#         response = await client.get(f"/api/v1/menus/{self.menu_id}/submenus/{self.submenu_id}/dishes")
#         assert response.status_code == 200
#         assert response.json() == []
#
#     @pytest.mark.asyncio
#     async def test_10_get_specific_menu_after_deletion(self, client):
#         response = await client.get(f"/api/v1/menus/{self.menu_id}")
#         assert response.status_code == 200
#         menu_data = response.json()
#         assert menu_data["id"] == TestCountSubmenuDishAPI.menu_id
#         assert menu_data["submenus_count"] == 0
#         assert menu_data["dishes_count"] == 0
#
#     @pytest.mark.asyncio
#     async def test_11_delete_menu(self, client):
#         response = await client.delete(f"/api/v1/menus/{self.menu_id}")
#         assert response.status_code == 200
#
#     @pytest.mark.asyncio
#     async def test_12_get_menus_empty(self, client):
#         response = await client.get("/api/v1/menus/")
#         assert response.status_code == 200
#         assert response.json() == []
