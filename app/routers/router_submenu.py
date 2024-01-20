import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.schemas import SubmenuModel
from app.models import Submenu

router = APIRouter(
    prefix="/api/v1/menus/{{api_test_menu_id}}/submenus",
    tags=["submenu"]
)

'''
Задача:
Посмотреть список подменю
путь:
{{LOCAL_URL}}/api/v1/menus/{{api_test_menu_id}}/submenus
пример ответа:
[
    {
        "id": "bc19488a-cc0e-4eaa-8d21-4d486a45392f",
        "title": "My submenu 1",
        "description": "My submenu description 1",
        "dishes_count": 0
    }
]
'''
@router.get("/")
async def get_submenus(menu_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    query = select(Submenu).filter_by(menu_id=menu_id)
    result = await session.execute(query)
    submenus = result.scalars().all()
    return submenus

'''
Задача:
Посмотреть определенное подменю
путь:
{{LOCAL_URL}}/api/v1/menus/{{api_test_menu_id}}/submenus/{{api_test_submenu_id}}
пример ответа:
{
    "id": "bc19488a-cc0e-4eaa-8d21-4d486a45392f",
    "title": "My submenu 1",
    "description": "My submenu description 1",
    "dishes_count": 0
}
или
{
    "detail": "submenu not found"
}
'''
@router.get("/{submenu_id}")
async def get_submenu(menu_id: uuid.UUID, submenu_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    query = select(Submenu).filter_by(id=submenu_id, menu_id=menu_id)
    result = await session.execute(query)
    submenu = result.scalars().first()
    if submenu is None:
        raise HTTPException(status_code=404, detail="Submenu not found")
    return submenu

'''
Задача:
Создать подменю
путь:
{{LOCAL_URL}}/api/v1/menus/{{api_test_menu_id}}/submenus
пример ответа:
{
    "id": "bc19488a-cc0e-4eaa-8d21-4d486a45392f",
    "title": "My submenu 1",
    "description": "My submenu description 1",
    "dishes_count": 0
}
'''

@router.post("/")
async def create_submenu(menu_id: uuid.UUID, submenu: SubmenuModel, session: AsyncSession = Depends(get_async_session)):
    new_submenu = Submenu(**submenu.model_dump(), menu_id=menu_id)
    session.add(new_submenu)
    await session.commit()
    return new_submenu

'''
Задача:
Обновить подменю
путь:
{{LOCAL_URL}}/api/v1/menus/{{api_test_menu_id}}/submenus/{{api_test_submenu_id}}
пример ответа:
{
    "id": "bc19488a-cc0e-4eaa-8d21-4d486a45392f",
    "title": "My updated submenu 1",
    "description": "My updated submenu description 1",
    "dishes_count": 0
}
или
{
    "detail": "submenu not found"
}
'''
@router.patch("/{submenu_id}")
async def update_submenu(menu_id: uuid.UUID, submenu_id: uuid.UUID, submenu: SubmenuModel, session: AsyncSession = Depends(get_async_session)):
    query = update(Submenu).filter_by(id=submenu_id, menu_id=menu_id).values(**submenu.model_dump())
    result = await session.execute(query)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Submenu not found")
    await session.commit()
    return {"detail": "Submenu updated"}

'''
Задача:
Удалить подменю
путь:
{{LOCAL_URL}}/api/v1/menus/{{api_test_menu_id}}/submenus/{{api_test_submenu_id}}
пример ответа:
{
    "status": true,
    "message": "The submenu has been deleted"
}
'''

@router.delete("/{submenu_id}")
async def delete_submenu(menu_id: uuid.UUID, submenu_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    query = delete(Submenu).filter_by(id=submenu_id, menu_id=menu_id)
    result = await session.execute(query)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Submenu not found")
    await session.commit()
    return {"detail": "Submenu deleted"}