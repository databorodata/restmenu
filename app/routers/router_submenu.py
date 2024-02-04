from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session, get_redis_connection
from app.repositories.cache_repository import CacheRepository
from app.repositories.submenu_repository import SubmenuRepository
from app.schemas import CreateEditSubmenuModel, SubmenuModel
from app.services.submenu_service import SubmenuService

router = APIRouter(prefix='/api/v1/menus/{menu_id}/submenus', tags=['submenu'])


def get_submenu_service(
        session: AsyncSession = Depends(get_async_session),
        redis=Depends(get_redis_connection)
) -> SubmenuService:
    """Предоставляет сервис для работы с подменю."""
    menu_repository = SubmenuRepository(session=session)
    cache_repository = CacheRepository(redis=redis)
    return SubmenuService(submenu_repository=menu_repository, cache_repository=cache_repository)


@router.get('/', status_code=200, response_model=list[SubmenuModel])
async def get_submenus(
        menu_id: UUID,
        submenu_service: SubmenuService = Depends(get_submenu_service)
) -> list[dict]:
    """Получает список всех подменю."""
    return await submenu_service.get_submenus(menu_id)


@router.get('/{submenu_id}', status_code=200, response_model=SubmenuModel)
async def get_submenu(
        menu_id: UUID, submenu_id: UUID,
        submenu_service: SubmenuService = Depends(get_submenu_service)
) -> dict:
    """Получает подменю по его ID."""
    return await submenu_service.get_submenu(menu_id, submenu_id)


@router.post('/', status_code=201, response_model=SubmenuModel)
async def create_submenu(menu_id: UUID,
                         submenu_data: CreateEditSubmenuModel,
                         submenu_service: SubmenuService = Depends(get_submenu_service)
                         ) -> dict:
    """Создает новое подменю."""
    return await submenu_service.create_submenu(menu_id, submenu_data.model_dump())


@router.patch('/{submenu_id}', status_code=200, response_model=SubmenuModel)
async def update_submenu(
        menu_id: UUID,
        submenu_id: UUID,
        submenu_data: CreateEditSubmenuModel,
        submenu_service: SubmenuService = Depends(get_submenu_service)
) -> dict:
    """Обновляет существующее подменю по его ID."""
    return await submenu_service.update_submenu(menu_id, submenu_id, submenu_data.model_dump())


@router.delete('/{submenu_id}', status_code=200)
async def delete_submenu(
        menu_id: UUID,
        submenu_id: UUID,
        submenu_service: SubmenuService = Depends(get_submenu_service)
) -> dict:
    """Удаляет подменю по его ID."""
    return await submenu_service.delete_submenu(menu_id, submenu_id)
