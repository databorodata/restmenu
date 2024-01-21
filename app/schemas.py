import uuid
from pydantic import BaseModel, Field


class CreateEditMenuModel(BaseModel):
    title: str
    description: str


class CreateEditSubmenuModel(BaseModel):
    title: str
    description: str


class CreateEditDishModel(BaseModel):
    title: str
    description: str


class MenuModel(BaseModel):
    id: uuid.UUID  # = Field(default_factory=uuid.uuid4, alias="id")
    title: str
    description: str


class SubmenuModel(BaseModel):
    id: uuid.UUID # = Field(default_factory=uuid.uuid4, alias="id")
    title: str
    description: str
    #api_test_menu_id: uuid.UUID


class DishModel(BaseModel):
    id: uuid.UUID # = Field(default_factory=uuid.uuid4, alias="id")
    title: str
    description: str
    price: float
    # api_test_submenu_id: uuid.UUID


