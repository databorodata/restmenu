import pytest

from httpx import AsyncClient
from tests.conftest import client
# from app.models import Menu, Submenu
# from app.schemas import CreateEditMenuModel, CreateEditSubmenuModel

# @pytest.mark.usefixtures("db_session", "create_test_database")


class TestSubmenuAPI:
    menu_id = None
    submenu_id = None

    @pytest.mark.asyncio
    async def test_1_create_menu_for_submenu(self, client: AsyncClient):
        data = {"title": "Test Menu", "description": "Test Description"}
        response = await client.post("/api/v1/menus/", json=data)
        assert response.status_code == 201
        TestSubmenuAPI.menu_id = response.json()["id"]
        print('test_1_create_menu_for_submenu !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_2_get_submenus_empty(self, client: AsyncClient):
        print('rrrrrrrrrrrrrrrrrrrrrr', TestSubmenuAPI.menu_id)
        response = await client.get(f"/api/v1/menus/{TestSubmenuAPI.menu_id}/submenus/")
        print(response.json())
        assert response.status_code == 200
        assert response.json() == []
        print('test_2_get_submenus_empty !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_3_create_submenu(self, client: AsyncClient):
        data = {"title": "Test Submenu", "description": "Test Submenu Description"}
        response = await client.post(f"/api/v1/menus/{TestSubmenuAPI.menu_id}/submenus/", json=data)
        assert response.status_code == 201
        TestSubmenuAPI.submenu_id = response.json()["id"]
        print('test_3_create_submenu !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_4_get_all_submenus(self, client: AsyncClient):
        response = await client.get(f"/api/v1/menus/{TestSubmenuAPI.menu_id}/submenus/")
        assert response.status_code == 200
        assert TestSubmenuAPI.submenu_id in [submenu["id"] for submenu in response.json()]
        print('test_4_get_all_submenus !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_5_get_specific_submenu(self, client: AsyncClient):
        response = await client.get(f"/api/v1/menus/{TestSubmenuAPI.menu_id}/submenus/{TestSubmenuAPI.submenu_id}")
        assert response.status_code == 200
        assert response.json()["id"] == TestSubmenuAPI.submenu_id
        print('test_5_get_specific_submenu !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_6_update_submenu(self, client: AsyncClient):
        update_data = {"title": "Updated Submenu", "description": "Updated Description"}
        response = await client.patch(f"/api/v1/menus/{TestSubmenuAPI.menu_id}/submenus/{TestSubmenuAPI.submenu_id}",
                                      json=update_data)
        assert response.status_code == 200
        print('test_6_update_submenu !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_7_get_specific_submenu_after_update(self, client: AsyncClient):
        response = await client.get(f"/api/v1/menus/{TestSubmenuAPI.menu_id}/submenus/{TestSubmenuAPI.submenu_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Submenu"
        print('test_7_get_specific_submenu_after_update !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_8_delete_submenu(self, client: AsyncClient):
        response = await client.delete(f"/api/v1/menus/{TestSubmenuAPI.menu_id}/submenus/{TestSubmenuAPI.submenu_id}")
        assert response.status_code == 200
        print('test_8_delete_submenu !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_9_get_submenus_empty_after_delete(self, client: AsyncClient):
        response = await client.get(f"/api/v1/menus/{TestSubmenuAPI.menu_id}/submenus/")
        assert response.status_code == 200
        assert TestSubmenuAPI.submenu_id not in [submenu["id"] for submenu in response.json()]
        print('test_9_get_submenus_empty_after_delete !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_10_delete_menu_for_submenu(self, client: AsyncClient):
        response = await client.delete(f"/api/v1/menus/{TestSubmenuAPI.menu_id}")
        assert response.status_code == 200
        print('test_10_delete_menu !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_11_get_menus_empty(self, client: AsyncClient):
        response = await client.get("/api/v1/menus/")
        assert response.status_code == 200
        assert response.json() == []
        print('test_11_get_menus_empty !!!!!!!!!!!!! PASSED')