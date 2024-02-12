import uuid
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient

from app.models import Dish, Menu, Submenu
from app.repositories.dish_repository import DishRepository
from app.repositories.menu_repository import MenuRepository
from app.repositories.submenu_repository import SubmenuRepository
from tests.utils import reverse


class TestFullMenuAPI:

    @pytest.fixture(scope='function')
    async def create_menu_submenu_dish_fixture(
            self,
            client: AsyncClient,
            menu_repo: MenuRepository,
            submenu_repo: SubmenuRepository,
            dish_repo: DishRepository
    ) -> AsyncGenerator[tuple[Menu, Submenu, Dish, Dish, Submenu, Dish, Dish], None]:
        """Фикстура для создания меню с подменю и блюдами для тестирования."""

        new_menu1 = await menu_repo.create_menu({
            'title': 'алкоголь',
            'description': 'весь алкоголь',
            'id': uuid.uuid4()
        })

        new_submenu1_1 = await submenu_repo.create_submenu({
            'title': 'слабоалкогольные напитки',
            'description': 'пиво',
            'menu_id': new_menu1.id,
            'id': uuid.uuid4()
        })

        new_dish1_1_1 = await dish_repo.create_dish({
            'title': 'пиво',
            'description': 'пиво светлое',
            'price': '80.50',
            'menu_id': new_menu1.id,
            'submenu_id': new_submenu1_1.id,
            'id': uuid.uuid4()
        })

        new_dish1_1_2 = await dish_repo.create_dish({
            'title': 'пиво',
            'description': 'пиво тёмное',
            'price': '86.50',
            'menu_id': new_menu1.id,
            'submenu_id': new_submenu1_1.id,
            'id': uuid.uuid4()
        })

        new_submenu1_2 = await submenu_repo.create_submenu({
            'title': 'крепкие напитки',
            'description': 'виски отечественный и зарубежный',
            'menu_id': new_menu1.id,
            'id': uuid.uuid4()
        })

        new_dish1_2_1 = await dish_repo.create_dish({
            'title': 'виски отечественный',
            'description': 'не дорогой, крепкий, опасный',
            'price': '90.50',
            'menu_id': new_menu1.id,
            'submenu_id': new_submenu1_2.id,
            'id': uuid.uuid4()
        })

        new_dish1_2_2 = await dish_repo.create_dish({
            'title': 'виски Шотландский',
            'description': 'дорогой и крепкий',
            'price': '480.00',
            'menu_id': new_menu1.id,
            'submenu_id': new_submenu1_2.id,
            'id': uuid.uuid4()
        })

        yield new_menu1, new_submenu1_1, new_dish1_1_1, new_dish1_1_2, new_submenu1_2, new_dish1_2_1, new_dish1_2_2

    @pytest.mark.usefixtures('create_menu_submenu_dish_fixture')
    async def test_when_get_menus_then_menus_correct(
            self,
            client: AsyncClient,
            create_menu_submenu_dish_fixture: tuple[Menu, Submenu, Dish, Dish, Submenu, Dish, Dish],
    ) -> None:
        """Тест получает список меню с одним и связанными двумя подменю и связанными четырьмя блюдами."""
        """И ожидает конкретные данные"""

        (
            new_menu1,
            new_submenu1_1,
            new_dish1_1_1,
            new_dish1_1_2,
            new_submenu1_2,
            new_dish1_2_1,
            new_dish1_2_2
        ) = create_menu_submenu_dish_fixture

        response = await client.get(reverse('get_full_menus'))

        menus_list = response.json()
        menu_dict = menus_list[0]
        submenus_list = menu_dict['submenus']
        submenu_dict_1 = submenus_list[0]
        submenu_dict_2 = submenus_list[1]
        dishes_list_1 = submenu_dict_1['dishes']
        dish_dict_1_1 = dishes_list_1[0]
        dish_dict_1_2 = dishes_list_1[1]
        dishes_list_2 = submenu_dict_2['dishes']
        dish_dict_2_1 = dishes_list_2[0]
        dish_dict_2_2 = dishes_list_2[1]

        assert response.status_code == 200

        assert menu_dict['description'] == new_menu1.description
        assert len(menus_list) == 1

        assert submenu_dict_1['title'] == new_submenu1_1.title
        assert submenu_dict_2['id'] == str(new_submenu1_2.id)
        assert len(submenus_list) == 2

        assert dish_dict_1_1['title'] == new_dish1_1_1.title
        assert dish_dict_1_2['description'] == new_dish1_1_2.description
        assert dish_dict_2_1['price'] == new_dish1_2_1.price
        assert dish_dict_2_2['id'] == str(new_dish1_2_2.id)
        assert len(dishes_list_1) == 2
        assert len(dishes_list_2) == 2


"""
example = [
    {'title': 'алкоголь', 'description': 'весь алкоголь', 'id': '8a0c8658-a70b-4abc-8602-c54fa0ffcca1', 'submenus':
        [
            {'title': 'слабоалкогольные напитки', 'description': 'пиво', 'id': '6e7619a1-1ca2-4512-9a44-3a093a14c271',
             'dishes':
                 [
                     {'title': 'пиво', 'description': 'пиво светлое', 'price': '80.50',
                      'id': '7248fccb-f7e8-4ab2-936f-41f056e2a68b'},
                     {'title': 'пиво', 'description': 'пиво тёмное', 'price': '86.50',
                      'id': 'ef34d574-e6eb-43cb-bb06-fb99895ac757'}
                 ]
             },
            {'title': 'крепкие напитки', 'description': 'виски отечественный и зарубежный',
             'id': '1f103819-6e09-4532-ad19-4715c777fc3f', 'dishes':
                 [
                     {'title': 'виски отечественный', 'description': 'не дорогой, крепкий, опасный', 'price': '90.50',
                      'id': '4aff465b-b73a-4cb5-b932-56e8e78004ac'},
                     {'title': 'виски Шотландский', 'description': 'дорогой и крепкий', 'price': '480.00',
                      'id': '61f961f9-59ff-4122-ade0-05c741432417'}
                 ]
             }
        ]
     }
]
"""
