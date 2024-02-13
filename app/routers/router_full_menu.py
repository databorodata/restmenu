from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session, get_redis_connection
from app.repositories.cache_repository import CacheRepository
from app.repositories.menu_repository import MenuRepository
from app.schemas import FullMenuModel
from app.services.full_menu_service import FullMenuService

router = APIRouter(
    prefix='/api/v1/full_menu',
    tags=['full_menu'],
)


def get_full_menu_service(
        session: AsyncSession = Depends(get_async_session),
        redis=Depends(get_redis_connection)
) -> FullMenuService:
    """Предоставляет сервис для работы с меню."""
    menu_repository = MenuRepository(session=session)
    cache_repository = CacheRepository(redis)
    return FullMenuService(menu_repository=menu_repository, cache_repository=cache_repository)


@router.get(
    '/',
    summary='Получить список меню со всеми связанными подменю и со всеми связанными блюдами',
    response_description='Список всех меню',
    response_model=list[FullMenuModel],
    responses={
        200: {'description': 'Список меню успешно получен'}
    },
)
async def get_full_menus(full_menu_service: FullMenuService = Depends(get_full_menu_service)) -> list[FullMenuModel]:
    """Возвращает список всех доступных меню в системе."""
    """Со связанными подменю и блюдами"""
    result = await full_menu_service.get_full_menus()
    return result
