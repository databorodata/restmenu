import uuid
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field


class MenuModel(BaseModel):
    id: uuid.UUID = Field(default=uuid.uuid4, alias="id")
    title: str
    description: str
    submenus_count: float = 0.0
    dishes_count: int = 0


class SubmenuModel(BaseModel):
    id: uuid.UUID = Field(default=uuid.uuid4, alias="id")
    title: str
    description: str
    dishes_count: int = 0


class DishModel(BaseModel):
    id: uuid.UUID = Field(default=uuid.uuid4, alias="id")
    title: str
    description: str
    price: float = 0.0


#
# class Menu(Base):
#     __tablename__ = "menu"
#
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True, unique=True)
#     description = Column(String, index=True, unique=False)
#     submenus = relationship("Submenu", back_populates="menu")
#
# class Submenu(Base):
#     __tablename__ = "submenu"
#
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True, unique=True)
#     menu_id = Column(Integer, ForeignKey("menu.id"))
#
#     menu = relationship("Menu", back_populates="submenus")
#     dishes = relationship("Dish", back_populates="submenu")
#
# class CreateMenu(Base):
#     __tablename__ = "dish"
#
#     id = Column(uuid.uuid4(), primary_key=True, index=True)
#     title = Column(String, index=True, unique=False)
#     description = Column(String, index=True, unique=False)
#     submenus_count = Column(Float)
#     submenu_id = Column(Integer, ForeignKey("submenu.id"))
#
#     submenu = relationship("Submenu", back_populates="dishes")
#
# class Dish(Base):
#     __tablename__ = "dish"
#
#     id = Column(uuid.uuid4(), primary_key=True, index=True)
#     name = Column(String, index=True, unique=True)
#     price = Column(Float)
#     submenu_id = Column(Integer, ForeignKey("submenu.id"))
#
#     submenu = relationship("Submenu", back_populates="dishes")
#
# class MenuCreate(BaseModel):
#     name: str
#
# class SubmenuCreate(BaseModel):
#     name: str
#     menu_id: int
#
# class DishCreate(BaseModel):
#     name: str
#     price: float
#     submenu_id: int
