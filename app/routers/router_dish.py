from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session, get_redis_connection
from app.repositories.cache_repository import CacheRepository
from app.repositories.dish_repository import DishRepository
from app.schemas import CreateEditDishModel, DishModel
from app.services.dish_service import DishDict, DishService

router = APIRouter(
    prefix='/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes',
    tags=['Dishes'],
)


def get_dish_service(
        session: AsyncSession = Depends(get_async_session),
        redis=Depends(get_redis_connection)) -> DishService:
    """Предоставляет сервис для работы с блюдо."""
    menu_repository = DishRepository(session=session)
    cache_repository = CacheRepository(redis=redis)
    return DishService(dish_repository=menu_repository, cache_repository=cache_repository)


def convert_dish(dish: DishDict) -> DishModel:
    return DishModel.model_validate(dish, from_attributes=True)


@router.get(
    '/',
    status_code=200,
    response_model=list[DishModel],
    summary='Получить список блюд',
    responses={
        200: {'description': 'Список блюд успешно получен'}
    }
)
async def get_dishes(
        menu_id: UUID,
        submenu_id: UUID,
        dish_service: DishService = Depends(get_dish_service)
) -> list[DishModel]:
    """
    Возвращает список всех блюд в подменю.

    - **menu_id**: UUID родительского меню.
    - **submenu_id**: UUID родительского подменю.
    """
    dishes = await dish_service.get_dishes(menu_id, submenu_id)
    return [convert_dish(dish) for dish in dishes]


@router.get(
    '/{dish_id}',
    status_code=200,
    response_model=DishModel,
    summary='Получить детали блюда',
    responses={
        200: {'description': 'Успешное получение деталей блюда'},
        404: {
            'description': 'Блюдо не найдено',
            'content': {
                'application/json': {
                    'example': {'detail': 'dish not found'}
                }
            },
        },
    },
)
async def get_dish(
        menu_id: UUID,
        submenu_id: UUID,
        dish_id: UUID,
        dish_service: DishService = Depends(get_dish_service)
) -> DishModel:
    """
    Возвращает детали блюда по его идентификатору.

    - **menu_id**: UUID родительского меню.
    - **submenu_id**: UUID родительского подменю.
    - **dish_id**: UUID блюда для получения информации.
    """
    dish = await dish_service.get_dish(menu_id, submenu_id, dish_id)
    return convert_dish(dish)


@router.post(
    '/',
    status_code=201,
    response_model=DishModel,
    summary='Создать новое блюдо',
    responses={
        201: {'description': 'Созданное блюдо'},
    },
)
async def create_dish(
        menu_id: UUID,
        submenu_id: UUID,
        dish_data: CreateEditDishModel,
        dish_service: DishService = Depends(get_dish_service)
) -> DishModel:
    """
    Создает новое блюдо в подменю.

    - **menu_id**: UUID родительского меню.
    - **submenu_id**: UUID родительского подменю.
    - **dish_data**: данные для создания блюда.
    """
    dish = await dish_service.create_dish(menu_id, submenu_id, dish_data.model_dump())
    return convert_dish(dish)


@router.patch(
    '/{dish_id}',
    response_model=DishModel,
    summary='Обновить блюдо',
    responses={
        200: {'description': 'Обновленное блюдо'},
        404: {
            'description': 'Блюдо не найдено',
            'content': {
                'application/json': {
                    'example': {'detail': 'dish not found'}
                }
            },
        },
    },
)
async def update_dish(
        menu_id: UUID,
        submenu_id: UUID,
        dish_id: UUID,
        dish_data: CreateEditDishModel,
        dish_service: DishService = Depends(get_dish_service)
) -> DishModel:
    """
    Обновляет информацию о блюде.

    - **menu_id**: UUID родительского меню.
    - **submenu_id**: UUID родительского подменю.
    - **dish_id**: UUID обновляемого блюда.
    - **dish_data**: новые данные для блюда.
    """
    dish = await dish_service.update_dish(menu_id, submenu_id, dish_id, dish_data.model_dump())
    return convert_dish(dish)


@router.delete(
    '/{dish_id}',
    status_code=200,
    summary='Удалить блюдо',
    responses={
        200: {
            'description': 'Блюдо удалено',
            'content': {
                'application/json': {
                    'example': {'detail': 'dish deleted'}
                }
            },
        },
        404: {
            'description': 'Блюдо не найдено',
            'content': {
                'application/json': {
                    'example': {'detail': 'dish not found'}
                }
            },
        },
    },
)
async def delete_dish(
        menu_id: UUID,
        submenu_id: UUID,
        dish_id: UUID,
        dish_service: DishService = Depends(get_dish_service)
) -> dict[str, str]:
    """
    Удаляет блюдо из подменю.

    - **menu_id**: UUID родительского меню.
    - **submenu_id**: UUID родительского подменю.
    - **dish_id**: UUID удаляемого блюда.
    """
    await dish_service.delete_dish(menu_id, submenu_id, dish_id)
    return {'detail': 'dish deleted'}
