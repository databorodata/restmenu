import uuid

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session

from sqlalchemy import func, select
from app.models import Menu, Submenu, Dish

router = APIRouter(prefix="/api/v1/complex", tags=["complex"])


@router.get("/")
async def get_menu_details(menu_id: uuid.UUID,
                   session: AsyncSession = Depends(get_async_session)):
    submenus_count_subq = (
        select(func.count(Submenu.id))
        .where(Submenu.menu_id == Menu.id)
        .scalar_subquery()
    )

    dishes_count_subq = (
        select(func.count(Dish.id))
        .join(Submenu, Submenu.id == Dish.submenu_id)
        .where(Submenu.menu_id == Menu.id)
        .scalar_subquery()
    )

    query = (
        select(
            Menu.id,
            Menu.title,
            Menu.description,
            submenus_count_subq.label("submenus_count"),
            dishes_count_subq.label("dishes_count")
        )
        .where(Menu.id == menu_id)
    )

    result = await session.execute(query)
    menu_details = result.first()

    if menu_details:
        return {
            "id": menu_details.id,
            "title": menu_details.title,
            "description": menu_details.description,
            "submenus_count": menu_details.submenus_count,
            "dishes_count": menu_details.dishes_count
        }
    else:
        raise HTTPException(status_code=404, detail="Menu not found")