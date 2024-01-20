import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.schemas import DishModel
from app.models import Dish

router = APIRouter(
    prefix="/api/v1/menus/{{api_test_menu_id}}/submenus/{{api_test_submenu_id}}/dishes",
    tags=["dish"]
)



'''
Задача:
Посмотреть список блюд
путь:
{{LOCAL_URL}}/api/v1/menus/{{api_test_menu_id}}/submenus/{{api_test_submenu_id}}/dishes
пример ответа:
[
    {
        "id": "602033b3-0462-4de1-a2f8-d8494795e0c0",
        "title": "My dish 1",
        "description": "My dish description 1",
        "price": "12.50"
    }
]
'''
@router.get("/")
async def get_dishes(menu_id: uuid.UUID, submenu_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    query = select(Dish).filter_by(submenu_id=submenu_id)
    result = await session.execute(query)
    dishes = result.scalars().all()
    return dishes

'''
Задача:
Посмотреть определенное блюдо
путь:
{{LOCAL_URL}}/api/v1/menus/{{api_test_menu_id}}/submenus/{{api_test_submenu_id}}/dishes/{{api_test_dish_id}}
пример ответа:
{
    "id": "602033b3-0462-4de1-a2f8-d8494795e0c0",
    "title": "My dish 1",
    "description": "My dish description 1",
    "price": "12.50"
}
или
{
    "detail": "dish not found"
}
'''
@router.get("/{dish_id}")
async def get_dish(menu_id: uuid.UUID, submenu_id: uuid.UUID, dish_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    query = select(Dish).filter_by(id=dish_id, submenu_id=submenu_id)
    result = await session.execute(query)
    dish = result.scalars().first()
    if dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish

'''
Задача:
Создать блюдо
путь:
{{LOCAL_URL}}/api/v1/menus/{{api_test_menu_id}}/submenus/{{api_test_submenu_id}}/dishes
пример ответа:
{
    "id": "602033b3-0462-4de1-a2f8-d8494795e0c0",
    "title": "My dish 1",
    "description": "My dish description 1",
    "price": "12.50"
}
'''

@router.post("/")
async def create_dish(menu_id: uuid.UUID, submenu_id: uuid.UUID, dish: DishModel, session: AsyncSession = Depends(get_async_session)):
    new_dish = Dish(**dish.model_dump(), submenu_id=submenu_id)
    session.add(new_dish)
    await session.commit()
    return new_dish

'''
Задача:
Обновить блюдо
путь:
{{LOCAL_URL}}/api/v1/menus/{{api_test_menu_id}}/submenus/{{api_test_submenu_id}}/dishes/{{api_test_dish_id}}
пример ответа:
{
    "id": "602033b3-0462-4de1-a2f8-d8494795e0c0",
    "title": "My updated dish 1",
    "description": "My updated dish description 1",
    "price": "14.50"
}
или
{
    "detail": "dish not found"
}
'''
@router.patch("/{dish_id}")
async def update_dish(menu_id: uuid.UUID, submenu_id: uuid.UUID, dish_id: uuid.UUID, dish: DishModel, session: AsyncSession = Depends(get_async_session)):
    query = update(Dish).filter_by(id=dish_id, submenu_id=submenu_id).values(**dish.model_dump())
    result = await session.execute(query)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Dish not found")
    await session.commit()
    return {"detail": "Dish updated"}

'''
Задача:
Удалить блюдо
путь:
{{LOCAL_URL}}/api/v1/menus/{{api_test_menu_id}}/submenus/{{api_test_submenu_id}}/dishes/{{api_test_dish_id}}
пример ответа:
{
    "status": true,
    "message": "The dish has been deleted"
}
'''

@router.delete("/{dish_id}")
async def delete_dish(menu_id: uuid.UUID, submenu_id: uuid.UUID, dish_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    query = delete(Dish).filter_by(id=dish_id, submenu_id=submenu_id)
    result = await session.execute(query)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Dish not found")
    await session.commit()
    return {"detail": "Dish deleted"}