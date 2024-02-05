import pytest
from httpx import AsyncClient

from tests.conftest import client

from app.repositories.dish_repository import DishRepository
from app.repositories.submenu_repository import SubmenuRepository
from app.repositories.menu_repository import MenuRepository
from app.routers.router_dish import router as router_dish
from app.routers.router_menu import router as router_menu
from app.routers.router_submenu import router as router_submenu


class TestCountSubmenuDishAPI:
    menu_id = None
    submenu_id = None
    dish1_id = None
    dish2_id = None

    @pytest.mark.asyncio
    async def test_1_create_menu_for_count(self, client: AsyncClient, menu_repo: MenuRepository):
        data = {'title': 'menu 1', 'description': 'description 1'}
        response = await client.post(router_menu.url_path_for('create_menu'), json=data)
        assert response.status_code == 201
        TestCountSubmenuDishAPI.menu_id = response.json()['id']

    @pytest.mark.asyncio
    async def test_2_create_submenu_for_count(self, client: AsyncClient, submenu_repo: SubmenuRepository):
        data = {'title': 'Test Submenu', 'description': 'Test Submenu Description'}
        response = await client.post(router_submenu.url_path_for('create_submenu', menu_id=self.menu_id), json=data)
        assert response.status_code == 201
        TestCountSubmenuDishAPI.submenu_id = response.json()['id']

    @pytest.mark.asyncio
    async def test_3_create_dish_1_for_count(self, client: AsyncClient, dish_repo: DishRepository):
        data = {'title': 'Test Dish 1', 'description': 'Dish Description 1', 'price': '10.33'}
        response = await client.post(
            router_dish.url_path_for('create_dish', menu_id=self.menu_id, submenu_id=self.submenu_id),
            json=data)
        assert response.status_code == 201
        TestCountSubmenuDishAPI.dish1_id = response.json()['id']

    @pytest.mark.asyncio
    async def test_4_create_dish_2_for_count(self, client: AsyncClient, dish_repo: DishRepository):
        data = {'title': 'Test Dish 2', 'description': 'Dish Description 2', 'price': '12.22'}
        response = await client.post(
            router_dish.url_path_for('create_dish', menu_id=self.menu_id, submenu_id=self.submenu_id),
            json=data)
        assert response.status_code == 201
        TestCountSubmenuDishAPI.dish2_id = response.json()['id']

    @pytest.mark.asyncio
    async def test_5_get_specific_menu_for_count(self, client: AsyncClient):
        response = await client.get(router_menu.url_path_for('get_menu', menu_id=self.menu_id))
        assert response.status_code == 200
        menu_data = response.json()
        assert menu_data['id'] == TestCountSubmenuDishAPI.menu_id
        assert menu_data['submenus_count'] == 1
        assert menu_data['dishes_count'] == 2

    @pytest.mark.asyncio
    async def test_6_get_specific_submenu_for_count(self, client: AsyncClient):
        response = await client.get(router_submenu.url_path_for('get_submenu', menu_id=self.menu_id, submenu_id=self.submenu_id))
        assert response.status_code == 200
        submenu_data = response.json()
        assert submenu_data['id'] == TestCountSubmenuDishAPI.submenu_id
        assert submenu_data['dishes_count'] == 2

    @pytest.mark.asyncio
    async def test_7_delete_submenu_for_count(self, client: AsyncClient):
        response = await client.delete(router_submenu.url_path_for('delete_submenu', menu_id=self.menu_id, submenu_id=self.submenu_id))
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_8_get_submenus_empty_for_count(self, client: AsyncClient):
        response = await client.get(router_submenu.url_path_for('get_submenus', menu_id=self.menu_id))
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_9_get_dishes_empty_for_count(self, client: AsyncClient):
        response = await client.get(router_dish.url_path_for('get_dishes', menu_id=self.menu_id, submenu_id=self.submenu_id))
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_10_get_specific_menu_after_deletion_for_count(self, client: AsyncClient):
        response = await client.get(router_menu.url_path_for('get_menu', menu_id=self.menu_id))
        assert response.status_code == 200
        menu_data = response.json()
        assert menu_data['id'] == TestCountSubmenuDishAPI.menu_id
        assert menu_data['submenus_count'] == 0
        assert menu_data['dishes_count'] == 0

    @pytest.mark.asyncio
    async def test_11_delete_menu_for_count(self, client: AsyncClient):
        response = await client.delete(router_menu.url_path_for('delete_menu', menu_id=self.menu_id))
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_12_get_menus_empty_for_count(self, client: AsyncClient):
        response = await client.get(router_menu.url_path_for('get_menus'))
        assert response.status_code == 200
        assert response.json() == []
