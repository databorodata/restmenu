import json
from typing import Any, TypedDict
from uuid import UUID

from fastapi import BackgroundTasks, HTTPException

from app.repositories.cache_repository import CacheRepository
from app.repositories.dish_repository import DishRepository


class DishDict(TypedDict):
    id: str
    title: str
    description: str
    price: str


async def invalidate_dish(
        cache: CacheRepository,
        menu_id: str,
        submenu_id: str,
        dish_id: str,
) -> None:
    await cache.delete(f'menu:{menu_id}/submenu:{submenu_id}/dish:{dish_id}')


async def invalidate_dish_all(
        cache: CacheRepository,
        menu_id: str,
        submenu_id: str,
) -> None:
    await cache.delete(f'menu:{menu_id}/submenu:{submenu_id}/dishes:all')


async def invalidate_dishes_submenu_submenus_menu_menus(
        cache: CacheRepository,
        menu_id: str,
        submenu_id: str
) -> None:
    await cache.delete(f'menu:{menu_id}/submenu:{submenu_id}/dishes:all')
    await cache.delete(f'menu:{menu_id}/submenu:{submenu_id}')
    await cache.delete(f'menu:{menu_id}/submenus:all')
    await cache.delete(f'menu:{menu_id}')
    await cache.delete('menus:all')


def validate_price(price: str) -> str:
    """Проверяет корректность полученной цены блюда и возвращает корректный результат."""
    try:
        price_float = float(price)
    except ValueError:
        raise HTTPException(status_code=400, detail='price type is not correct')
    return normalize_price(price_float)


def normalize_price(price: float) -> str:
    return f'{price:.2f}'


def try_parse_discount(discount: str | None) -> float:
    if not discount:
        return 0
    try:
        return float(discount)
    except ValueError:
        return 0


def calculate_price(price: str, discount: str | None) -> str:
    price_float = float(price)
    discount_float = try_parse_discount(discount)
    return normalize_price(
        max(0.0, (100.0 - discount_float) / 100.0 * price_float)
    )


class DishService:
    def __init__(
            self,
            dish_repository: DishRepository,
            cache_repository: CacheRepository
    ) -> None:
        """Инициализация сервиса для работы с блюдо."""
        self.dish_repository = dish_repository
        self.cache_repository = cache_repository

    async def get_dishes(
            self,
            menu_id: UUID,
            submenu_id: UUID
    ) -> list[DishDict]:
        """Возвращает список всех блюд с кэшированием."""
        cache_key = f'menu:{menu_id}/submenu:{submenu_id}/dishes:all'
        cached_dishes = await self.cache_repository.get(cache_key)

        if cached_dishes:
            return json.loads(cached_dishes)

        dishes_data = await self.dish_repository.get_all_dishes_for_submenu(submenu_id)
        dishes_list: list[DishDict] = []
        for dish in dishes_data:
            dish_discount = await self.cache_repository.get(f'{str(dish.id)}_discount')
            dishes_list.append(
                {
                    'id': str(dish.id),
                    'title': dish.title,
                    'description': dish.description,
                    'price': calculate_price(dish.price, dish_discount),
                }
            )
        await self.cache_repository.set(cache_key, json.dumps(dishes_list), expire=60)
        return dishes_list

    async def get_dish(
            self,
            menu_id: UUID,
            submenu_id: UUID,
            dish_id: UUID
    ) -> DishDict:
        """Возвращает детали блюда по ID с кэшированием."""
        cache_key = f'menu:{menu_id}/submenu:{submenu_id}/dish:{dish_id}'
        cached_dish = await self.cache_repository.get(cache_key)

        if cached_dish:
            return json.loads(cached_dish)

        dish_data = await self.dish_repository.get_dish_by_id(dish_id)
        if dish_data is None:
            raise HTTPException(status_code=404, detail='dish not found')

        dish_discount = await self.cache_repository.get(f'{str(dish_id)}_discount')
        dish: DishDict = {
            'id': str(dish_data.id),
            'title': dish_data.title,
            'description': dish_data.description,
            'price': calculate_price(dish_data.price, dish_discount),
        }
        await self.cache_repository.set(cache_key, json.dumps(dish), expire=60)
        return dish

    async def create_dish(
            self,
            menu_id: UUID,
            submenu_id: UUID,
            dish_data: dict[str, Any],
            background_tasks: BackgroundTasks,
    ) -> DishDict:
        """Создает новое блюдо и обновляет кэш."""
        dish_data['price'] = validate_price(dish_data['price'])
        new_dish = await self.dish_repository.create_dish({**dish_data, 'submenu_id': submenu_id})
        dish_cache_data = {
            'id': str(new_dish.id),
            'title': new_dish.title,
            'description': new_dish.description,
            'price': new_dish.price
        }
        await self.cache_repository.set(
            f'menu:{menu_id}/submenu:{submenu_id}/dish:{str(new_dish.id)}',
            json.dumps(dish_cache_data),
            expire=60)

        background_tasks.add_task(
            invalidate_dishes_submenu_submenus_menu_menus,
            self.cache_repository,
            str(menu_id),
            str(submenu_id)
        )

        return new_dish

    async def update_dish(
            self,
            menu_id: UUID,
            submenu_id: UUID,
            dish_id: UUID,
            dish_data: dict[str, Any],
            background_tasks: BackgroundTasks,
    ) -> DishDict:
        """Обновляет существующее блюдо и кэш."""
        dish_data['price'] = validate_price(dish_data['price'])
        updated_dish = await self.dish_repository.update_dish(dish_id, dish_data)
        if updated_dish is None:
            raise HTTPException(status_code=404, detail='dish not found')

        dish_discount = await self.cache_repository.get(f'{str(dish_id)}_discount')
        new_dish_data: DishDict = {
            'id': str(updated_dish.id),
            'title': updated_dish.title,
            'description': updated_dish.description,
            'price': calculate_price(updated_dish.price, dish_discount)
        }
        await self.cache_repository.set(
            f'menu:{menu_id}/submenu:{submenu_id}/dish:{dish_id}',
            json.dumps(new_dish_data),
            expire=60)

        background_tasks.add_task(
            invalidate_dish_all,
            self.cache_repository,
            str(menu_id),
            str(submenu_id)
        )

        return new_dish_data

    async def delete_dish(
            self,
            menu_id: UUID,
            submenu_id: UUID,
            dish_id: UUID,
            background_tasks: BackgroundTasks,
    ) -> None:
        """Удаляет блюдо и связанный с ним кэш."""
        await self.dish_repository.delete_dish(dish_id)
        background_tasks.add_task(
            invalidate_dish,
            self.cache_repository,
            str(menu_id),
            str(submenu_id),
            str(dish_id)
        )
        background_tasks.add_task(
            invalidate_dishes_submenu_submenus_menu_menus,
            self.cache_repository,
            str(menu_id),
            str(submenu_id)
        )
