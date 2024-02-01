import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models import Dish
from app.schemas import CreateEditDishModel, DishModel

router = APIRouter(prefix='/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', tags=['dish'])


def convert_dish(dish):
    return DishModel.model_validate(dish, from_attributes=True).model_dump()


async def get_dish_from_db(session,
                           menu_id: uuid.UUID,
                           submenu_id: uuid.UUID,
                           dish_id: uuid.UUID):
    query = (select(Dish)
             .filter(Dish.submenu_id == submenu_id,
                     Dish.menu_id == menu_id,
                     Dish.id == dish_id))
    result = await session.execute(query)
    dish = result.scalars().one_or_none()
    if dish is None:
        raise HTTPException(status_code=404, detail='dish not found')
    return dish


def validate_price(price: str) -> str:
    try:
        price_float = float(price)
    except ValueError:
        raise HTTPException(status_code=400, detail='price type is not correct')
    return f'{price_float:.2f}'


@router.get('/')
async def get_dishes(menu_id: uuid.UUID,
                     submenu_id: uuid.UUID,
                     session: AsyncSession = Depends(get_async_session)):
    query = (select(Dish)
             .filter(Dish.menu_id == menu_id,
                     Dish.submenu_id == submenu_id))
    result = await session.execute(query)
    dishes = result.scalars().all()
    return [convert_dish(dish) for dish in dishes]


@router.get('/{dish_id}')
async def get_dish(menu_id: uuid.UUID,
                   submenu_id: uuid.UUID,
                   dish_id: uuid.UUID,
                   session: AsyncSession = Depends(get_async_session)):
    dish = await get_dish_from_db(session, menu_id, submenu_id, dish_id)
    return convert_dish(dish)


@router.post('/', status_code=201)
async def create_dish(menu_id: uuid.UUID,
                      submenu_id: uuid.UUID,
                      dish_data: CreateEditDishModel,
                      session: AsyncSession = Depends(get_async_session)):
    dish_data.price = validate_price(dish_data.price)
    new_dish = Dish(**dish_data.model_dump(),
                    menu_id=menu_id,
                    submenu_id=submenu_id,
                    id=uuid.uuid4())
    session.add(new_dish)
    await session.commit()
    return convert_dish(new_dish)


@router.patch('/{dish_id}')
async def update_dish(menu_id: uuid.UUID,
                      submenu_id: uuid.UUID,
                      dish_id: uuid.UUID,
                      dish_data: CreateEditDishModel,
                      session: AsyncSession = Depends(get_async_session)):
    dish_data.price = validate_price(dish_data.price)
    query = (update(Dish)
             .where(Dish.id == dish_id,
                    Dish.submenu_id == submenu_id,
                    Dish.menu_id == menu_id)
             .values(**dish_data.model_dump()))
    await session.execute(query)
    await session.commit()

    dish = await get_dish_from_db(session, menu_id, submenu_id, dish_id)
    return convert_dish(dish)


@router.delete('/{dish_id}')
async def delete_dish(menu_id: uuid.UUID,
                      submenu_id: uuid.UUID,
                      dish_id: uuid.UUID,
                      session: AsyncSession = Depends(get_async_session)):
    query = delete(Dish).where(Dish.id == dish_id,
                               Dish.submenu_id == submenu_id,
                               Dish.menu_id == menu_id)
    result = await session.execute(query)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail='dish not found')
    await session.commit()
    return {'detail': 'dish deleted'}
