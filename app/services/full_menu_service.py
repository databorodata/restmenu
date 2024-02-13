from typing import Sequence

from app.models import Dish, Menu, Submenu
from app.repositories.cache_repository import CacheRepository
from app.repositories.menu_repository import MenuRepository
from app.schemas import DishModel, FullMenuModel, FullSubmenuModel
from app.services.dish_service import calculate_price


async def convert_full_data(
        cache_repository: CacheRepository,
        raw_results: Sequence[tuple[Menu, Submenu, Dish]]
) -> list[FullMenuModel]:
    menus = {}
    submenus = {}

    for menu_data, submenu_data, dish_data in raw_results:
        if menu_data.id not in menus:
            menus[menu_data.id] = FullMenuModel(
                id=menu_data.id,
                title=menu_data.title,
                description=menu_data.description, submenus=[]
            )
        menu = menus[menu_data.id]

        if submenu_data and submenu_data.id not in submenus:
            submenus[submenu_data.id] = FullSubmenuModel(
                id=submenu_data.id,
                title=submenu_data.title,
                description=submenu_data.description,
                dishes=[]
            )
            menu.submenus.append(submenus[submenu_data.id])

        if submenu_data:
            submenu = submenus[submenu_data.id]

            if dish_data:
                dish_discount = await cache_repository.get(f'{str(dish_data.id)}_discount')
                dish_model = DishModel(
                    id=dish_data.id,
                    title=dish_data.title,
                    description=dish_data.description,
                    price=calculate_price(dish_data.price, dish_discount)
                )
                submenu.dishes.append(dish_model)

    return list(menus.values())


class FullMenuService:
    def __init__(self, menu_repository: MenuRepository, cache_repository: CacheRepository) -> None:
        """Инициализация сервиса для работы с меню."""
        self.menu_repository = menu_repository
        self.cache_repository = cache_repository

    async def get_full_menus(self) -> list[FullMenuModel]:
        results = await self.menu_repository.get_full_menus()
        return await convert_full_data(self.cache_repository, results)
