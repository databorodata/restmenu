from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session, get_redis_connection
from app.repositories.cache_repository import CacheRepository
from app.repositories.submenu_repository import SubmenuRepository
from app.schemas import CreateEditSubmenuModel, SubmenuModel
from app.services.submenu_service import SubmenuDict, SubmenuService

router = APIRouter(
    prefix='/api/v1/menus/{menu_id}/submenus',
    tags=['Submenus'],
)


def get_submenu_service(
        session: AsyncSession = Depends(get_async_session),
        redis=Depends(get_redis_connection)
) -> SubmenuService:
    """Предоставляет сервис для работы с подменю."""
    menu_repository = SubmenuRepository(session=session)
    cache_repository = CacheRepository(redis=redis)
    return SubmenuService(submenu_repository=menu_repository, cache_repository=cache_repository)


def convert_submenu(submenu: SubmenuDict) -> SubmenuModel:
    return SubmenuModel.model_validate(submenu, from_attributes=True)


@router.get(
    '/',
    status_code=200,
    response_model=list[SubmenuModel],
    summary='Получить список подменю',
    responses={
        200: {'description': 'Список подменю успешно получен'}
    },
)
async def get_submenus(
        menu_id: UUID,
        submenu_service: SubmenuService = Depends(get_submenu_service)
) -> list[SubmenuModel]:
    """
    Возвращает список подменю для указанного меню.

    - **menu_id**: UUID родительского меню.
    """
    submenus = await submenu_service.get_submenus(menu_id)
    return [convert_submenu(it) for it in submenus]


@router.get(
    '/{submenu_id}',
    status_code=200,
    response_model=SubmenuModel,
    summary='Получить детали подменю',
    responses={
        200: {'description': 'Успешное получение деталей подменю'},
        404: {
            'description': 'Подменю не найдено',
            'content': {
                'application/json': {
                    'example': {'detail': 'submenu not found'}
                }
            },
        },
    },
)
async def get_submenu(
        menu_id: UUID, submenu_id: UUID,
        submenu_service: SubmenuService = Depends(get_submenu_service)
) -> SubmenuModel:
    """
    Возвращает детали подменю по его идентификатору.

    - **menu_id**: UUID родительского меню.
    - **submenu_id**: UUID подменю для получения информации.
    """
    submenu = await submenu_service.get_submenu(menu_id, submenu_id)
    return convert_submenu(submenu)


@router.post(
    '/',
    status_code=201,
    response_model=SubmenuModel,
    summary='Создать новое подменю',
    responses={
        201: {'description': 'Созданное подменю'},
    }
)
async def create_submenu(
        menu_id: UUID,
        submenu_data: CreateEditSubmenuModel,
        background_tasks: BackgroundTasks,
        submenu_service: SubmenuService = Depends(get_submenu_service)
) -> SubmenuModel:
    """
    Создает новое подменю в указанном меню.

    - **menu_id**: UUID родительского меню.
    - **submenu_data**: данные для создания подменю.
    """
    submenu = await submenu_service.create_submenu(
        menu_id,
        submenu_data.model_dump(),
        background_tasks
    )
    return convert_submenu(submenu)


@router.patch(
    '/{submenu_id}',
    status_code=200,
    response_model=SubmenuModel,
    summary='Обновить подменю',
    responses={
        200: {'description': 'Обновленное подменю'},
        404: {
            'description': 'Подменю не найдено',
            'content': {
                'application/json': {
                    'example': {'detail': 'submenu not found'}
                }
            },
        },
    },
)
async def update_submenu(
    menu_id: UUID,
    submenu_id: UUID,
    submenu_data: CreateEditSubmenuModel,
    background_tasks: BackgroundTasks,
    submenu_service: SubmenuService = Depends(get_submenu_service)
) -> SubmenuModel:
    """
    Обновляет информацию о подменю.

    - **menu_id**: UUID родительского меню.
    - **submenu_id**: UUID обновляемого подменю.
    - **submenu_data**: новые данные для подменю.
    """
    submenu = await submenu_service.update_submenu(
        menu_id,
        submenu_id,
        submenu_data.model_dump(),
        background_tasks
    )
    return convert_submenu(submenu)


@router.delete(
    '/{submenu_id}',
    status_code=200,
    summary='Удалить подменю',
    responses={
        200: {
            'description': 'Подменю удалено',
            'content': {
                'application/json': {
                    'example': {'detail': 'submenu deleted'}
                }
            },
        },
        404: {
            'description': 'Подменю не найдено',
            'content': {
                'application/json': {
                    'example': {'detail': 'submenu not found'}
                }
            },
        },
    },
)
async def delete_submenu(
    menu_id: UUID,
    submenu_id: UUID,
    background_tasks: BackgroundTasks,
    submenu_service: SubmenuService = Depends(get_submenu_service)
) -> dict[str, str]:
    """
    Удаляет подменю из родительского меню.

    - **menu_id**: UUID родительского меню.
    - **submenu_id**: UUID удаляемого подменю.
    """
    await submenu_service.delete_submenu(menu_id, submenu_id, background_tasks)
    return {'detail': 'submenu deleted'}
