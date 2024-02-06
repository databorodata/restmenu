import pytest
from httpx import AsyncClient

from app.repositories.dish_repository import DishRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.submenu_repository import SubmenuRepository
from tests.utils import reverse


class TestCountSubmenuDishAPI:
    menu_id: str | None = None
    submenu_id: str | None = None
    dish1_id: str | None = None
    dish2_id: str | None = None

    @pytest.mark.asyncio
    async def test_create_menu_then_menu_created(
            self,
            client: AsyncClient,
            menu_repo: MenuRepository
    ) -> None:
        """Тест создает меню и ожидает успех."""
        data = {'title': 'menu 1', 'description': 'description 1'}
        response = await client.post(reverse('create_menu'), json=data)
        assert response.status_code == 201
        TestCountSubmenuDishAPI.menu_id = response.json()['id']

    @pytest.mark.asyncio
    async def test_create_submenu_then_submenu_created(
            self,
            client: AsyncClient,
            submenu_repo: SubmenuRepository
    ) -> None:
        """Тест создает подменю и ожидает успех."""
        data = {'title': 'Test Submenu', 'description': 'Test Submenu Description'}
        response = await client.post(
            reverse(
                'create_submenu',
                menu_id=self.menu_id
            ),
            json=data
        )
        assert response.status_code == 201
        TestCountSubmenuDishAPI.submenu_id = response.json()['id']

    @pytest.mark.asyncio
    async def test_create_first_dish_then_dish_created(
            self,
            client: AsyncClient,
            dish_repo: DishRepository
    ) -> None:
        """Тест создает первое блюдо и ожидает успех."""
        data = {'title': 'Test Dish 1', 'description': 'Dish Description 1', 'price': '10.33'}
        response = await client.post(
            reverse(
                'create_dish',
                menu_id=self.menu_id,
                submenu_id=self.submenu_id
            ),
            json=data
        )
        assert response.status_code == 201
        TestCountSubmenuDishAPI.dish1_id = response.json()['id']

    @pytest.mark.asyncio
    async def test_create_second_dish_then_dish_created(
            self,
            client: AsyncClient,
            dish_repo: DishRepository
    ) -> None:
        """Тест создает второе блюдо и ожидает успех."""
        data = {'title': 'Test Dish 2', 'description': 'Dish Description 2', 'price': '12.22'}
        response = await client.post(
            reverse(
                'create_dish',
                menu_id=self.menu_id,
                submenu_id=self.submenu_id
            ),
            json=data
        )
        assert response.status_code == 201
        TestCountSubmenuDishAPI.dish2_id = response.json()['id']

    @pytest.mark.asyncio
    async def test_get_menu_with_counts_then_counts_correct(self, client: AsyncClient) -> None:
        """Тест проверяет кол-во подменю и блюд в меню."""
        response = await client.get(reverse('get_menu', menu_id=self.menu_id))
        assert response.status_code == 200
        menu_data = response.json()
        assert menu_data['id'] == TestCountSubmenuDishAPI.menu_id
        assert menu_data['submenus_count'] == 1
        assert menu_data['dishes_count'] == 2

    @pytest.mark.asyncio
    async def test_get_submenu_with_count_then_count_correct(self, client: AsyncClient) -> None:
        """Тест проверяет кол-во блюд в подменю."""
        response = await client.get(
            reverse(
                'get_submenu',
                menu_id=self.menu_id,
                submenu_id=self.submenu_id
            )
        )
        assert response.status_code == 200
        submenu_data = response.json()
        assert submenu_data['id'] == TestCountSubmenuDishAPI.submenu_id
        assert submenu_data['dishes_count'] == 2

    @pytest.mark.asyncio
    async def test_delete_submenu_then_submenu_removed(self, client: AsyncClient) -> None:
        """Тест удаляет подменю."""
        response = await client.delete(
            reverse(
                'delete_submenu',
                menu_id=self.menu_id,
                submenu_id=self.submenu_id
            )
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_submenus_after_deletion_then_empty(self, client: AsyncClient) -> None:
        """Тест проверяет список подменю."""
        response = await client.get(
            reverse(
                'get_submenus',
                menu_id=self.menu_id
            )
        )
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_dishes_after_submenu_deletion_then_empty(self, client: AsyncClient) -> None:
        """Тест проверяет список блюд."""
        response = await client.get(
            reverse(
                'get_dishes',
                menu_id=self.menu_id,
                submenu_id=self.submenu_id
            )
        )
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_menu_after_submenu_deletion_then_counts_updated(self, client: AsyncClient) -> None:
        """Тест проверяет кол-во блюд и подменю в меню."""
        response = await client.get(
            reverse(
                'get_menu',
                menu_id=self.menu_id
            )
        )
        assert response.status_code == 200
        menu_data = response.json()
        assert menu_data['id'] == TestCountSubmenuDishAPI.menu_id
        assert menu_data['submenus_count'] == 0
        assert menu_data['dishes_count'] == 0

    @pytest.mark.asyncio
    async def test_delete_menu_then_menu_removed(self, client: AsyncClient) -> None:
        """Тест удаляет меню."""
        response = await client.delete(
            reverse(
                'delete_menu',
                menu_id=self.menu_id
            )
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_menus_after_menu_deletion_then_empty(self, client: AsyncClient) -> None:
        """Тест проверяет список меню."""
        response = await client.get(reverse('get_menus'))
        assert response.status_code == 200
        assert response.json() == []
