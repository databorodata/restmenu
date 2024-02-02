from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from app.models import Dish


class DishRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_dishes_for_submenu(self, submenu_id):
        async with self.session() as session:
            result = await session.execute(select(Dish).where(Dish.submenu_id == submenu_id))
            return result.scalars().all()

    async def get_dish_by_id(self, dish_id):
        async with self.session() as session:
            result = await session.execute(select(Dish).where(Dish.id == dish_id))
            return result.scalars().first()

    async def create_dish(self, dish_data):
        new_dish = Dish(**dish_data)
        self.session.add(new_dish)
        await self.session.commit()
        return new_dish

    async def update_dish(self, dish_id, dish_data):
        async with self.session() as session:
            await session.execute(update(Dish).where(Dish.id == dish_id).values(**dish_data))
            await session.commit()

    async def delete_dish(self, dish_id):
        async with self.session() as session:
            await session.execute(delete(Dish).where(Dish.id == dish_id))
            await session.commit()
