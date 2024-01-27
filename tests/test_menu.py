import pytest
from httpx import AsyncClient
from tests.conftest import client


class TestMenuAPI:
    menu_id = None

    @pytest.fixture(scope="function")
    async def create_menu_fixture(self, client: AsyncClient):
        data = {"title": "Test Menu", "description": "Test Description"}
        response = await client.post("/api/v1/menus/", json=data)
        assert response.status_code == 201
        TestMenuAPI.menu_id = response.json()["id"]
        yield

    @pytest.fixture(scope="function")
    async def delete_menu_fixture(self, client: AsyncClient):
        yield
        await client.delete(f"/api/v1/menus/{TestMenuAPI.menu_id}")
        TestMenuAPI.menu_id = None

    @pytest.mark.usefixtures('create_menu_fixture', 'delete_menu_fixture')
    async def test_menu_create(self, client: AsyncClient):
        # data = {"title": "Test Menu", "description": "Test Description"}
        # response = await client.post("/api/v1/menus/", json=data)
        response = await client.get(f"/api/v1/menus/{TestMenuAPI.menu_id}")
        assert response.json()["title"] == "Test Menu"
        assert response.json()["description"] == "Test Description"
        # TestMenuAPI.menu_id = response.json()["id"]

    @pytest.mark.usefixtures('create_menu_fixture', 'delete_menu_fixture')
    async def test_get_menu(self, client: AsyncClient):
        response = await client.get(f"/api/v1/menus/{TestMenuAPI.menu_id}")
        assert response.status_code == 200
        assert response.json()["id"] == TestMenuAPI.menu_id

    @pytest.mark.usefixtures('create_menu_fixture', 'delete_menu_fixture')
    async def test_menu_update(self, client: AsyncClient):
        update_data = {"title": "Updated Test Menu", "description": "Updated Description"}
        response = await client.patch(f"/api/v1/menus/{TestMenuAPI.menu_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Test Menu"
        assert response.json()["description"] == "Updated Description"

    @pytest.mark.usefixtures('create_menu_fixture')
    async def test_menu_delete(self, client: AsyncClient):
        response = await client.delete(f"/api/v1/menus/{TestMenuAPI.menu_id}")
        assert response.status_code == 200
        response = await client.get(f"/api/v1/menus/{TestMenuAPI.menu_id}")
        assert response.status_code == 404
