import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.schemas import SubmenuModel, CreateEditSubmenuModel
from app.models import Submenu

router = APIRouter(prefix="/api/v1/menus/{menu_id}/submenus", tags=["submenu"])


def convert_submenu(submenu):
    submenu_dict = SubmenuModel.model_validate(submenu, from_attributes=True).model_dump()
    submenu_dict.update({"dishes_count": len(submenu.dishes)})
    return submenu_dict


async def get_submenu_from_db(session, menu_id: uuid.UUID, submenu_id: uuid.UUID):
    query = (select(Submenu)
             .options(selectinload(Submenu.dishes))
             .filter(Submenu.id == submenu_id, Submenu.menu_id == menu_id))
    result = await session.execute(query)
    submenu = result.scalars().one_or_none()
    if submenu is None:
        raise HTTPException(status_code=404, detail="submenu not found")
    return submenu



@router.get("/")
async def get_submenus(menu_id: uuid.UUID,
                       session: AsyncSession = Depends(get_async_session)):
    query = (select(Submenu)
             .options(selectinload(Submenu.dishes))
             .filter(Submenu.menu_id == menu_id))
    result = await session.execute(query)
    submenus = result.scalars().all()
    return [convert_submenu(submenu) for submenu in submenus]


@router.get("/{submenu_id}")
async def get_submenu(menu_id: uuid.UUID,
                      submenu_id: uuid.UUID,
                      session: AsyncSession = Depends(get_async_session)):
    submenu = await get_submenu_from_db(session, menu_id, submenu_id)
    return convert_submenu(submenu)



@router.post("/", status_code=201)
async def create_submenu(menu_id: uuid.UUID,
                         submenu_data: CreateEditSubmenuModel,
                         session: AsyncSession = Depends(get_async_session)):
    new_submenu = Submenu(**submenu_data.model_dump(), menu_id=menu_id, id=uuid.uuid4())
    session.add(new_submenu)
    await session.commit()
    result = SubmenuModel.model_validate(new_submenu, from_attributes=True).model_dump()
    result.update({"dishes_count": 0})
    return result



@router.patch("/{submenu_id}")
async def update_submenu(menu_id: uuid.UUID,
                         submenu_id: uuid.UUID,
                         submenu_data: CreateEditSubmenuModel,
                         session: AsyncSession = Depends(get_async_session)):
    query = (update(Submenu)
             .where(Submenu.id == submenu_id,
                    Submenu.menu_id == menu_id)
             .values(**submenu_data.model_dump())
             .returning(Submenu))
    result = await session.execute(query)
    submenu = result.scalars().one_or_none()
    if submenu is None:
        raise HTTPException(status_code=404, detail="submenu not found")
    await session.commit()
    submenu = await get_submenu_from_db(session, menu_id, submenu_id)
    return convert_submenu(submenu)



@router.delete("/{submenu_id}")
async def delete_submenu(menu_id: uuid.UUID,
                         submenu_id: uuid.UUID,
                         session: AsyncSession = Depends(get_async_session)):
    query = (delete(Submenu)
             .where(Submenu.id == submenu_id,
                    Submenu.menu_id == menu_id))
    result = await session.execute(query)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="submenu not found")
    await session.commit()
    return {"detail": "submenu deleted"}
