import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.menu_repository import MenuRepository
from app.routers.router_menu import router as router_menu
from tests.conftest import client, db_session

from app.models import Menu


class TestMenuAPI:
    @pytest.fixture(scope="function")
    async def create_menu_fixture(self, client: AsyncClient, menu_repo: MenuRepository) -> Menu:
        new_menu = await menu_repo.create_menu({"title": 'menu 1', "description": 'description 1', "id": uuid.uuid4()})
        yield new_menu

    async def test_menu_create(self, client: AsyncClient, menu_repo: MenuRepository):
        data = {'title': 'menu 1', 'description': 'description 1'}
        response = await client.post(router_menu.url_path_for('create_menu'), json=data)

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
    async def test_get_menu(self, client: AsyncClient, create_menu_fixture):
        new_menu = create_menu_fixture

        response = await client.get(router_menu.url_path_for('get_menu', menu_id=str(new_menu.id)))

        assert response.status_code == 200
        assert response.json()['id'] == str(new_menu.id)
        assert response.json()['title'] == new_menu.title
        assert response.json()['description'] == new_menu.description
        assert response.json()['submenus_count'] == 0
        assert response.json()['dishes_count'] == 0

    @pytest.mark.usefixtures('create_menu_fixture')
    async def test_menu_update(self, db_session: AsyncSession, client: AsyncClient, menu_repo: MenuRepository, create_menu_fixture):
        new_menu = create_menu_fixture

        update_data = {'title': 'menu 1 update', 'description': 'description 1 update'}
        response = await client.patch(router_menu.url_path_for('update_menu', menu_id=str(new_menu.id)),
                                      json=update_data)
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
    async def test_menu_delete(self, client: AsyncClient, menu_repo: MenuRepository, create_menu_fixture):
        new_menu = create_menu_fixture

        response = await client.delete(router_menu.url_path_for('delete_menu', menu_id=str(new_menu.id)))
        assert response.json()['detail'] == 'menu deleted'

        menu_deleted = await menu_repo.get_menu_by_id(new_menu.id)
        assert menu_deleted is None
