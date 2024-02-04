from typing import Any, Sequence
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import Row, delete, func, update
from sqlalchemy.future import select

from app.database import get_async_session
from app.models import Dish, Submenu


class SubmenuRepository:
    def __init__(self, session=Depends(get_async_session)) -> None:
        """Инициализация репозитория подменю с сессией базы данных."""
        self.session = session

    def _dishes_count_subquery(self) -> Any:
        """Возвращает подзапрос для подсчета блюд."""
        return (
            select(func.count(Dish.id))
            .where(Dish.submenu_id == Submenu.id)
            .correlate(Submenu)
            .scalar_subquery()
            .label('dishes_count')
        )

    async def get_all_submenus_for_menu(self, menu_id: UUID) -> Sequence[Row]:
        """Возвращает список всех подменю."""
        query = select(Submenu).add_columns(
            self._dishes_count_subquery()
        ).where(Submenu.menu_id == menu_id)
        result = await self.session.execute(query)
        return result.all()

    async def get_submenu_by_id(self, submenu_id: UUID) -> Row:
        """Возвращает подменю по его ID."""
        query = select(Submenu).add_columns(
            self._dishes_count_subquery()
        ).where(Submenu.id == submenu_id)
        result = await self.session.execute(query)
        return result.first()

    async def create_submenu(self, submenu_data: dict) -> Submenu:
        """Создает и возвращает новое подменю."""
        new_submenu = Submenu(**submenu_data)
        self.session.add(new_submenu)
        await self.session.commit()
        return new_submenu

    async def update_submenu(self, submenu_id: UUID, submenu_data: dict) -> Row:
        """Обновляет и возвращает обновленное подменю."""
        await self.session.execute(
            update(Submenu)
            .where(Submenu.id == submenu_id)
            .values(**submenu_data)
        )
        await self.session.commit()
        return await self.get_submenu_by_id(submenu_id)

    async def delete_submenu(self, submenu_id: UUID) -> None:
        """Удаляет подменю по его ID."""
        result = await self.session.execute(delete(Submenu).where(Submenu.id == submenu_id))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail='submenu not found')
        await self.session.commit()
