import uuid

# import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Dish, Menu, Submenu
from tests.conftest import client


class TestDishAPI:

    async def test_dish_create(self, db_session: AsyncSession, client: AsyncClient):
        new_menu = Menu(title='menu 1', description='description 1', id=uuid.uuid4())
        new_submenu = Submenu(title='submenu 1', description='description 1', id=uuid.uuid4(), menu_id=new_menu.id)
        db_session.add(new_menu)
        db_session.add(new_submenu)
        await db_session.commit()

        data_dish = {"title": "Test Dish", "description": "Test Dish Description", "price": "42.42"}
        response_dish = await (client.
                               post(f"/api/v1/menus/{new_menu.id}/submenus/{new_submenu.id}/dishes/", json=data_dish))

        query = (select(Dish).filter(Dish.id == response_dish.json()['id']))
        result = await db_session.execute(query)
        dish = result.scalars().one_or_none()

        assert dish is not None
        assert response_dish.status_code == 201
        assert response_dish.json()["id"] == str(dish.id)
        assert response_dish.json()["title"] == dish.title
        assert response_dish.json()["description"] == dish.description
        assert response_dish.json()['price'] == "42.42"

    async def test_get_dish(self, db_session: AsyncSession, client: AsyncClient):
        new_menu = Menu(title='menu 1', description='description 1', id=uuid.uuid4())
        new_submenu = Submenu(title='submenu 1', description='description 1', id=uuid.uuid4(), menu_id=new_menu.id)
        new_dish = Dish(title='dish 1', description='description 1', price='42.42',
                        id=uuid.uuid4(), menu_id=new_menu.id, submenu_id=new_submenu.id)
        db_session.add(new_menu)
        db_session.add(new_submenu)
        db_session.add(new_dish)
        await db_session.commit()

        response = await client.get(f"/api/v1/menus/{str(new_menu.id)}/submenus/{str(new_submenu.id)}/dishes/{str(new_dish.id)}")
        assert response.status_code == 200
        assert response.json()["id"] == str(new_dish.id)
        assert response.json()["title"] == new_dish.title
        assert response.json()["description"] == new_dish.description
        assert response.json()['price'] == new_dish.price

    async def test_dish_update(self, db_session: AsyncSession, client: AsyncClient):
        new_menu = Menu(title='menu 1', description='description 1', id=uuid.uuid4())
        new_submenu = Submenu(title='submenu 1', description='description 1', id=uuid.uuid4(), menu_id=new_menu.id)
        new_dish = Dish(title='dish 1', description='description 1', price='42.42',
                        id=uuid.uuid4(), menu_id=new_menu.id, submenu_id=new_submenu.id)
        db_session.add(new_menu)
        db_session.add(new_submenu)
        db_session.add(new_dish)
        await db_session.commit()

        update_data = {"title": "submenu 1 update", "description": "description 1 update", 'price': "20.24"}
        response = await client.patch(f"/api/v1/menus/{str(new_menu.id)}/submenus/{str(new_submenu.id)}/dishes/{str(new_dish.id)}", json=update_data)
        await db_session.refresh(new_dish)

        query = (select(Dish).filter(Dish.id == response.json()['id']))
        result = await db_session.execute(query)
        dish = result.scalars().one_or_none()

        assert dish is not None
        assert response.status_code == 200
        assert response.json()["id"] == str(dish.id)
        assert response.json()["title"] == dish.title
        assert response.json()["description"] == dish.description
        assert response.json()['price'] == dish.price

    async def test_dish_delete(self, db_session: AsyncSession, client: AsyncClient):
        new_menu = Menu(title='menu 1', description='description 1', id=uuid.uuid4())
        new_submenu = Submenu(title='submenu 1', description='description 1', id=uuid.uuid4(), menu_id=new_menu.id)
        new_dish = Dish(title='dish 1', description='description 1', price='42.42',
                        id=uuid.uuid4(), menu_id=new_menu.id, submenu_id=new_submenu.id)
        db_session.add(new_menu)
        db_session.add(new_submenu)
        db_session.add(new_dish)
        await db_session.commit()

        response = await client.delete(f"/api/v1/menus/{str(new_menu.id)}/submenus/{str(new_submenu.id)}/dishes/{str(new_dish.id)}")

        assert response.json()['detail'] == 'dish deleted'

        query = (select(Dish).filter(Dish.id == new_dish.id))
        result = await db_session.execute(query)
        dish_deleted = result.scalars().one_or_none()

        assert dish_deleted is None
