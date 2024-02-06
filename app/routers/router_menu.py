from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session, get_redis_connection
from app.repositories.cache_repository import CacheRepository
from app.repositories.menu_repository import MenuRepository
from app.schemas import CreateEditMenuModel, MenuModel
from app.services.menu_service import MenuDict, MenuService

router = APIRouter(
    prefix='/api/v1/menus',
    tags=['Menus'],
)


def get_menu_service(
        session: AsyncSession = Depends(get_async_session),
        redis=Depends(get_redis_connection)
) -> MenuService:
    """Предоставляет сервис для работы с меню."""
    menu_repository = MenuRepository(session=session)
    cache_repository = CacheRepository(redis=redis)
    return MenuService(menu_repository=menu_repository, cache_repository=cache_repository)


def convert_menu(menu: MenuDict) -> MenuModel:
    return MenuModel.model_validate(menu, from_attributes=True)


@router.get(
    '/menus/',
    summary='Получить список меню',
    response_description='Список всех меню',
    response_model=list[MenuModel],
    responses={
        200: {'description': 'Список меню успешно получен'}
    },
)
async def get_menus(menu_service: MenuService = Depends(get_menu_service)) -> list[MenuModel]:
    """Возвращает список всех доступных меню в системе."""
    menus = await menu_service.get_menus()
    return [convert_menu(it) for it in menus]


# @router.get('/{menu_id}', status_code=200, response_model=MenuModel, summary='Получить детали меню')
@router.get(
    '/{menu_id}',
    summary='Получить детали меню',
    response_description='Детали меню',
    response_model=MenuModel,
    responses={
        200: {'description': 'Успешное получение деталей меню'},
        404: {
            'description': 'Меню не найдено',
            'content': {
                'application/json': {
                    'example': {'detail': 'menu not found'}
                }
            },
        },
    },
)
async def get_menu(
    menu_id: UUID,
    menu_service: MenuService = Depends(get_menu_service)
) -> MenuModel:
    """
    Возвращает детали меню по его уникальному идентификатору.

    - **menu_id**: UUID меню для получения информации.
    """

    menu = await menu_service.get_menu(menu_id)
    return convert_menu(menu)


@router.post(
    '/',
    status_code=201,
    response_model=MenuModel,
    response_description='Успешно созданное меню',
    summary='Создать новое меню',
    responses={
        201: {'description': 'Созданное меню'},
    }
)
async def create_menu(
    menu_data: CreateEditMenuModel,
    menu_service: MenuService = Depends(get_menu_service)
) -> MenuModel:
    """
    Создает новое меню с указанными данными.

    - **menu_data**: данные для создания меню.
    """
    menu = await menu_service.create_menu(menu_data.model_dump())
    return convert_menu(menu)


@router.patch(
    '/{menu_id}',
    response_model=MenuModel,
    response_description='Успешно обновленное меню',
    summary='Обновить меню',
    responses={
        200: {'description': 'Обновленное меню'},
        404: {
            'description': 'Меню не найдено',
            'content': {
                'application/json': {
                    'example': {'detail': 'menu not found'}
                }
            },
        },
    },
)
async def update_menu(
    menu_id: UUID,
    menu_data: CreateEditMenuModel,
    menu_service: MenuService = Depends(get_menu_service)
) -> MenuModel:
    """
    Обновляет информацию о меню по его идентификатору.

    - **menu_id**: UUID обновляемого меню.
    - **menu_data**: новые данные для меню.
    """
    menu = await menu_service.update_menu(menu_id, menu_data.model_dump())
    return convert_menu(menu)


@router.delete(
    '/{menu_id}',
    status_code=200,
    summary='Удалить меню',
    responses={
        200: {
            'description': 'Меню удалено',
            'content': {
                'application/json': {
                    'example': {'detail': 'menu deleted'}
                }
            },
        },
        404: {
            'description': 'Меню не найдено',
            'content': {
                'application/json': {
                    'example': {'detail': 'menu not found'}
                }
            },
        },
    },
)
async def delete_menu(
        menu_id: UUID,
        menu_service: MenuService = Depends(get_menu_service)
) -> dict[str, str]:
    """
    Удаляет меню по его идентификатору.

    - **menu_id**: UUID удаляемого меню.
    """
    await menu_service.delete_menu(menu_id)
    return {'detail': 'menu deleted'}
