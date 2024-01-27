import pytest
from httpx import AsyncClient
from tests.conftest import client


class TestSubmenuAPI:
    menu_id = None
    submenu_id = None

    @pytest.fixture(scope="function")
    async def create_menu_submenu_fixture(self, client: AsyncClient):
        data_menu = {"title": "Test Menu", "description": "Test Description"}
        response = await client.post("/api/v1/menus/", json=data_menu)
        assert response.status_code == 201
        TestSubmenuAPI.menu_id = response.json()["id"]

        data_submenu = {"title": "Test Submenu", "description": "Test Submenu Description"}
        response = await client.post(f"/api/v1/menus/{TestSubmenuAPI.menu_id}/submenus/", json=data_submenu)
        assert response.status_code == 201
        TestSubmenuAPI.submenu_id = response.json()["id"]
        yield

    @pytest.fixture(scope="function")
    async def delete_menu_submenu_fixture(self, client: AsyncClient):
        yield
        await client.delete(f"/api/v1/menus/{TestSubmenuAPI.menu_id}")
        TestSubmenuAPI.menu_id = None
        TestSubmenuAPI.submenu_id = None

    @pytest.mark.usefixtures('create_menu_submenu_fixture', 'delete_menu_submenu_fixture')
    async def test_create_submenu(self, client: AsyncClient):
        response = await client.get(f"/api/v1/menus/{TestSubmenuAPI.menu_id}/submenus/{TestSubmenuAPI.submenu_id}")
        assert response.json()["title"] == "Test Submenu"
        assert response.json()["description"] == "Test Submenu Description"

    @pytest.mark.usefixtures('create_menu_submenu_fixture', 'delete_menu_submenu_fixture')
    async def test_get_submenu(self, client: AsyncClient):
        response = await client.get(f"/api/v1/menus/{TestSubmenuAPI.menu_id}/submenus/{TestSubmenuAPI.submenu_id}")
        assert response.status_code == 200
        assert response.json()["id"] == TestSubmenuAPI.submenu_id

    @pytest.mark.usefixtures('create_menu_submenu_fixture', 'delete_menu_submenu_fixture')
    async def test_submenu_update(self, client: AsyncClient):
        update_data = {"title": "Updated Submenu", "description": "Updated Description"}
        response = await client.patch(f"/api/v1/menus/{TestSubmenuAPI.menu_id}/submenus/{TestSubmenuAPI.submenu_id}",
                                      json=update_data)
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Submenu"
        assert response.json()["description"] == "Updated Description"

    @pytest.mark.usefixtures('create_menu_submenu_fixture')
    async def test_submenu_delete(self, client: AsyncClient):
        response = await client.delete(f"/api/v1/menus/{TestSubmenuAPI.menu_id}/submenus/{TestSubmenuAPI.submenu_id}")
        assert response.status_code == 200
        response = await client.get(f"/api/v1/menus/{TestSubmenuAPI.menu_id}/submenus/{TestSubmenuAPI.submenu_id}")
        assert response.status_code == 404
