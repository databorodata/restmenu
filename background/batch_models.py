from app.schemas import CreateEditDishModel, CreateEditMenuModel, CreateEditSubmenuModel


class BatchCreateSubmenuModel(CreateEditSubmenuModel):
    dishes: list[CreateEditDishModel]


class BatchCreateMenuModel(CreateEditMenuModel):
    submenus: list[BatchCreateSubmenuModel]
