import json
from typing import Any, TypedDict
from uuid import UUID

from fastapi import HTTPException

from app.repositories.cache_repository import CacheRepository
from app.repositories.menu_repository import MenuRepository


class MenuDict(TypedDict):
    id: str
    title: str
    description: str
    submenus_count: int
    dishes_count: int


class MenuService:
    def __init__(
            self,
            menu_repository: MenuRepository,
            cache_repository: CacheRepository
    ) -> None:
        """Инициализация сервиса для работы с меню."""
        self.menu_repository = menu_repository
        self.cache_repository = cache_repository

    async def get_menus(self) -> list[MenuDict]:
        """Возвращает список всех меню с кэшированием."""
        cache_key = 'menus:all'
        cached_menus = await self.cache_repository.get(cache_key)

        if cached_menus:
            return json.loads(cached_menus)

        menus_data = await self.menu_repository.get_all_menus()
        menus_list: list[MenuDict] = [
            {
                'id': str(menu.Menu.id),
                'title': menu.Menu.title,
                'description': menu.Menu.description,
                'submenus_count': menu.submenus_count,
                'dishes_count': menu.dishes_count
            }
            for menu in menus_data
        ]

        await self.cache_repository.set(cache_key, json.dumps(menus_list), expire=60)
        return menus_list

    async def get_menu(self, menu_id: UUID) -> MenuDict:
        """Возвращает детали меню по ID с кэшированием."""
        cache_key = f'menu:{menu_id}'
        cached_menu = await self.cache_repository.get(cache_key)

        if cached_menu:
            return json.loads(cached_menu)

        menu_data = await self.menu_repository.get_menu_by_id(menu_id)
        if menu_data is None:
            raise HTTPException(status_code=404, detail='menu not found')

        menu: MenuDict = {
            'id': str(menu_data.Menu.id),
            'title': menu_data.Menu.title,
            'description': menu_data.Menu.description,
            'submenus_count': menu_data.submenus_count,
            'dishes_count': menu_data.dishes_count
        }
        await self.cache_repository.set(cache_key, json.dumps(menu), expire=60)
        return menu

    async def create_menu(self, menu_data: dict[str, Any]) -> MenuDict:
        """Создает новое меню и обновляет кэш."""
        new_menu = await self.menu_repository.create_menu(menu_data)
        menu_cache_data: MenuDict = {
            'id': str(new_menu.id),
            'title': new_menu.title,
            'description': new_menu.description,
            'submenus_count': 0,
            'dishes_count': 0
        }
        await self.cache_repository.set(f'menu:{str(new_menu.id)}', json.dumps(menu_cache_data), expire=60)
        await self.cache_repository.delete('menus:all')
        return menu_cache_data

    async def update_menu(self, menu_id: UUID, menu_data: dict[str, Any]) -> MenuDict:
        """Обновляет существующее меню и кэш."""
        updated_menu = await self.menu_repository.update_menu(menu_id, menu_data)
        if updated_menu is None:
            raise HTTPException(status_code=404, detail='menu not found')

        new_menu_data: MenuDict = {
            'id': str(updated_menu.Menu.id),
            'title': updated_menu.Menu.title,
            'description': updated_menu.Menu.description,
            'submenus_count': updated_menu.submenus_count,
            'dishes_count': updated_menu.dishes_count
        }
        await self.cache_repository.set(f'menu:{menu_id}', json.dumps(new_menu_data), expire=60)
        await self.cache_repository.delete('menus:all')

        return new_menu_data

    async def delete_menu(self, menu_id: UUID) -> None:
        """Удаляет меню и связанный с ним кэш."""
        await self.menu_repository.delete_menu(menu_id)
        await self.cache_repository.delete_pattern(f'menu:{menu_id}*')
        await self.cache_repository.delete('menus:all')
