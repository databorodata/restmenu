from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from app.models import Submenu


class SubmenuRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_submenus_for_menu(self, menu_id):
        async with self.session() as session:
            result = await session.execute(select(Submenu).where(Submenu.menu_id == menu_id))
            return result.scalars().all()

    async def get_submenu_by_id(self, submenu_id):
        async with self.session() as session:
            result = await session.execute(select(Submenu).where(Submenu.id == submenu_id))
            return result.scalars().first()

    async def create_submenu(self, submenu_data):
        new_submenu = Submenu(**submenu_data)
        self.session.add(new_submenu)
        await self.session.commit()
        return new_submenu

    async def update_submenu(self, submenu_id, submenu_data):
        async with self.session() as session:
            await session.execute(update(Submenu).where(Submenu.id == submenu_id).values(**submenu_data))
            await session.commit()

    async def delete_submenu(self, submenu_id):
        async with self.session() as session:
            await session.execute(delete(Submenu).where(Submenu.id == submenu_id))
            await session.commit()
