import uuid
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Menu
from app.repositories.menu_repository import MenuRepository
from tests.utils import reverse


class TestMenuAPI:
    @pytest.fixture(scope='function')
    async def create_menu_fixture(
            self,
            client: AsyncClient,
            menu_repo: MenuRepository
    ) -> AsyncGenerator[Menu, None]:
        """Фикстура для создания меню для тестирования."""
        new_menu = await menu_repo.create_menu({
            'title': 'menu 1',
            'description': 'description 1',
            'id': uuid.uuid4()
        })
        yield new_menu

    async def test_when_create_menu_then_success(
            self,
            client: AsyncClient,
            menu_repo: MenuRepository
    ) -> None:
        """Тест создает меню и ожидает успех."""
        data = {'title': 'menu 1', 'description': 'description 1'}
        response = await client.post(reverse('create_menu'), json=data)

        menu_id = response.json()['id']
        menu = await menu_repo.get_menu_by_id(menu_id)

        assert menu is not None
        assert response.status_code == 201
        assert response.json()['id'] == str(menu.Menu.id)
        assert response.json()['title'] == menu.Menu.title
        assert response.json()['description'] == menu.Menu.description
        assert response.json()['submenus_count'] == menu.submenus_count
        assert response.json()['dishes_count'] == menu.dishes_count

    @pytest.mark.usefixtures('create_menu_fixture')
    async def test_when_get_menu_then_details_correct(
            self,
            client: AsyncClient,
            create_menu_fixture: Menu
    ) -> None:
        """Тест получает детали меню и ожидает корректные данные."""
        new_menu = create_menu_fixture

        response = await client.get(reverse('get_menu', menu_id=str(new_menu.id)))

        assert response.status_code == 200
        assert response.json()['id'] == str(new_menu.id)
        assert response.json()['title'] == new_menu.title
        assert response.json()['description'] == new_menu.description
        assert response.json()['submenus_count'] == 0
        assert response.json()['dishes_count'] == 0

    @pytest.mark.usefixtures('create_menu_fixture')
    async def test_when_update_menu_then_details_updated(
            self,
            db_session: AsyncSession,
            client: AsyncClient,
            menu_repo: MenuRepository,
            create_menu_fixture: Menu,
    ) -> None:
        """Тест обновляет меню и проверяет, что детали изменены."""
        new_menu = create_menu_fixture

        update_data = {'title': 'menu 1 update', 'description': 'description 1 update'}
        response = await client.patch(
            reverse(
                'update_menu',
                menu_id=str(new_menu.id)
            ),
            json=update_data
        )
        await db_session.refresh(new_menu)

        menu = await menu_repo.get_menu_by_id(new_menu.id)

        assert menu is not None
        assert response.status_code == 200
        assert response.json()['id'] == str(menu.Menu.id)
        assert response.json()['title'] == menu.Menu.title
        assert response.json()['description'] == menu.Menu.description
        assert response.json()['submenus_count'] == menu.submenus_count
        assert response.json()['dishes_count'] == menu.dishes_count

    @pytest.mark.usefixtures('create_menu_fixture')
    async def test_when_delete_menu_then_it_is_removed(
            self,
            client: AsyncClient,
            menu_repo: MenuRepository,
            create_menu_fixture: Menu,
    ) -> None:
        """Тест удаляет меню и проверяет, что оно удалено."""
        new_menu = create_menu_fixture

        response = await client.delete(
            reverse(
                'delete_menu',
                menu_id=str(new_menu.id)
            )
        )
        assert response.json()['detail'] == 'menu deleted'

        menu_deleted = await menu_repo.get_menu_by_id(new_menu.id)
        assert menu_deleted is None
