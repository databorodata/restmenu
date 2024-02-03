from fastapi import APIRouter, Depends
from uuid import UUID

from app.database import get_async_session
from app.repositories.cache_repository import CacheRepository
from app.repositories.dish_repository import DishRepository
from app.services.dish_service import DishService
from app.schemas import CreateEditDishModel

router = APIRouter(prefix='/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', tags=['dish'])

# Dependency
def get_dish_service():
    dish_repository = DishRepository(session=Depends(get_async_session))
    cache_repository = CacheRepository(redis_url="redis://localhost")
    return DishService(dish_repository=dish_repository, cache_repository=cache_repository)

@router.get('/')
async def get_dishes(menu_id: UUID, submenu_id: UUID, dish_service: DishService = Depends(get_dish_service)):
    return await dish_service.get_dishes(menu_id, submenu_id)

@router.get('/{dish_id}')
async def get_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish_service: DishService = Depends(get_dish_service)):
    return await dish_service.get_dish(menu_id, submenu_id, dish_id)

@router.post('/', status_code=201)
async def create_dish(menu_id: UUID, submenu_id: UUID, dish_data: CreateEditDishModel, dish_service: DishService = Depends(get_dish_service)):
    return await dish_service.create_dish(menu_id, submenu_id, dish_data.model_dump())

@router.patch('/{dish_id}')
async def update_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish_data: CreateEditDishModel, dish_service: DishService = Depends(get_dish_service)):
    await dish_service.update_dish(menu_id, submenu_id, dish_id, dish_data.model_dump())

@router.delete('/{dish_id}')
async def delete_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish_service: DishService = Depends(get_dish_service)):
    await dish_service.delete_dish(menu_id, submenu_id, dish_id)


# import uuid
# import json
# import logging
#
# import aioredis
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy import delete, select, update
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.database import get_async_session, get_redis_connection
# from app.models import Dish
# from app.schemas import CreateEditDishModel, DishModel
#
# router = APIRouter(prefix='/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', tags=['dish'])
#
# logger = logging.getLogger(__name__)
# logging.basicConfig(filename='redis_operations.log', level=logging.INFO, format='%(asctime)s - %(message)s')
#
#
# def convert_dish(dish):
#     dish_dict = DishModel.model_validate(dish, from_attributes=True).model_dump()
#     dish_dict['id'] = str(dish_dict['id'])
#     return dish_dict
#
#
# async def get_dish_from_db(session,
#                            menu_id: uuid.UUID,
#                            submenu_id: uuid.UUID,
#                            dish_id: uuid.UUID):
#     query = (select(Dish)
#              .filter(Dish.submenu_id == submenu_id,
#                      Dish.menu_id == menu_id,
#                      Dish.id == dish_id))
#     result = await session.execute(query)
#     dish = result.scalars().one_or_none()
#     if dish is None:
#         raise HTTPException(status_code=404, detail='dish not found')
#     return dish
#
#
# def validate_price(price: str) -> str:
#     try:
#         price_float = float(price)
#     except ValueError:
#         raise HTTPException(status_code=400, detail='price type is not correct')
#     return f'{price_float:.2f}'
#
#
# @router.get('/')
# async def get_dishes(menu_id: uuid.UUID,
#                      submenu_id: uuid.UUID,
#                      session: AsyncSession = Depends(get_async_session)):
#     redis = await get_redis_connection()
#     cache_key = f'menu:{menu_id}/submenu:{submenu_id}/dishes:all'
#     cached_dishes = await redis.get(cache_key)
#
#     if cached_dishes:
#         logger.info('Fetching all dishes from cache')
#         return json.loads(cached_dishes)
#
#     logger.info('Fetching all dishes from database')
#
#     query = (select(Dish)
#              .filter(Dish.menu_id == menu_id,
#                      Dish.submenu_id == submenu_id))
#     result = await session.execute(query)
#     dishes = result.scalars().all()
#     return [convert_dish(dish) for dish in dishes]
#
#
# @router.get('/{dish_id}')
# async def get_dish(menu_id: uuid.UUID,
#                    submenu_id: uuid.UUID,
#                    dish_id: uuid.UUID,
#                    session: AsyncSession = Depends(get_async_session)):
#     redis = await get_redis_connection()
#     cache_key = f'menu:{menu_id}/submenu/{submenu_id}/dish/{dish_id}'
#     cached_dish = await redis.get(cache_key)
#
#     if cached_dish:
#         logger.info(f'Fetching dish {dish_id} from cache')
#         return json.loads(cached_dish)
#
#     logger.info(f'Fetching dish {dish_id} from database')
#
#     dish = await get_dish_from_db(session, menu_id, submenu_id, dish_id)
#     return convert_dish(dish)
#
#
# @router.post('/', status_code=201)
# async def create_dish(menu_id: uuid.UUID,
#                       submenu_id: uuid.UUID,
#                       dish_data: CreateEditDishModel,
#                       session: AsyncSession = Depends(get_async_session)):
#     dish_data.price = validate_price(dish_data.price)
#     new_dish = Dish(**dish_data.model_dump(),
#                     menu_id=menu_id,
#                     submenu_id=submenu_id,
#                     id=uuid.uuid4())
#     session.add(new_dish)
#     await session.commit()
#
#     new_dict = convert_dish(new_dish)
#
#     redis = await get_redis_connection()
#     cache_key = f'menu:{menu_id}/submenu/{submenu_id}/dish/{str({new_dish.id})}'
#     await redis.set(cache_key, json.dumps(new_dict), ex=60)
#
#     await redis.delete(f'menu:{menu_id}/submenu:{submenu_id}/dishes:all')
#     await redis.delete(f'menu:{menu_id}/submenu:{submenu_id}')
#     await redis.delete(f'menu:{menu_id}/submenus:all')
#     await redis.delete(f'menu:{menu_id}')
#     await redis.delete('menus:all')
#
#     return new_dict
#
#
# @router.patch('/{dish_id}')
# async def update_dish(menu_id: uuid.UUID,
#                       submenu_id: uuid.UUID,
#                       dish_id: uuid.UUID,
#                       dish_data: CreateEditDishModel,
#                       session: AsyncSession = Depends(get_async_session)):
#     dish_data.price = validate_price(dish_data.price)
#     query = (update(Dish)
#              .where(Dish.id == dish_id,
#                     Dish.submenu_id == submenu_id,
#                     Dish.menu_id == menu_id)
#              .values(**dish_data.model_dump()))
#     await session.execute(query)
#     await session.commit()
#
#     dish = await get_dish_from_db(session, menu_id, submenu_id, dish_id)
#     dish_dict = convert_dish(dish)
#
#     redis = await get_redis_connection()
#     cache_key = f'menu:{menu_id}/submenu/{submenu_id}/dish/{dish_id}'
#     await redis.set(cache_key, json.dumps(dish_dict), ex=60)
#     await redis.delete(f'menu:{menu_id}/submenu/{submenu_id}/dishes:all')
#
#     return dish_dict
#
#
# @router.delete('/{dish_id}')
# async def delete_dish(menu_id: uuid.UUID,
#                       submenu_id: uuid.UUID,
#                       dish_id: uuid.UUID,
#                       session: AsyncSession = Depends(get_async_session)):
#     query = delete(Dish).where(Dish.id == dish_id,
#                                Dish.submenu_id == submenu_id,
#                                Dish.menu_id == menu_id)
#     result = await session.execute(query)
#     if result.rowcount == 0:
#         raise HTTPException(status_code=404, detail='dish not found')
#     await session.commit()
#
#     redis = await get_redis_connection()
#     await redis.delete(f'menu:{menu_id}/submenu:{submenu_id}/dish:{dish_id}')
#     await redis.delete(f'menu:{menu_id}/submenu:{submenu_id}/dishes:all')
#     await redis.delete(f'menu:{menu_id}/submenu:{submenu_id}')
#     await redis.delete(f'menu:{menu_id}/submenus:all')
#     await redis.delete(f'menu:{menu_id}')
#     await redis.delete('menus:all')
#
#     return {'detail': 'dish deleted'}
#
#
#
#
#
#
