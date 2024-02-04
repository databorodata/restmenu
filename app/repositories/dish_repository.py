from typing import Sequence
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import Row, delete, update
from sqlalchemy.future import select

from app.database import get_async_session
from app.models import Dish


class DishRepository:
    def __init__(self, session=Depends(get_async_session)) -> None:
        """Инициализация репозитория блюда с сессией базы данных."""
        self.session = session

    async def get_all_dishes_for_submenu(self, submenu_id: UUID) -> Sequence[Row]:
        """Возвращает список всех блюд."""
        query = (select(Dish).filter(Dish.submenu_id == submenu_id))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_dish_by_id(self, dish_id: UUID) -> Row:
        """Возвращает блюдо по его ID."""
        query = (select(Dish).filter(Dish.id == dish_id))
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def create_dish(self, dish_data: dict) -> Dish:
        """Создает и возвращает новое блюдо."""
        new_dish = Dish(**dish_data)
        self.session.add(new_dish)
        await self.session.commit()
        return new_dish

    async def update_dish(self, dish_id: UUID, dish_data: dict) -> Row:
        """Обновляет и возвращает обновленное блюдо."""
        await self.session.execute(
            update(Dish)
            .where(Dish.id == dish_id)
            .values(**dish_data)
        )
        await self.session.commit()
        return await self.get_dish_by_id(dish_id)

    async def delete_dish(self, dish_id: UUID) -> None:
        """Удаляет блюдо по его ID."""
        result = await self.session.execute(delete(Dish).where(Dish.id == dish_id))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail='dish not found')
        await self.session.commit()
