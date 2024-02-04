import uuid

from pydantic import BaseModel


class CreateEditMenuModel(BaseModel):
    title: str
    description: str


class MenuModel(CreateEditMenuModel):
    id: uuid.UUID
    submenus_count: int
    dishes_count: int


class CreateEditSubmenuModel(BaseModel):
    title: str
    description: str


class SubmenuModel(CreateEditSubmenuModel):
    id: uuid.UUID
    dishes_count: int


class CreateEditDishModel(BaseModel):
    title: str
    description: str
    price: str


class DishModel(CreateEditDishModel):
    id: uuid.UUID
