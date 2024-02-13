from typing import Any

from background.batch_models import (
    AddDiscountDishModel,
    BatchCreateMenuModel,
    BatchCreateSubmenuModel,
)


def get_int(cell):
    try:
        int(cell)
        return True
    except ValueError:
        return False


def parse_sheet(data: list[Any]) -> list[BatchCreateMenuModel]:
    """Парсинг данных из google sheets"""
    current_col = 0
    current_row = 0
    result = []
    while current_row < len(data) and get_int(data[current_row][current_col]):
        menu_title = data[current_row][current_col + 1]
        menu_description = data[current_row][current_col + 2]
        current_col += 1
        current_row += 1

        submenus = []
        while current_row < len(data) and get_int(data[current_row][current_col]):
            submenu_title = data[current_row][current_col + 1]
            submenu_description = data[current_row][current_col + 2]

            current_col += 1
            current_row += 1
            dishes = []
            while current_row < len(data) and get_int(data[current_row][current_col]):
                price = data[current_row][current_col + 3].replace(',', '.')
                discount = data[current_row][current_col + 4]
                if discount:
                    discount = discount.replace(',', '.')
                dish_data = AddDiscountDishModel(
                    title=data[current_row][current_col + 1],
                    description=data[current_row][current_col + 2],
                    price=price,
                    discount=discount,
                )
                dishes.append(dish_data)
                current_row += 1

            current_col -= 1

            submenus.append(
                BatchCreateSubmenuModel(
                    title=submenu_title,
                    description=submenu_description,
                    dishes=dishes,
                )
            )

        current_col -= 1

        result.append(
            BatchCreateMenuModel(
                title=menu_title,
                description=menu_description,
                submenus=submenus,
            )
        )

    return result
