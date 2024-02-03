
from fastapi import Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy import update, delete, func

from app.database import get_async_session
from app.models import Menu, Submenu, Dish


class MenuRepository:
    def __init__(self, session=Depends(get_async_session)):
        self.session = session

    def _submenus_count_subquery(self):
        return (
            select(func.count(Submenu.id))
            .where(Submenu.menu_id == Menu.id)
            .correlate(Menu)
            .scalar_subquery()
            .label('submenus_count')
        )

    def _dishes_count_subquery(self):
        return (
            select(func.count(Dish.id))
            .join(Submenu, Submenu.id == Dish.submenu_id)
            .where(Submenu.menu_id == Menu.id)
            .correlate(Menu)
            .scalar_subquery()
            .label('dishes_count')
        )

    async def get_all_menus(self):
        query = select(Menu).add_columns(
            self._submenus_count_subquery(),
            self._dishes_count_subquery()
        )
        result = await self.session.execute(query)
        return result.all()

    async def get_menu_by_id(self, menu_id):
        query = select(Menu).add_columns(
            self._submenus_count_subquery(),
            self._dishes_count_subquery()
        ).where(Menu.id == menu_id)
        result = await self.session.execute(query)
        return result.first()

    async def create_menu(self, menu_data):
        new_menu = Menu(**menu_data)
        self.session.add(new_menu)
        await self.session.commit()
        return new_menu

    async def update_menu(self, menu_id, menu_data):
        await self.session.execute(
            update(Menu)
            .where(Menu.id == menu_id)
            .values(**menu_data)
        )
        await self.session.commit()
        return  await self.get_menu_by_id(menu_id)

    async def delete_menu(self, menu_id):
        result = await self.session.execute(delete(Menu).where(Menu.id == menu_id))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail='Menu not found')
        await self.session.commit()
