from uuid import UUID

from app.repositories.menu_repository import MenuRepository
from app.repositories.cache_repository import CacheRepository

class MenuService:
    def __init__(self, menu_repository: MenuRepository, cache_repository: CacheRepository):
        self.menu_repository = menu_repository
        self.cache_repository = cache_repository

    async def get_menus(self):
        cache_key = 'menus:all'
        cached_menus = await self.cache_repository.get(cache_key)
        if cached_menus:
            return cached_menus

        menus = await self.menu_repository.get_all_menus()
        await self.cache_repository.set(cache_key, menus, expire=60)
        return menus

    async def get_menu(self, menu_id: UUID):
        cache_key = f'menu:{menu_id}'
        cached_menu = await self.cache_repository.get(cache_key)
        if cached_menu:
            return cached_menu

        menu = await self.menu_repository.get_menu_by_id(menu_id)
        await self.cache_repository.set(cache_key, menu, expire=60)
        return menu

    async def create_menu(self, menu_data):
        new_menu = await self.menu_repository.create_menu(menu_data)
        await self.cache_repository.delete('menus:all')
        return new_menu

    async def update_menu(self, menu_id: UUID, menu_data):
        await self.menu_repository.update_menu(menu_id, menu_data)
        await self.cache_repository.delete(f'menu:{menu_id}')
        await self.cache_repository.delete('menus:all')

    async def delete_menu(self, menu_id: UUID):
        await self.menu_repository.delete_menu(menu_id)
        await self.cache_repository.delete(f'menu:{menu_id}')
        await self.cache_repository.delete('menus:all')
