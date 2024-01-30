import uuid

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Menu, Submenu
from tests.conftest import client


class TestSubmenuAPI:

    async def test_submenu_create(self, db_session: AsyncSession, client: AsyncClient):
        new_menu = Menu(title='menu 1', description='description 1', id=uuid.uuid4())
        db_session.add(new_menu)
        await db_session.commit()

        data_submenu = {"title": "Test Submenu", "description": "Test Submenu Description"}
        response_submenu = await client.post(f"/api/v1/menus/{new_menu.id}/submenus/", json=data_submenu)

        query = (select(Submenu).filter(Submenu.id == response_submenu.json()['id']))
        result = await db_session.execute(query)
        submenu = result.scalars().one_or_none()

        assert submenu is not None
        assert response_submenu.status_code == 201
        assert response_submenu.json()["id"] == str(submenu.id)
        assert response_submenu.json()["title"] == submenu.title
        assert response_submenu.json()["description"] == submenu.description
        assert response_submenu.json()['dishes_count'] == 0

    async def test_get_submenu(self, db_session: AsyncSession, client: AsyncClient):
        new_menu = Menu(title='menu 1', description='description 1', id=uuid.uuid4())
        new_submenu = Submenu(title='submenu 1', description='description 1', id=uuid.uuid4(), menu_id=new_menu.id)
        db_session.add(new_menu)
        db_session.add(new_submenu)
        await db_session.commit()

        response = await client.get(f"/api/v1/menus/{str(new_menu.id)}/submenus/{str(new_submenu.id)}")
        assert response.status_code == 200
        assert response.json()["id"] == str(new_submenu.id)
        assert response.json()["title"] == new_submenu.title
        assert response.json()["description"] == new_submenu.description
        assert response.json()['dishes_count'] == 0

    async def test_submenu_update(self, db_session: AsyncSession, client: AsyncClient):
        new_menu = Menu(title='menu 1', description='description 1', id=uuid.uuid4())
        new_submenu = Submenu(title='submenu 1', description='description 1', id=uuid.uuid4(), menu_id=new_menu.id)
        db_session.add(new_menu)
        db_session.add(new_submenu)
        await db_session.commit()

        update_data = {"title": "submenu 1 update", "description": "description 1 update"}
        response = await client.patch(f"/api/v1/menus/{str(new_menu.id)}/submenus/{str(new_submenu.id)}", json=update_data)
        await db_session.refresh(new_submenu)

        query = (select(Submenu).filter(Submenu.id == response.json()['id']))
        result = await db_session.execute(query)
        submenu = result.scalars().one_or_none()

        assert submenu is not None
        assert response.status_code == 200
        assert response.json()["id"] == str(submenu.id)
        assert response.json()["title"] == submenu.title
        assert response.json()["description"] == submenu.description
        assert response.json()['dishes_count'] == 0

    async def test_submenu_delete(self, db_session: AsyncSession, client: AsyncClient):
        new_menu = Menu(title='menu 1', description='description 1', id=uuid.uuid4())
        new_submenu = Submenu(title='submenu 1', description='description 1', id=uuid.uuid4(), menu_id=new_menu.id)
        db_session.add(new_menu)
        db_session.add(new_submenu)
        await db_session.commit()

        response = await client.delete(f"/api/v1/menus/{str(new_menu.id)}/submenus/{str(new_submenu.id)}")

        assert response.json()['detail'] == 'submenu deleted'

        query = (select(Submenu).filter(Submenu.id == new_submenu.id))
        result = await db_session.execute(query)
        submenu_deleted = result.scalars().one_or_none()

        assert submenu_deleted is None
