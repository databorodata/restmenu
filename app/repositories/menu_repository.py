from typing import Any, Sequence
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import delete, func, update
from sqlalchemy.engine.row import Row
from sqlalchemy.future import select

from app.database import get_async_session
from app.models import Dish, Menu, Submenu


class MenuRepository:
    def __init__(self, session=Depends(get_async_session)) -> None:
        """Инициализация репозитория меню с сессией базы данных."""
        self.session = session

    def _submenus_count_subquery(self) -> Any:
        """Возвращает подзапрос для подсчета подменю."""
        return (
            select(func.count(Submenu.id))
            .where(Submenu.menu_id == Menu.id)
            .correlate(Menu)
            .scalar_subquery()
            .label('submenus_count')
        )

    def _dishes_count_subquery(self) -> Any:
        """Возвращает подзапрос для подсчета блюд."""
        return (
            select(func.count(Dish.id))
            .join(Submenu, Submenu.id == Dish.submenu_id)
            .where(Submenu.menu_id == Menu.id)
            .correlate(Menu)
            .scalar_subquery()
            .label('dishes_count')
        )

    async def get_all_menus(self) -> Sequence[Row]:
        """Возвращает список всех меню."""
        query = select(Menu).add_columns(
            self._submenus_count_subquery(),
            self._dishes_count_subquery()
        )
        result = await self.session.execute(query)
        return result.all()

    async def get_menu_by_id(self, menu_id: UUID) -> Row:
        """Возвращает меню по его ID."""
        query = select(Menu).add_columns(
            self._submenus_count_subquery(),
            self._dishes_count_subquery()
        ).where(Menu.id == menu_id)
        result = await self.session.execute(query)
        return result.first()

    async def create_menu(self, menu_data: dict[str, Any]) -> Menu:
        """Создает и возвращает новое меню."""
        new_menu = Menu(**menu_data)
        self.session.add(new_menu)
        await self.session.commit()
        return new_menu

    async def update_menu(self, menu_id: UUID, menu_data: dict[str, Any]) -> Row:
        """Обновляет и возвращает обновленное меню."""
        await self.session.execute(
            update(Menu)
            .where(Menu.id == menu_id)
            .values(**menu_data)
        )
        await self.session.commit()
        return await self.get_menu_by_id(menu_id)

    async def delete_menu(self, menu_id: UUID) -> None:
        """Удаляет меню по его ID."""
        result = await self.session.execute(delete(Menu).where(Menu.id == menu_id))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail='menu not found')
        await self.session.commit()
