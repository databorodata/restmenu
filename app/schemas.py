import uuid
from pydantic import BaseModel


class CreateEditMenuModel(BaseModel):
    title: str
    description: str


class CreateEditSubmenuModel(BaseModel):
    title: str
    description: str


class CreateEditDishModel(BaseModel):
    title: str
    description: str
    price: str


class MenuModel(BaseModel):
    id: uuid.UUID
    title: str
    description: str


class SubmenuModel(BaseModel):
    id: uuid.UUID
    title: str
    description: str


class DishModel(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    price: str
