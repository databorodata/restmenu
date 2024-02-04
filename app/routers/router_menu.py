from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session, get_redis_connection
from app.repositories.cache_repository import CacheRepository
from app.repositories.menu_repository import MenuRepository
from app.schemas import CreateEditMenuModel, MenuModel
from app.services.menu_service import MenuService

router = APIRouter(prefix='/api/v1/menus', tags=['menu'])


def get_menu_service(
        session: AsyncSession = Depends(get_async_session),
        redis=Depends(get_redis_connection)
) -> MenuService:
    """Предоставляет сервис для работы с меню."""
    menu_repository = MenuRepository(session=session)
    cache_repository = CacheRepository(redis=redis)
    return MenuService(menu_repository=menu_repository, cache_repository=cache_repository)


@router.get('/', status_code=200, response_model=list[MenuModel])
async def get_menus(menu_service: MenuService = Depends(get_menu_service)) -> list[dict]:
    """Получает список всех меню."""
    return await menu_service.get_menus()


@router.get('/{menu_id}', status_code=200, response_model=MenuModel)
async def get_menu(
    menu_id: UUID,
    menu_service: MenuService = Depends(get_menu_service)
) -> dict:
    """Получает меню по его ID."""
    return await menu_service.get_menu(menu_id)


@router.post('/', status_code=201, response_model=MenuModel)
async def create_menu(
        menu_data: CreateEditMenuModel,
        menu_service: MenuService = Depends(get_menu_service)
) -> dict:
    """Создает новое меню."""
    return await menu_service.create_menu(menu_data.model_dump())


@router.patch('/{menu_id}', response_model=MenuModel)
async def update_menu(
        menu_id: UUID,
        menu_data: CreateEditMenuModel,
        menu_service: MenuService = Depends(get_menu_service)
) -> dict:
    """Обновляет существующее меню по его ID."""
    return await menu_service.update_menu(menu_id, menu_data.model_dump())


@router.delete('/{menu_id}', status_code=200)
async def delete_menu(
        menu_id: UUID,
        menu_service: MenuService = Depends(get_menu_service)
) -> dict:
    """Удаляет меню по его ID."""
    return await menu_service.delete_menu(menu_id)
