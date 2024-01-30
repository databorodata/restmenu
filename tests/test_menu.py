import uuid

# import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Menu
# from app.schemas import MenuModel
from tests.conftest import client, db_session


class TestMenuAPI:

    async def test_menu_create(self, db_session: AsyncSession, client: AsyncClient):
        data = {"title": "Test Menu", "description": "Test Description"}
        response = await client.post("/api/v1/menus/", json=data)

        query = (select(Menu).filter(Menu.id == response.json()['id']))
        result = await db_session.execute(query)
        menu = result.scalars().one_or_none()

        assert menu is not None
        assert response.status_code == 201
        assert response.json()["id"] == str(menu.id)
        assert response.json()["title"] == menu.title
        assert response.json()["description"] == menu.description
        assert response.json()['submenus_count'] == 0
        assert response.json()['dishes_count'] == 0



    async def test_get_menu(self, db_session: AsyncSession, client: AsyncClient):
        new_menu = Menu(title='menu 1', description='description 1', id=uuid.uuid4())
        db_session.add(new_menu)
        await db_session.commit()

        response = await client.get(f"/api/v1/menus/{new_menu.id}")
        assert response.status_code == 200
        assert response.json()["id"] == str(new_menu.id)
        assert response.json()["title"] == new_menu.title
        assert response.json()["description"] == new_menu.description
        assert response.json()['submenus_count'] == 0
        assert response.json()['dishes_count'] == 0

    async def test_menu_update(self, db_session: AsyncSession, client: AsyncClient):
        new_menu = Menu(title='menu 1', description='description 1', id=uuid.uuid4())
        db_session.add(new_menu)
        await db_session.commit()

        update_data = {"title": "menu 1 update", "description": "description 1 update"}
        response = await client.patch(f"/api/v1/menus/{new_menu.id}", json=update_data)
        await db_session.refresh(new_menu)

        query = (select(Menu).filter(Menu.id == new_menu.id))
        result = await db_session.execute(query)
        menu = result.scalars().one_or_none()

        assert menu is not None
        assert response.status_code == 200
        assert response.json()["id"] == str(menu.id)
        assert response.json()["title"] == menu.title
        assert response.json()["description"] == menu.description
        assert response.json()['submenus_count'] == 0
        assert response.json()['dishes_count'] == 0

    async def test_menu_delete(self, db_session: AsyncSession, client: AsyncClient):
        new_menu = Menu(title='menu 1', description='description 1', id=uuid.uuid4())
        db_session.add(new_menu)
        await db_session.commit()

        response = await client.delete(f"/api/v1/menus/{new_menu.id}")
        assert response.json()['detail'] == 'menu deleted'

        query = (select(Menu).filter(Menu.id == new_menu.id))
        result = await db_session.execute(query)
        menu_deleted = result.scalars().one_or_none()

        assert menu_deleted is None
