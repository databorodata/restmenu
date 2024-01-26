import pytest

from httpx import AsyncClient
from tests.conftest import client


class TestMenuAPI:
    menu_id = None

    @pytest.mark.asyncio
    async def test_1_get_menus_empty(self, client: AsyncClient):
        response = await client.get("/api/v1/menus/")
        assert response.status_code == 200
        assert response.json() == []
        print('test_1_get_menus_empty !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_2_create_menu(self, client: AsyncClient):
        data = {"title": "Test Menu", "description": "Test Description"}
        response = await client.post("/api/v1/menus/", json=data)
        assert response.status_code == 201
        TestMenuAPI.menu_id = response.json()["id"]
        print('test_2_create_menu !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_3_get_all_menus(self, client: AsyncClient):
        response = await client.get("/api/v1/menus/")
        assert response.status_code == 200
        assert TestMenuAPI.menu_id in [menu["id"] for menu in response.json()]
        print('test_3_get_all_menus !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_4_get_specific_menu(self, client: AsyncClient):
        response = await client.get(f"/api/v1/menus/{TestMenuAPI.menu_id}")
        assert response.status_code == 200
        assert response.json()["id"] == TestMenuAPI.menu_id
        print('test_4_get_specific_menu !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_5_update_menu(self, client: AsyncClient):
        update_data = {"title": "Updated Test Menu", "description": "Updated Description"}
        response = await client.patch(f"/api/v1/menus/{TestMenuAPI.menu_id}", json=update_data)
        assert response.status_code == 200
        print('test_5_update_menu !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_6_get_specific_menu_after_update(self, client: AsyncClient):
        response = await client.get(f"/api/v1/menus/{TestMenuAPI.menu_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Test Menu"
        print('test_6_get_specific_menu_after_update !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_7_delete_menu(self, client: AsyncClient):
        response = await client.delete(f"/api/v1/menus/{TestMenuAPI.menu_id}")
        assert response.status_code == 200
        print('test_7_delete_menu !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_8_get_menus_empty_after_delete(self, client: AsyncClient):
        response = await client.get("/api/v1/menus/")
        assert response.status_code == 200
        assert TestMenuAPI.menu_id not in [menu["id"] for menu in response.json()]
        print('test_8_get_menus_empty_after_delete !!!!!!!!!!!!! PASSED')
