from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from app.models import Menu


class MenuRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_menus(self):
        async with self.session() as session:
            result = await session.execute(select(Menu))
            return result.scalars().all()

    async def get_menu_by_id(self, menu_id):
        async with self.session() as session:
            result = await session.execute(select(Menu).where(Menu.id == menu_id))
            return result.scalars().first()

    async def create_menu(self, menu_data):
        new_menu = Menu(**menu_data)
        self.session.add(new_menu)
        await self.session.commit()
        return new_menu

    async def update_menu(self, menu_id, menu_data):
        async with self.session() as session:
            await session.execute(update(Menu).where(Menu.id == menu_id).values(**menu_data))
            await session.commit()

    async def delete_menu(self, menu_id):
        async with self.session() as session:
            await session.execute(delete(Menu).where(Menu.id == menu_id))
            await session.commit()
