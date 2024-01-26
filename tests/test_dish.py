import pytest

from httpx import AsyncClient
from tests.conftest import client


class TestDishAPI:
    menu_id = None
    submenu_id = None
    dish_id = None

    # @pytest.fixture(autouse=True)
    # async def setup(self, db_session):
    #     # Создание меню и подменю для тестирования блюд
    #     new_menu = Menu(title="Test Menu", description="Test Description")
    #     new_submenu = Submenu(title="Test Submenu", description="Test Submenu Description", menu_id=new_menu.id)
    #     db_session.add(new_menu)
    #     db_session.add(new_submenu)
    #     await db_session.commit()
    #     TestDishAPI.menu_id = new_menu.id
    #     TestDishAPI.submenu_id = new_submenu.id
    #
    #     yield  # После завершения тестов
    #
    #     # Очистка данных
    #     await db_session.delete(new_menu)
    #     print('!!!!!!!!!!!!!!!!!!!!!!delete')
    #     await db_session.delete(new_submenu)
    #     await db_session.commit()

    @pytest.mark.asyncio
    async def test_1_create_menu_for_dish(self, client: AsyncClient):
        data = {"title": "Test Menu", "description": "Test Description"}
        response = await client.post("/api/v1/menus/", json=data)
        assert response.status_code == 201
        TestDishAPI.menu_id = response.json()["id"]
        print('test_1_create_menu_for_dish !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_2_create_submenu_for_dish(self, client: AsyncClient):
        data = {"title": "Test Submenu", "description": "Test Submenu Description"}
        response = await client.post(f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/", json=data)
        assert response.status_code == 201
        TestDishAPI.submenu_id = response.json()["id"]
        print('test_2_create_submenu_for_dish !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_3_get_dishes_empty(self, client: AsyncClient):
        response = await client.get(f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/{TestDishAPI.submenu_id}/dishes/")
        assert response.status_code == 200
        assert response.json() == []
        print('test_3_get_dishes_empty !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_4_create_dish(self, client: AsyncClient):
        data = {"title": "Test Dish", "description": "Test Dish Description", "price": "10.99"}
        response = await (client
                          .post(f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/{TestDishAPI.submenu_id}/dishes/",
                                     json=data))
        assert response.status_code == 201
        TestDishAPI.dish_id = response.json()["id"]
        print('test_4_create_dish !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_5_get_all_dishes(self, client: AsyncClient):
        response = await client.get(f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/{TestDishAPI.submenu_id}/dishes/")
        assert response.status_code == 200
        assert TestDishAPI.dish_id in [dish["id"] for dish in response.json()]
        print('test_5_get_all_dishes !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_6_get_specific_dish(self, client: AsyncClient):
        response = await (client
                          .get(f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/{TestDishAPI.submenu_id}/dishes/{TestDishAPI.dish_id}"))
        assert response.status_code == 200
        assert response.json()["id"] == TestDishAPI.dish_id
        print('test_6_get_specific_dish !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_7_update_dish(self, client: AsyncClient):
        update_data = {"title": "Updated Dish", "description": "Updated Description", "price": "15.01"}
        response = await (client
                          .patch(f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/{TestDishAPI.submenu_id}/dishes/{TestDishAPI.dish_id}",
                                      json=update_data))
        assert response.status_code == 200
        print('test_7_update_dish !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_8_get_specific_dish_after_update(self, client: AsyncClient):
        response = await (client
                          .get(f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/{TestDishAPI.submenu_id}/dishes/{TestDishAPI.dish_id}"))
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Dish"
        print('test_8_get_specific_dish_after_update !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_9_delete_dish(self, client: AsyncClient):
        response = await (client
                          .delete(f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/{TestDishAPI.submenu_id}/dishes/{TestDishAPI.dish_id}"))
        assert response.status_code == 200
        print('test_9_delete_dish !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_10_get_dishes_empty_after_delete(self, client: AsyncClient):
        response = await client.get(f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/{TestDishAPI.submenu_id}/dishes/")
        assert response.status_code == 200
        assert TestDishAPI.dish_id not in [dish["id"] for dish in response.json()]
        print('test_10_get_dishes_empty_after_delete !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_11_delete_submenu_for_dish(self, client: AsyncClient):
        response = await client.delete(f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/{TestDishAPI.submenu_id}")
        assert response.status_code == 200
        print('test_11_delete_submenu !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_12_get_submenus_empty_after_delete(self, client: AsyncClient):
        response = await client.get(f"/api/v1/menus/{TestDishAPI.menu_id}/submenus/")
        assert response.status_code == 200
        assert TestDishAPI.submenu_id not in [submenu["id"] for submenu in response.json()]
        print('test_12_get_submenus_empty_after_delete !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_13_delete_menu_for_dish(self, client: AsyncClient):
        response = await client.delete(f"/api/v1/menus/{TestDishAPI.menu_id}")
        assert response.status_code == 200
        print('test_10_delete_menu !!!!!!!!!!!!! PASSED')

    @pytest.mark.asyncio
    async def test_14_get_menus_empty(self, client: AsyncClient):
        response = await client.get("/api/v1/menus/")
        assert response.status_code == 200
        assert response.json() == []
        print('test_14_get_menus_empty !!!!!!!!!!!!! PASSED')