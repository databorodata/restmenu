from uuid import UUID

from app.repositories.dish_repository import DishRepository
from app.repositories.cache_repository import CacheRepository

class DishService:
    def __init__(self, dish_repository: DishRepository, cache_repository: CacheRepository):
        self.dish_repository = dish_repository
        self.cache_repository = cache_repository

    async def get_dishes(self, menu_id: UUID, submenu_id: UUID):
        cache_key = f'menu:{menu_id}/submenu:{submenu_id}/dishes:all'
        cached_dishes = await self.cache_repository.get(cache_key)
        if cached_dishes:
            return cached_dishes

        dishes = await self.dish_repository.get_all_dishes_for_submenu(submenu_id)
        await self.cache_repository.set(cache_key, dishes, expire=60)
        return dishes

    async def create_dish(self, menu_id: UUID, submenu_id: UUID, dish_data):
        new_dish = await self.dish_repository.create_dish(dish_data)
        await self.cache_repository.delete(f'menu:{menu_id}/submenu:{submenu_id}/dishes:all')
        return new_dish

    async def update_dish(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish_data):
        await self.dish_repository.update_dish(dish_id, dish_data)
        await self.cache_repository.delete(f'menu:{menu_id}/submenu:{submenu_id}/dishes:all')

    async def delete_dish(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID):
        await self.dish_repository.delete_dish(dish_id)
        await self.cache_repository.delete(f'menu:{menu_id}/submenu:{submenu_id}/dishes:all')
