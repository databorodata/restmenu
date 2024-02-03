from fastapi import APIRouter, Depends
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session, get_redis_connection
from app.repositories.cache_repository import CacheRepository
from app.repositories.submenu_repository import SubmenuRepository
from app.services.submenu_service import SubmenuService
from app.schemas import CreateEditSubmenuModel

router = APIRouter(prefix='/api/v1/menus/{menu_id}/submenus', tags=['submenu'])


def get_submenu_service(session: AsyncSession = Depends(get_async_session), redis=Depends(get_redis_connection)):
    menu_repository = SubmenuRepository(session=session)
    cache_repository = CacheRepository(redis=redis)
    return SubmenuService(submenu_repository=menu_repository, cache_repository=cache_repository)


@router.get('/')
async def get_submenus(menu_id: UUID, submenu_service: SubmenuService = Depends(get_submenu_service)):
    return await submenu_service.get_submenus(menu_id)


@router.get('/{submenu_id}')
async def get_submenu(menu_id: UUID, submenu_id: UUID, submenu_service: SubmenuService = Depends(get_submenu_service)):
    return await submenu_service.get_submenu(menu_id, submenu_id)


@router.post('/', status_code=201)
async def create_submenu(menu_id: UUID, submenu_data: CreateEditSubmenuModel, submenu_service: SubmenuService = Depends(get_submenu_service)):
    return await submenu_service.create_submenu(menu_id, submenu_data.model_dump())


@router.patch('/{submenu_id}')
async def update_submenu(menu_id: UUID, submenu_id: UUID, submenu_data: CreateEditSubmenuModel, submenu_service: SubmenuService = Depends(get_submenu_service)):
    return await submenu_service.update_submenu(menu_id, submenu_id, submenu_data.model_dump())


@router.delete('/{submenu_id}')
async def delete_submenu(menu_id: UUID, submenu_id: UUID, submenu_service: SubmenuService = Depends(get_submenu_service)):
    return await submenu_service.delete_submenu(menu_id, submenu_id)
