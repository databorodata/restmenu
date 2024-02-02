from uuid import UUID

from app.repositories.submenu_repository import SubmenuRepository
from app.repositories.cache_repository import CacheRepository

class SubmenuService:
    def __init__(self, submenu_repository: SubmenuRepository, cache_repository: CacheRepository):
        self.submenu_repository = submenu_repository
        self.cache_repository = cache_repository

    async def get_submenus(self, menu_id: UUID):
        cache_key = f'menu:{menu_id}/submenus:all'
        cached_submenus = await self.cache_repository.get(cache_key)
        if cached_submenus:
            return cached_submenus

        submenus = await self.submenu_repository.get_all_submenus_for_menu(menu_id)
        await self.cache_repository.set(cache_key, submenus, expire=60)
        return submenus

    async def create_submenu(self, menu_id: UUID, submenu_data):
        new_submenu = await self.submenu_repository.create_submenu(submenu_data)
        await self.cache_repository.delete(f'menu:{menu_id}/submenus:all')
        return new_submenu

    async def update_submenu(self, menu_id: UUID, submenu_id: UUID, submenu_data):
        await self.submenu_repository.update_submenu(submenu_id, submenu_data)
        await self.cache_repository.delete(f'menu:{menu_id}/submenus:all')
        await self.cache_repository.delete(f'menu:{menu_id}')

    async def delete_submenu(self, menu_id: UUID, submenu_id: UUID):
        await self.submenu_repository.delete_submenu(submenu_id)
        await self.cache_repository.delete(f'menu:{menu_id}/submenus:all')
        await self.cache_repository.delete(f'menu:{menu_id}')
