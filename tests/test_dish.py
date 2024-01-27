import pytest
from httpx import AsyncClient
from tests.conftest import client


class TestDishAPI:
    menu_id = None
    submenu_id = None
    dish_id = None

    @pytest.fixture(scope="function")
    async def create_menu_submenu_dish_fixture(self, client: AsyncClient):
        data_menu = {"title": "Test Menu", "description": "Test Description"}
        response = await client.post("/api/v1/menus/", json=data_menu)
        assert response.status_code == 201
        TestDishAPI.menu_id = response.json()["id"]

        data_submenu = {"title": "Test Submenu", "description": "Test Submenu Description"}
        response = await client.post(f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/", json=data_submenu)
        assert response.status_code == 201
        TestDishAPI.submenu_id = response.json()["id"]

        data_dish = {"title": "Test Dish", "description": "Test Dish Description", "price": "42.42"}
        response = await (client
                          .post(f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/{TestDishAPI.submenu_id}/dishes/"
                                ,json=data_dish))
        assert response.status_code == 201
        TestDishAPI.dish_id = response.json()["id"]
        yield

    @pytest.fixture(scope="function")
    async def delete_menu_submenu_dish_fixture(self, client: AsyncClient):
        yield
        await client.delete(f"/api/v1/menus/{TestDishAPI.menu_id}")
        TestDishAPI.menu_id = None
        TestDishAPI.submenu_id = None
        TestDishAPI.dish_id = None

    @pytest.mark.usefixtures('create_menu_submenu_dish_fixture', 'delete_menu_submenu_dish_fixture')
    async def test_create_dish(self, client: AsyncClient):
        response = await (client.get(
            f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/{TestDishAPI.submenu_id}/dishes/{TestDishAPI.dish_id}"))
        assert response.json()["title"] == "Test Dish"
        assert response.json()["description"] == "Test Dish Description"
        assert response.json()["price"] == "42.42"

    @pytest.mark.usefixtures('create_menu_submenu_dish_fixture', 'delete_menu_submenu_dish_fixture')
    async def test_get_dish(self, client: AsyncClient):
        response = await (client.get(
            f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/{TestDishAPI.submenu_id}/dishes/{TestDishAPI.dish_id}"))
        assert response.status_code == 200
        assert response.json()["id"] == TestDishAPI.dish_id

    @pytest.mark.usefixtures('create_menu_submenu_dish_fixture', 'delete_menu_submenu_dish_fixture')
    async def test_dish_update(self, client: AsyncClient):
        update_data = {"title": "Updated Dish", "description": "Updated Description", "price": "42.42"}
        response = await (client.patch(
            f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/{TestDishAPI.submenu_id}/dishes/{TestDishAPI.dish_id}",
            json=update_data))
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Dish"
        assert response.json()["description"] == "Updated Description"
        assert response.json()["price"] == "42.42"

    @pytest.mark.usefixtures('create_menu_submenu_dish_fixture')
    async def test_dish_delete(self, client: AsyncClient):
        response = await (client.delete(
            f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/{TestDishAPI.submenu_id}/dishes/{TestDishAPI.dish_id}"))
        assert response.status_code == 200
        response = await (client.get(
            f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/{TestDishAPI.submenu_id}/dishes/{TestDishAPI.dish_id}"))
        assert response.status_code == 404
