from uuid import UUID
import json

from fastapi import HTTPException

from app.repositories.dish_repository import DishRepository
from app.repositories.cache_repository import CacheRepository


class DishService:
    def __init__(self, dish_repository: DishRepository, cache_repository: CacheRepository):
        self.dish_repository = dish_repository
        self.cache_repository = cache_repository

    def _validate_price(self, price: str) -> str:
        try:
            price_float = float(price)
        except ValueError:
            raise HTTPException(status_code=400, detail='price type is not correct')
        return f'{price_float:.2f}'

    async def get_dishes(self, menu_id: UUID, submenu_id: UUID):
        cache_key = f'menu:{menu_id}/submenu:{submenu_id}/dishes:all'
        cached_dishes = await self.cache_repository.get(cache_key)
        if cached_dishes:
            return json.loads(cached_dishes)

        dishes_data = await self.dish_repository.get_all_dishes_for_submenu(submenu_id)
        dishes_list = [
            {
                'id': str(dish.id),
                'title': dish.title,
                'description': dish.description,
                'price': dish.price
            }
            for dish in dishes_data
        ]
        await self.cache_repository.set(cache_key, json.dumps(dishes_list), expire=60)
        return dishes_list

    async def get_dish(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID):
        cache_key = f'menu:{menu_id}/submenu:{submenu_id}/dish:{dish_id}'
        cached_dish = await self.cache_repository.get(cache_key)
        if cached_dish:
            return json.loads(cached_dish)

        dish_data = await self.dish_repository.get_dish_by_id(dish_id)
        if dish_data is None:
            raise HTTPException(status_code=404, detail="dish not found")

        dish = {
            'id': str(dish_data.id),
            'title': dish_data.title,
            'description': dish_data.description,
            'price': dish_data.price
        }
        await self.cache_repository.set(cache_key, json.dumps(dish), expire=60)
        return dish

    async def create_dish(self, menu_id: UUID, submenu_id: UUID, dish_data):
        dish_data['price'] = self._validate_price(dish_data['price'])
        new_dish = await self.dish_repository.create_dish({**dish_data, 'menu_id': menu_id, 'submenu_id': submenu_id})
        dish_cache_data = {
            'id': str(new_dish.id),
            'title': new_dish.title,
            'description': new_dish.description,
            'price': new_dish.price
        }
        await self.cache_repository.set(f'menu:{menu_id}/submenu:{submenu_id}/dish:{str(new_dish.id)}', json.dumps(dish_cache_data), expire=60)

        await self.cache_repository.delete(f'menu:{menu_id}/submenu:{submenu_id}/dishes:all')
        await self.cache_repository.delete(f'menu:{menu_id}/submenu:{submenu_id}')
        await self.cache_repository.delete(f'menu:{menu_id}/submenus:all')
        await self.cache_repository.delete(f'menu:{menu_id}')
        await self.cache_repository.delete('menus:all')

        return new_dish

    async def update_dish(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish_data):
        dish_data['price'] = self._validate_price(dish_data['price'])
        updated_dish = await self.dish_repository.update_dish(dish_id, dish_data)
        if updated_dish is None:
            raise HTTPException(status_code=404, detail="dish not found")
        new_dish_data = {
            'id': str(updated_dish.id),
            'title': updated_dish.title,
            'description': updated_dish.description,
            'price': updated_dish.price
        }
        await self.cache_repository.set(f'menu:{menu_id}/submenu:{submenu_id}/dish:{dish_id}', json.dumps(new_dish_data), expire=60)
        await self.cache_repository.delete(f'menu:{menu_id}/submenu:{submenu_id}/dishes:all')

        return new_dish_data

    async def delete_dish(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID):
        await self.dish_repository.delete_dish(dish_id)
        await self.cache_repository.delete(f'menu:{menu_id}/submenu:{submenu_id}/dish:{dish_id}')
        await self.cache_repository.delete(f'menu:{menu_id}/submenu:{submenu_id}/dishes:all')
        await self.cache_repository.delete(f'menu:{menu_id}/submenu:{submenu_id}')
        await self.cache_repository.delete(f'menu:{menu_id}/submenus:all')
        await self.cache_repository.delete(f'menu:{menu_id}')
        await self.cache_repository.delete('menus:all')

        return {'detail': 'dish deleted'}
