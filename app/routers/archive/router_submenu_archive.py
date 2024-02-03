import uuid
import json
import logging

import aioredis
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session, get_redis_connection
from app.models import Submenu, Dish
from app.schemas import CreateEditSubmenuModel, SubmenuModel

router = APIRouter(prefix='/api/v1/menus/{menu_id}/submenus', tags=['submenu'])
logger = logging.getLogger(__name__)

logging.basicConfig(filename='redis_operations.log', level=logging.INFO, format='%(asctime)s - %(message)s')


async def get_dishes_count_for_submenus(session: AsyncSession, submenu_id: uuid.UUID):
    query = select(func.count()).where(Dish.submenu_id == submenu_id).select_from(Dish)
    result = await session.execute(query)
    dishes_count = result.scalar_one()
    return dishes_count

# Функция для получения подменю с подсчетом блюд
async def get_submenu_with_dishes_count(session, menu_id: uuid.UUID, submenu_id: uuid.UUID):
    query = select(Submenu).where(Submenu.id == submenu_id, Submenu.menu_id == menu_id)
    result = await session.execute(query)
    submenu = result.scalars().one_or_none()
    if submenu is None:
        raise HTTPException(status_code=404, detail='submenu not found')

    dishes_count = await get_dishes_count_for_submenus(session, submenu_id)
    return submenu, dishes_count

# Конвертация объекта Submenu в словарь, включая количество блюд
def convert_submenu(submenu, dishes_count):
    submenu_dict = SubmenuModel.model_validate(submenu, from_attributes=True).model_dump()
    submenu_dict['id'] = str(submenu_dict['id'])
    submenu_dict.update({'dishes_count': dishes_count})
    return submenu_dict

@router.get('/')
async def get_submenus(menu_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    redis = await get_redis_connection()
    cache_key = f'menu:{menu_id}/submenus:all'
    cached_submenus = await redis.get(cache_key)

    if cached_submenus:
        logger.info('Fetching all submenus from cache')
        return json.loads(cached_submenus)

    logger.info('Fetching all submenus from database')

    query = select(Submenu).where(Submenu.menu_id == menu_id)
    result = await session.execute(query)
    submenus = result.scalars().all()

    # Добавляем количество блюд для каждого подменю
    submenus_with_counts = []
    for submenu in submenus:
        dishes_count = await get_dishes_count_for_submenus(session, submenu.id)
        submenus_with_counts.append(convert_submenu(submenu, dishes_count))

    await redis.set(cache_key, json.dumps(submenus_with_counts), ex=60)

    return submenus_with_counts

@router.get('/{submenu_id}')
async def get_submenu(menu_id: uuid.UUID, submenu_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    redis = await get_redis_connection()
    cache_key = f'menu:{menu_id}/submenu/{submenu_id}'
    cached_submenu = await redis.get(cache_key)

    if cached_submenu:
        logger.info(f'Fetching submenu {submenu_id} from cache')
        return json.loads(cached_submenu)

    logger.info(f'Fetching submenu {submenu_id} from database')

    submenu, dishes_count = await get_submenu_with_dishes_count(session, menu_id, submenu_id)
    return convert_submenu(submenu, dishes_count)

@router.post('/', status_code=201)
async def create_submenu(menu_id: uuid.UUID, submenu_data: CreateEditSubmenuModel, session: AsyncSession = Depends(get_async_session)):
    new_submenu = Submenu(**submenu_data.model_dump(), menu_id=menu_id, id=uuid.uuid4())
    session.add(new_submenu)
    await session.commit()

    submenu_dict = convert_submenu(new_submenu, dishes_count=0)
    submenu_dict['id'] = str(submenu_dict['id'])

    redis = await get_redis_connection()
    cache_key = f'menu:{menu_id}/submenu/{str(new_submenu.id)}'
    await redis.set(cache_key, json.dumps(submenu_dict), ex=60)
    await redis.delete(f'menu:{menu_id}/submenus:all')
    await redis.delete(f'menu:{menu_id}')
    await redis.delete('menus:all')

    return submenu_dict

@router.patch('/{submenu_id}')
async def update_submenu(menu_id: uuid.UUID, submenu_id: uuid.UUID, submenu_data: CreateEditSubmenuModel, session: AsyncSession = Depends(get_async_session)):
    await session.execute(update(Submenu).where(Submenu.id == submenu_id, Submenu.menu_id == menu_id).values(**submenu_data.model_dump()))
    await session.commit()

    # Получаем обновленное подменю и количество блюд после обновления
    submenu, dishes_count = await get_submenu_with_dishes_count(session, menu_id, submenu_id)

    new_submenu_data = {
        'id': str(submenu_id),
        'title': submenu_data.title,
        'description': submenu_data.description,
        'dishes_count': dishes_count
    }

    redis = await get_redis_connection()
    cache_key = f'submenu:{submenu_id}'
    await redis.set(cache_key, json.dumps(new_submenu_data), ex=60)
    await redis.delete(f'menu:{menu_id}/submenus:all')  # Инвалидируем кэш списка всех меню

    return convert_submenu(submenu, dishes_count)

@router.delete('/{submenu_id}')
async def delete_submenu(menu_id: uuid.UUID, submenu_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(delete(Submenu).where(Submenu.id == submenu_id, Submenu.menu_id == menu_id))
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail='submenu not found')
    await session.commit()

    redis = await get_redis_connection()

    cursor = 0
    submenu_keys = []

    # Перебор ключей, соответствующих шаблону
    while True:
        cursor, keys = await redis.scan(cursor, match=f'menu:{menu_id}/submenu:{submenu_id}*', count=100)
        submenu_keys.extend(keys)
        if cursor == 0:  # Если курсор вернулся в начало, завершаем цикл
            break

    # submenu_keys = [key async for key in redis.iscan(match=f'menu:{menu_id}/submenu:{submenu_id}*')]
    if submenu_keys:
        await redis.delete(*submenu_keys)
    await redis.delete(f'menu:{menu_id}/submenus:all')
    await redis.delete(f'menu:{menu_id}')
    await redis.delete('menus:all')

    return {'detail': 'submenu deleted'}





