import uuid
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Dish, Menu, Submenu
from app.repositories.dish_repository import DishRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.submenu_repository import SubmenuRepository
from app.routers.router_dish import router as router_dish
from app.routers.router_menu import router as router_menu
from app.routers.router_submenu import router as router_submenu


class TestDishAPI:

    @pytest.fixture(scope='function')
    async def create_dish_fixture(
            self,
            client: AsyncClient,
            menu_repo: MenuRepository,
            submenu_repo: SubmenuRepository,
            dish_repo: DishRepository
    ) -> AsyncGenerator[tuple[Menu, Submenu, Dish], None]:
        """Фикстура для создания блюда для тестирования."""
        new_menu = await menu_repo.create_menu({
            'title': 'menu 1',
            'description': 'description 1',
            'id': uuid.uuid4()
        })

        new_submenu = await submenu_repo.create_submenu({
            'title': 'Test Submenu',
            'description': 'Test Submenu Description',
            'menu_id': new_menu.id,
            'id': uuid.uuid4()
        })

        new_dish = await dish_repo.create_dish({
            'title': 'Test Submenu',
            'description': 'Test Submenu Description',
            'price': '42.42',
            'menu_id': new_menu.id,
            'submenu_id': new_submenu.id,
            'id': uuid.uuid4()
        })

        yield new_menu, new_submenu, new_dish

    async def test_when_create_dish_then_success(
            self,
            client: AsyncClient,
            menu_repo: MenuRepository,
            submenu_repo: SubmenuRepository,
            dish_repo: DishRepository
    ):
        """Тест создает блюдо и ожидает успех."""
        data_menu = {'title': 'menu 1', 'description': 'description 1'}
        response_menu = await client.post(
            router_menu.url_path_for(
                'create_menu'),
            json=data_menu
        )
        menu_id = response_menu.json()['id']

        data_submenu = {'title': 'Test Submenu', 'description': 'Test Submenu Description'}
        response_submenu = await client.post(
            router_submenu.url_path_for(
                'create_submenu',
                menu_id=menu_id),
            json=data_submenu
        )
        submenu_id = response_submenu.json()['id']

        data_dish = {'title': 'Test Dish', 'description': 'Test Dish Description', 'price': '42.42'}
        response_dish = await client.post(
            router_dish.url_path_for(
                'create_dish',
                menu_id=menu_id,
                submenu_id=submenu_id),
            json=data_dish
        )
        dish_id = response_dish.json()['id']

        dish = await dish_repo.get_dish_by_id(dish_id)

        assert dish is not None
        assert response_dish.status_code == 201
        assert response_dish.json()['id'] == str(dish.id)
        assert response_dish.json()['title'] == dish.title
        assert response_dish.json()['description'] == dish.description
        assert response_dish.json()['price'] == '42.42'

    @pytest.mark.usefixtures('create_dish_fixture')
    async def test_when_get_dish_then_details_correct(
            self,
            client: AsyncClient,
            create_dish_fixture
    ):
        """Тест получает детали блюда и ожидает корректные данные."""
        new_menu, new_submenu, new_dish = create_dish_fixture

        response = await client.get(
            router_dish.url_path_for(
                'get_dish',
                menu_id=str(new_menu.id),
                submenu_id=str(new_submenu.id),
                dish_id=str(new_dish.id)
            )
        )

        assert response.status_code == 200
        assert response.json()['id'] == str(new_dish.id)
        assert response.json()['title'] == new_dish.title
        assert response.json()['description'] == new_dish.description
        assert response.json()['price'] == new_dish.price

    @pytest.mark.usefixtures('create_dish_fixture')
    async def test_when_update_dish_then_details_updated(
            self,
            db_session: AsyncSession,
            client: AsyncClient,
            dish_repo: DishRepository,
            create_dish_fixture
    ):
        """Тест обновляет блюдо и проверяет, что детали изменены."""
        new_menu, new_submenu, new_dish = create_dish_fixture

        update_data = {
            'title': 'submenu 1 update',
            'description': 'description 1 update',
            'price': '20.24'
        }
        response = await client.patch(
            router_dish.url_path_for(
                'update_dish',
                menu_id=str(new_menu.id),
                submenu_id=str(new_submenu.id),
                dish_id=str(new_dish.id)
            ),
            json=update_data
        )
        await db_session.refresh(new_dish)

        dish = await dish_repo.get_dish_by_id(new_dish.id)

        assert dish is not None
        assert response.status_code == 200
        assert response.json()['id'] == str(dish.id)
        assert response.json()['title'] == dish.title
        assert response.json()['description'] == dish.description
        assert response.json()['price'] == dish.price

    @pytest.mark.usefixtures('create_dish_fixture')
    async def test_when_delete_dish_then_it_is_removed(
            self,
            client: AsyncClient,
            dish_repo: DishRepository,
            create_dish_fixture
    ):
        """Тест удаляет блюдо и проверяет, что оно удалено."""
        new_menu, new_submenu, new_dish = create_dish_fixture

        response = await client.delete(
            router_dish.url_path_for(
                'delete_dish',
                menu_id=str(new_menu.id),
                submenu_id=str(new_submenu.id),
                dish_id=str(new_dish.id)
            )
        )
        assert response.json()['detail'] == 'dish deleted'

        dish_deleted = await dish_repo.get_dish_by_id(new_dish.id)
        assert dish_deleted is None
