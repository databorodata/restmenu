from sqlalchemy.orm import joinedload
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.models import Menu
# from app.schemas import MenuSchema  # Define this Pydantic schema
#
# router = APIRouter()
#
# @router.get("/menus")
# async def get_menus(session: AsyncSession = Depends(get_async_session)):
#     async with session() as s:
#         result = await s.query(Menu).options(joinedload(Menu.submenus).joinedload(Submenu.dishes)).all()
#         return MenuSchema.from_orm(result).dict()  # Serialize result using Pydantic



# from pydantic import BaseModel
# from typing import List, Optional
# import uuid
#
# # Определение модели блюда
# class DishModel(BaseModel):
#     id: uuid.UUID
#     title: str
#     description: str
#     price: float
#     discount: Optional[float] = 0.0  # Скидка, по умолчанию 0
#
# # Определение модели подменю с вложенными блюдами
# class SubmenuModel(BaseModel):
#     id: uuid.UUID
#     title: str
#     description: str
#     dishes: List[DishModel]  # Список блюд, связанных с подменю
#
# # Определение модели меню с вложенными подменю
# class MenuModel(BaseModel):
#     id: uuid.UUID
#     title: str
#     description: str
#     submenus: List[SubmenuModel]