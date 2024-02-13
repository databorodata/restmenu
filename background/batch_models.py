import uuid

from app.schemas import CreateEditDishModel, CreateEditMenuModel, CreateEditSubmenuModel


class AddDiscountDishModel(CreateEditDishModel):
    id: uuid.UUID
    discount: str = '0.0'


class BatchCreateSubmenuModel(CreateEditSubmenuModel):
    id: uuid.UUID
    dishes: list[AddDiscountDishModel]


class BatchCreateMenuModel(CreateEditMenuModel):
    id: uuid.UUID
    submenus: list[BatchCreateSubmenuModel]
