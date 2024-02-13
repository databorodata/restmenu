from app.schemas import CreateEditDishModel, CreateEditMenuModel, CreateEditSubmenuModel


class AddDiscountDishModel(CreateEditDishModel):
    discount: str = '0.0'


class BatchCreateSubmenuModel(CreateEditSubmenuModel):
    dishes: list[AddDiscountDishModel]


class BatchCreateMenuModel(CreateEditMenuModel):
    submenus: list[BatchCreateSubmenuModel]
