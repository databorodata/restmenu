from fastapi import Depends
from sqlalchemy.future import select
from sqlalchemy import update, delete

from app.database import get_async_session
from app.models import Dish


class DishRepository:
    def __init__(self, session=Depends(get_async_session)):
        self.session = session

    async def get_all_dishes_for_submenu(self, submenu_id):
        query = (select(Dish).filter(Dish.submenu_id == submenu_id))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_dish_by_id(self, dish_id):
        query = (select(Dish).filter(Dish.id == dish_id))
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def create_dish(self, dish_data):
        new_dish = Dish(**dish_data)
        self.session.add(new_dish)
        await self.session.commit()
        return new_dish

    async def update_dish(self, dish_id, dish_data):
        await self.session.execute(update(Dish)
                                   .where(Dish.id == dish_id)
                                   .values(**dish_data))
        await self.session.commit()
        return await self.get_dish_by_id(dish_id)

    async def delete_dish(self, dish_id):
        await self.session.execute(delete(Dish).where(Dish.id == dish_id))
        await self.session.commit()