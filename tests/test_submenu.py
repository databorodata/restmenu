import uuid
from typing import Tuple

import pytest

from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Menu, Submenu
from app.repositories.submenu_repository import SubmenuRepository
from app.repositories.menu_repository import MenuRepository
from app.routers.router_menu import router as router_menu
from app.routers.router_submenu import router as router_submenu

from tests.conftest import client, db_session


class TestSubmenuAPI:

    @pytest.fixture(scope="function")
    async def create_submenu_fixture(
            self,
            client: AsyncClient,
            menu_repo: MenuRepository,
            submenu_repo: SubmenuRepository
    ) -> Tuple[Menu, Submenu]:
        """Фикстура для создания подменю для тестирования."""

        new_menu = await menu_repo.create_menu({
            "title": 'menu 1',
            "description": 'description 1',
            "id": uuid.uuid4()
        })

        new_submenu = await (submenu_repo.create_submenu({
            'title': 'Test Submenu',
            'description': 'Test Submenu Description',
            'menu_id': new_menu.id,
             "id": uuid.uuid4()
        }))

        yield new_menu, new_submenu

    async def test_when_create_submenu_then_success(
            self,
            client: AsyncClient,
            menu_repo: MenuRepository,
            submenu_repo: SubmenuRepository
    ):
        """Тест создает подменю и ожидает успех."""

        data_menu = {'title': 'menu 1', 'description': 'description 1'}
        response_menu = await client.post(router_menu.url_path_for('create_menu'), json=data_menu)
        menu_id = response_menu.json()['id']

        data_submenu = {'title': 'Test Submenu', 'description': 'Test Submenu Description'}
        response_submenu = await client.post(
            router_submenu.url_path_for(
                'create_submenu',
                menu_id=menu_id
            ),
            json=data_submenu)
        submenu_id = response_submenu.json()['id']

        submenu = await submenu_repo.get_submenu_by_id(submenu_id)

        assert submenu is not None
        assert response_submenu.status_code == 201
        assert response_submenu.json()['id'] == str(submenu.Submenu.id)
        assert response_submenu.json()['title'] == submenu.Submenu.title
        assert response_submenu.json()['description'] == submenu.Submenu.description
        assert response_submenu.json()['dishes_count'] == 0

    @pytest.mark.usefixtures('create_submenu_fixture')
    async def test_when_get_submenu_then_details_correct(
            self,
            client: AsyncClient,
            create_submenu_fixture
    ):
        """Тест получает детали подменю и ожидает корректные данные."""

        new_menu, new_submenu = create_submenu_fixture

        response = await client.get(
            router_submenu.url_path_for(
                'get_submenu',
                menu_id=str(new_menu.id),
                submenu_id=str(new_submenu.id)
            )
        )

        assert response.status_code == 200
        assert response.json()['id'] == str(new_submenu.id)
        assert response.json()['title'] == new_submenu.title
        assert response.json()['description'] == new_submenu.description
        assert response.json()['dishes_count'] == 0

    @pytest.mark.usefixtures('create_submenu_fixture')
    async def test_when_update_submenu_then_details_updated(
            self,
            db_session: AsyncSession,
            client: AsyncClient,
            submenu_repo: SubmenuRepository,
            create_submenu_fixture
    ):
        """Тест обновляет подменю и проверяет, что детали изменены."""
        new_menu, new_submenu = create_submenu_fixture

        update_data = {'title': 'submenu 1 update', 'description': 'description 1 update'}
        response = await client.patch(
            router_submenu.url_path_for(
                'update_submenu',
                menu_id=str(new_menu.id),
                submenu_id=str(new_submenu.id)
            ),
            json=update_data
        )
        await db_session.refresh(new_submenu)

        submenu = await submenu_repo.get_submenu_by_id(new_submenu.id)

        assert submenu is not None
        assert response.status_code == 200
        assert response.json()['id'] == str(submenu.Submenu.id)
        assert response.json()['title'] == submenu.Submenu.title
        assert response.json()['description'] == submenu.Submenu.description
        assert response.json()['dishes_count'] == 0

    @pytest.mark.usefixtures('create_submenu_fixture')
    async def test_when_delete_submenu_then_it_is_removed(
            self,
            client: AsyncClient,
            submenu_repo: SubmenuRepository,
            create_submenu_fixture
    ):
        """Тест удаляет подменю и проверяет, что оно удалено."""
        new_menu, new_submenu = create_submenu_fixture

        response = await client.delete(
            router_submenu.url_path_for(
                'delete_submenu',
                menu_id=str(new_menu.id),
                submenu_id=str(new_submenu.id)
            )
        )
        assert response.json()['detail'] == 'submenu deleted'

        submenu_deleted = await submenu_repo.get_submenu_by_id(new_submenu.id)
        assert submenu_deleted is None
