from fastapi import APIRouter, Depends
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.cache_repository import CacheRepository
from app.database import get_async_session, get_redis_connection
from app.repositories.menu_repository import MenuRepository
from app.services.menu_service import MenuService
from app.schemas import CreateEditMenuModel

router = APIRouter(prefix='/api/v1/menus', tags=['menu'])


def get_menu_service(session: AsyncSession = Depends(get_async_session), redis=Depends(get_redis_connection)):
    menu_repository = MenuRepository(session=session)
    cache_repository = CacheRepository(redis=redis)
    return MenuService(menu_repository=menu_repository, cache_repository=cache_repository)


@router.get('/')
async def get_menus(menu_service: MenuService = Depends(get_menu_service)):
    return await menu_service.get_menus()


@router.get('/{menu_id}')
async def get_menu(menu_id: UUID, menu_service: MenuService = Depends(get_menu_service)):
    return await menu_service.get_menu(menu_id)


@router.post('/', status_code=201)
async def create_menu(menu_data: CreateEditMenuModel, menu_service: MenuService = Depends(get_menu_service)):
    return await menu_service.create_menu(menu_data.model_dump())


@router.patch('/{menu_id}')
async def update_menu(menu_id: UUID, menu_data: CreateEditMenuModel, menu_service: MenuService = Depends(get_menu_service)):
    return await menu_service.update_menu(menu_id, menu_data.model_dump())


@router.delete('/{menu_id}')
async def delete_menu(menu_id: UUID, menu_service: MenuService = Depends(get_menu_service)):
    return await menu_service.delete_menu(menu_id)
