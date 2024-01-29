import uuid

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.schemas import MenuModel, CreateEditMenuModel
from app.models import Menu

from sqlalchemy import func, select
from app.models import Menu, Submenu, Dish

router = APIRouter(prefix="/api/v1/menus", tags=["menu"])


def convert_menu(menu):
    menu_dict = MenuModel.model_validate(menu, from_attributes=True).model_dump()
    menu_dict.update({"submenus_count": len(menu.submenus), "dishes_count": len(menu.dishes)})
    return menu_dict


async def get_menu_from_db(session, menu_id: uuid.UUID):
    query = (
        select(Menu)
        .options(joinedload(Menu.submenus), joinedload(Menu.dishes))
        .filter(Menu.id == menu_id)
    )
    print(query)
    result = await session.execute(query)
    menu = result.scalars().unique().one_or_none()

    if menu is None:
        raise HTTPException(status_code=404, detail="menu not found")
    return menu


@router.get("/")
async def get_menus(session: AsyncSession = Depends(get_async_session)):
    query = (select(Menu)
             .options(selectinload(Menu.submenus),
                      selectinload(Menu.dishes)))
    result = await session.execute(query)
    menus = result.scalars().all()
    return [convert_menu(menu) for menu in menus]


@router.get("/{menu_id}")
async def get_menu(menu_id: uuid.UUID,
                   session: AsyncSession = Depends(get_async_session)):
    menu = await get_menu_from_db(session, menu_id)
    return convert_menu(menu)


@router.post("/", status_code=201)
async def create_menu(menu_data: CreateEditMenuModel,
                      session: AsyncSession = Depends(get_async_session)):
    new_menu = Menu(**menu_data.model_dump(), id=uuid.uuid4())
    session.add(new_menu)
    await session.commit()
    result = MenuModel.model_validate(new_menu, from_attributes=True).model_dump()
    result.update({"submenus_count": 0, "dishes_count": 0})
    return result


@router.patch("/{menu_id}")
async def update_menu(menu_id: uuid.UUID,
                      menu_data: CreateEditMenuModel,
                      session: AsyncSession = Depends(get_async_session)):
    query = (update(Menu)
             .where(Menu.id == menu_id)
             .values(**menu_data.model_dump()))
    await session.execute(query)
    await session.commit()

    menu = await get_menu_from_db(session, menu_id)
    return convert_menu(menu)


@router.delete("/{menu_id}")
async def delete_menu(menu_id: uuid.UUID,
                      session: AsyncSession = Depends(get_async_session)):
    query = (delete(Menu)
             .where(Menu.id == menu_id))
    result = await session.execute(query)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="menu not found")
    await session.commit()
    return {"detail": "menu deleted"}


