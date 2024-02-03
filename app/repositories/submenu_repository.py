from fastapi import Depends
from sqlalchemy.future import select
from sqlalchemy import update, delete, func
from app.database import get_async_session
from app.models import Submenu, Dish


class SubmenuRepository:
    def __init__(self, session=Depends(get_async_session)):
        self.session = session

    def _dishes_count_subquery(self):
        return (
            select(func.count(Dish.id))
            .where(Dish.submenu_id == Submenu.id)
            .correlate(Submenu)
            .scalar_subquery()
            .label('dishes_count')
        )

    async def get_all_submenus_for_menu(self, menu_id):
        query = select(Submenu).add_columns(
            self._dishes_count_subquery()
        ).where(Submenu.menu_id == menu_id)
        result = await self.session.execute(query)
        return result.all()

    async def get_submenu_by_id(self, submenu_id):
        query = select(Submenu).add_columns(
            self._dishes_count_subquery()
        ).where(Submenu.id == submenu_id)
        result = await self.session.execute(query)
        return result.first()

    async def create_submenu(self, submenu_data):
        new_submenu = Submenu(**submenu_data)
        self.session.add(new_submenu)
        await self.session.commit()
        return new_submenu

    async def update_submenu(self, submenu_id, submenu_data):
        await self.session.execute(update(Submenu)
                                   .where(Submenu.id == submenu_id)
                                   .values(**submenu_data))
        await self.session.commit()
        return await self.get_submenu_by_id(submenu_id)

    async def delete_submenu(self, submenu_id):
        await self.session.execute(delete(Submenu).where(Submenu.id == submenu_id))
        await self.session.commit()





