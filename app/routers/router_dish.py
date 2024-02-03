from fastapi import APIRouter, Depends
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session, get_redis_connection
from app.repositories.cache_repository import CacheRepository
from app.repositories.dish_repository import DishRepository
from app.services.dish_service import DishService
from app.schemas import CreateEditDishModel

router = APIRouter(prefix='/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', tags=['dish'])


def get_dish_service(session: AsyncSession = Depends(get_async_session), redis=Depends(get_redis_connection)):
    menu_repository = DishRepository(session=session)
    cache_repository = CacheRepository(redis=redis)
    return DishService(dish_repository=menu_repository, cache_repository=cache_repository)


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
    return await dish_service.update_dish(menu_id, submenu_id, dish_id, dish_data.model_dump())


@router.delete('/{dish_id}')
async def delete_dish(menu_id: UUID, submenu_id: UUID, dish_id: UUID, dish_service: DishService = Depends(get_dish_service)):
    return await dish_service.delete_dish(menu_id, submenu_id, dish_id)
