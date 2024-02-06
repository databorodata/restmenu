from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session, get_redis_connection
from app.repositories.cache_repository import CacheRepository
from app.repositories.menu_repository import MenuRepository
from app.schemas import CreateEditMenuModel, MenuModel
from app.services.menu_service import MenuService

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


# @router.get('/', status_code=200, response_model=list[MenuModel], summary="Получить список меню")
@router.get(
    '/menus/',
    summary='Получить список меню',
    response_description='Список всех меню',
    response_model=list[MenuModel],
    responses={
        200: {
            'description': 'Список меню успешно получен',
            'content': {
                'application/json': {
                    'examples': {
                        'normal': {
                            'summary': 'Пример списка меню',
                            'value': [
                                {
                                    'id': 'a2eb416c-2245-4526-bb4b-6343d5c5016f',
                                    'title': 'My menu 1',
                                    'description': 'My menu description 1',
                                    'submenus_count': 0,
                                    'dishes_count': 0
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
)
async def get_menus(menu_service: MenuService = Depends(get_menu_service)) -> list[dict]:
    """Возвращает список всех доступных меню в системе."""
    return await menu_service.get_menus()


# @router.get('/{menu_id}', status_code=200, response_model=MenuModel, summary="Получить детали меню")
@router.get(
    '/{item_id}',
    responses={
        200: {'description': 'Успешное получение деталей элемента'},
        404: {
            'description': 'Элемент не найден',
            'content': {
                'application/json': {
                    'example': {'detail': 'Элемент с указанным ID не найден'}
                }
            },
        },
    },
    tags=['Items'],
    summary='Получить детали элемента'
)
async def get_menu(
    menu_id: UUID,
    menu_service: MenuService = Depends(get_menu_service)
) -> dict[str, Any]:
    """
    Возвращает детали меню по его уникальному идентификатору.

    - **menu_id**: UUID меню для получения информации.
    """

    return await menu_service.get_menu(menu_id)


@router.post('/', status_code=201, response_model=MenuModel, summary='Создать новое меню')
async def create_menu(
        menu_data: CreateEditMenuModel,
        menu_service: MenuService = Depends(get_menu_service)
) -> dict:
    """
    Создает новое меню с указанными данными.

    - **menu_data**: данные для создания меню.
    """
    return await menu_service.create_menu(menu_data.model_dump())


@router.patch('/{menu_id}', response_model=MenuModel, summary='Обновить меню')
async def update_menu(
        menu_id: UUID,
        menu_data: CreateEditMenuModel,
        menu_service: MenuService = Depends(get_menu_service)
) -> dict:
    """
    Обновляет информацию о меню по его идентификатору.

    - **menu_id**: UUID обновляемого меню.
    - **menu_data**: новые данные для меню.
    """
    return await menu_service.update_menu(menu_id, menu_data.model_dump())


@router.delete('/{menu_id}', status_code=200, summary='Удалить меню')
async def delete_menu(
        menu_id: UUID,
        menu_service: MenuService = Depends(get_menu_service)
) -> dict:
    """
    Удаляет меню по его идентификатору.

    - **menu_id**: UUID удаляемого меню.
    """
    return await menu_service.delete_menu(menu_id)
