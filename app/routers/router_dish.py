import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.schemas import DishModel
from app.models import Dish

router = APIRouter(prefix="/api/v1/menus/{api_test_menu_id}/submenus/{api_test_submenu_id}/dishes", tags=["dish"])

@router.get("/")
async def get_dishes(menu_id: uuid.UUID,
                     submenu_id: uuid.UUID,
                     session: AsyncSession = Depends(get_async_session)):
    query = (select(Dish)
             .filter(Dish.submenu_id == submenu_id))
    result = await session.execute(query)
    return result.scalars().all()

@router.get("/{api_test_dish_id}")
async def get_dish(menu_id: uuid.UUID,
                   submenu_id: uuid.UUID,
                   dish_id: uuid.UUID,
                   session: AsyncSession = Depends(get_async_session)):
    query = select(Dish).filter(Dish.id == dish_id,
                                Dish.submenu_id == submenu_id)
    result = await session.execute(query)
    dish = result.scalar_one_or_none()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish

@router.post("/")
async def create_dish(menu_id: uuid.UUID,
                      submenu_id: uuid.UUID,
                      dish_data: DishModel,
                      session: AsyncSession = Depends(get_async_session)):
    new_dish = Dish(**dish_data.model_dump(),
                    submenu_id=submenu_id)
    session.add(new_dish)
    await session.commit()
    return new_dish

@router.patch("/{api_test_dish_id}")
async def update_dish(menu_id: uuid.UUID,
                      submenu_id: uuid.UUID,
                      dish_id: uuid.UUID,
                      dish_data: DishModel,
                      session: AsyncSession = Depends(get_async_session)):
    query = (update(Dish)
             .where(Dish.id == dish_id,
                    Dish.submenu_id == submenu_id)
             .values(**dish_data.model_dump()))
    result = await session.execute(query)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Dish not found")
    await session.commit()
    return {"detail": "Dish updated"}

@router.delete("/{api_test_dish_id}")
async def delete_dish(menu_id: uuid.UUID,
                      submenu_id: uuid.UUID,
                      dish_id: uuid.UUID,
                      session: AsyncSession = Depends(get_async_session)):
    query = delete(Dish).where(Dish.id == dish_id,
                               Dish.submenu_id == submenu_id)
    result = await session.execute(query)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Dish not found")
    await session.commit()
    return {"detail": "Dish deleted"}

