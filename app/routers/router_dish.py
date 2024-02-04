from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session, get_redis_connection
from app.repositories.cache_repository import CacheRepository
from app.repositories.dish_repository import DishRepository
from app.schemas import CreateEditDishModel, DishModel
from app.services.dish_service import DishService

router = APIRouter(prefix='/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', tags=['dish'])


def get_dish_service(
        session: AsyncSession = Depends(get_async_session),
        redis=Depends(get_redis_connection)) -> DishService:
    """Предоставляет сервис для работы с блюдо."""
    menu_repository = DishRepository(session=session)
    cache_repository = CacheRepository(redis=redis)
    return DishService(dish_repository=menu_repository, cache_repository=cache_repository)


@router.get('/', status_code=200, response_model=list[DishModel])
async def get_dishes(
        menu_id: UUID,
        submenu_id: UUID,
        dish_service: DishService = Depends(get_dish_service)
) -> list[dict]:
    """Получает список всех блюдо."""
    return await dish_service.get_dishes(menu_id, submenu_id)


@router.get('/{dish_id}', status_code=200, response_model=DishModel)
async def get_dish(
        menu_id: UUID,
        submenu_id: UUID,
        dish_id: UUID,
        dish_service: DishService = Depends(get_dish_service)
) -> dict:
    """Получает блюдо по его ID."""
    return await dish_service.get_dish(menu_id, submenu_id, dish_id)


@router.post('/', status_code=201, response_model=DishModel)
async def create_dish(
        menu_id: UUID,
        submenu_id: UUID,
        dish_data: CreateEditDishModel,
        dish_service: DishService = Depends(get_dish_service)
) -> dict:
    """Создает новое блюдо."""
    return await dish_service.create_dish(menu_id, submenu_id, dish_data.model_dump())


@router.patch('/{dish_id}', response_model=DishModel)
async def update_dish(
        menu_id: UUID,
        submenu_id: UUID,
        dish_id: UUID,
        dish_data: CreateEditDishModel,
        dish_service: DishService = Depends(get_dish_service)
) -> dict:
    """Обновляет существующее блюдо по его ID."""
    return await dish_service.update_dish(menu_id, submenu_id, dish_id, dish_data.model_dump())


@router.delete('/{dish_id}', status_code=200)
async def delete_dish(
        menu_id: UUID,
        submenu_id: UUID,
        dish_id: UUID,
        dish_service: DishService = Depends(get_dish_service)
) -> dict:
    """Удаляет блюдо по его ID."""
    return await dish_service.delete_dish(menu_id, submenu_id, dish_id)
