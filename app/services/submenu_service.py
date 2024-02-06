import json
from typing import Any, TypedDict
from uuid import UUID

from fastapi import HTTPException

from app.repositories.cache_repository import CacheRepository
from app.repositories.submenu_repository import SubmenuRepository


class SubmenuDict(TypedDict):
    id: str
    title: str
    description: str
    dishes_count: int


class SubmenuService:
    def __init__(
            self,
            submenu_repository: SubmenuRepository,
            cache_repository: CacheRepository
    ) -> None:
        """Инициализация сервиса для работы с подменю."""
        self.submenu_repository = submenu_repository
        self.cache_repository = cache_repository

    async def get_submenus(self, menu_id: UUID) -> list[SubmenuDict]:
        """Возвращает список всех подменю с кэшированием."""
        cache_key = f'menu:{menu_id}/submenus:all'
        cached_submenus = await self.cache_repository.get(cache_key)
        if cached_submenus:
            return json.loads(cached_submenus)

        submenus_data = await self.submenu_repository.get_all_submenus_for_menu(menu_id)
        submenus_list: list[SubmenuDict] = [
            {
                'id': str(submenu.Submenu.id),
                'title': submenu.Submenu.title,
                'description': submenu.Submenu.description,
                'dishes_count': submenu.dishes_count
            }
            for submenu in submenus_data
        ]
        await self.cache_repository.set(cache_key, json.dumps(submenus_list), expire=60)
        return submenus_list

    async def get_submenu(self, menu_id: UUID, submenu_id: UUID) -> SubmenuDict:
        """Возвращает детали подменю по ID с кэшированием."""
        cache_key = f'menu:{menu_id}/submenu:{submenu_id}'
        cached_submenu = await self.cache_repository.get(cache_key)

        if cached_submenu:
            return json.loads(cached_submenu)

        submenu_data = await self.submenu_repository.get_submenu_by_id(submenu_id)
        if submenu_data is None:
            raise HTTPException(status_code=404, detail='submenu not found')

        submenu: SubmenuDict = {
            'id': str(submenu_data.Submenu.id),
            'title': submenu_data.Submenu.title,
            'description': submenu_data.Submenu.description,
            'dishes_count': submenu_data.dishes_count
        }
        await self.cache_repository.set(cache_key, json.dumps(submenu), expire=60)
        return submenu

    async def create_submenu(self, menu_id: UUID, submenu_data: dict[str, Any]) -> SubmenuDict:
        """Создает новое подменю и обновляет кэш."""
        new_submenu = await self.submenu_repository.create_submenu({**submenu_data, 'menu_id': menu_id})
        submenu_cache_data: SubmenuDict = {
            'id': str(new_submenu.id),
            'title': new_submenu.title,
            'description': new_submenu.description,
            'dishes_count': 0
        }
        await self.cache_repository.set(
            f'menu:{menu_id}/submenu:{str(new_submenu.id)}',
            json.dumps(submenu_cache_data),
            expire=60)
        await self.cache_repository.delete(f'menu:{menu_id}/submenus:all')
        await self.cache_repository.delete(f'menu:{menu_id}')
        await self.cache_repository.delete('menus:all')
        return submenu_cache_data

    async def update_submenu(self, menu_id: UUID, submenu_id: UUID, submenu_data: dict[str, Any]) -> SubmenuDict:
        """Обновляет существующее подменю и кэш."""
        updated_submenu = await self.submenu_repository.update_submenu(submenu_id, submenu_data)
        if updated_submenu is None:
            raise HTTPException(status_code=404, detail='submenu not found')

        new_submenu_data: SubmenuDict = {
            'id': str(updated_submenu.Submenu.id),
            'title': updated_submenu.Submenu.title,
            'description': updated_submenu.Submenu.description,
            'dishes_count': updated_submenu.dishes_count
        }
        await self.cache_repository.set(f'menu:{menu_id}/submenu:{submenu_id}',
                                        json.dumps(new_submenu_data),
                                        expire=60)
        await self.cache_repository.delete(f'menu:{menu_id}/submenus:all')

        return new_submenu_data

    async def delete_submenu(self, menu_id: UUID, submenu_id: UUID) -> None:
        """Удаляет подменю и связанный с ним кэш."""
        await self.submenu_repository.delete_submenu(submenu_id)
        await self.cache_repository.delete_pattern(f'menu:{menu_id}/submenu:{submenu_id}*')
        await self.cache_repository.delete(f'menu:{menu_id}/submenus:all')
        await self.cache_repository.delete(f'menu:{menu_id}')
        await self.cache_repository.delete('menus:all')
