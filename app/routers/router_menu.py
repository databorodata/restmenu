import json
import logging
import uuid

import aioredis
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_async_session, get_redis_connection
from app.models import Dish, Menu, Submenu
from app.schemas import CreateEditMenuModel, MenuModel

router = APIRouter(prefix='/api/v1/menus', tags=['menu'])
logger = logging.getLogger(__name__)

logging.basicConfig(filename='redis_operations.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# menu:aaa
# menu:aaa/submenu:bbb
# menu:aaa/submenu:bbb/dish:ccc


async def complex_menu_query(session, menu_id=None):
    submenus_count_subq = (
        select(func.count(Submenu.id))
        .where(Submenu.menu_id == Menu.id)
        .scalar_subquery()
    )

    dishes_count_subq = (
        select(func.count(Dish.id))
        .join(Submenu, Submenu.id == Dish.submenu_id)
        .where(Submenu.menu_id == Menu.id)
        .scalar_subquery()
    )

    query = (
        select(
            Menu,
            submenus_count_subq.label('submenus_count'),
            dishes_count_subq.label('dishes_count')
        )
    )

    if menu_id:
        query = query.where(Menu.id == menu_id)

    result = await session.execute(query)
    return result.all() if menu_id is None else result.first()


@router.get('/')
async def get_menus(session: AsyncSession = Depends(get_async_session)):
    redis = await get_redis_connection()
    cache_key = 'menus:all'
    cached_menus = await redis.get(cache_key)
    print('get_menus', cached_menus)

    if cached_menus:
        logger.info('Fetching all menus from cache')
        return json.loads(cached_menus)

    logger.info('Fetching all menus from database')
    menus_data = await complex_menu_query(session)

    menus_list = [
        {
            'id': str(menu.id),
            'title': menu.title,
            'description': menu.description,
            'submenus_count': submenus_count,
            'dishes_count': dishes_count
        }
        for menu, submenus_count, dishes_count in menus_data
    ]

    await redis.set(cache_key, json.dumps(menus_list), ex=60)

    return menus_list

# Получение конкретного меню по ID


@router.get('/{menu_id}')
async def get_menu(menu_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    redis = await get_redis_connection()
    cache_key = f'menu:{menu_id}'
    cached_menu = await redis.get(cache_key)
    print('get_menus', cached_menu)

    if cached_menu:
        logger.info(f'Fetching menu {menu_id} from cache')
        return json.loads(cached_menu)

    logger.info(f'Fetching menu {menu_id} from database')
    menu_item = await complex_menu_query(session, menu_id)

    if menu_item is None:
        raise HTTPException(status_code=404, detail='menu not found')

    menu, submenus_count, dishes_count = menu_item
    menu_data = {
        'id': str(menu.id),
        'title': menu.title,
        'description': menu.description,
        'submenus_count': submenus_count,
        'dishes_count': dishes_count
    }

    await redis.set(cache_key, json.dumps(menu_data), ex=60)

    return menu_data

# Создание нового меню


@router.post('/', status_code=201)
async def create_menu(menu_data: CreateEditMenuModel, session: AsyncSession = Depends(get_async_session)):
    new_menu = Menu(**menu_data.model_dump(), id=uuid.uuid4())
    session.add(new_menu)
    await session.commit()

    menu_data = {
        'id': str(new_menu.id),
        'title': new_menu.title,
        'description': new_menu.description,
        'submenus_count': 0,
        'dishes_count': 0
    }

    redis = await get_redis_connection()
    cache_key = f'menu:{new_menu.id}'
    await redis.set(cache_key, json.dumps(menu_data), ex=60)
    await redis.delete('menus:all')

    return menu_data

# Обновление меню по ID


@router.patch('/{menu_id}')
async def update_menu(menu_id: uuid.UUID, menu_data: CreateEditMenuModel, session: AsyncSession = Depends(get_async_session)):
    await session.execute(
        update(Menu)
        .where(Menu.id == menu_id)
        .values(**menu_data.model_dump())
    )
    await session.commit()


    updated_menu = await complex_menu_query(session, menu_id)
    menu, submenus_count, dishes_count = updated_menu

    new_menu_data = {
        'id': str(menu),
        'title': menu_data.title,
        'description': menu_data.description,
        'submenus_count': submenus_count,
        'dishes_count': dishes_count
    }

    redis = await get_redis_connection()
    cache_key = f'menu:{menu_id}'
    await redis.set(cache_key, json.dumps(new_menu_data), ex=60)

    return new_menu_data



@router.delete('/{menu_id}')
async def delete_menu(menu_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(
        delete(Menu).where(Menu.id == menu_id)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail='menu not found')
    await session.commit()

    redis = await get_redis_connection()

    # Инициализация сканирования
    cursor = 0
    menu_keys = []

    # Перебор ключей, соответствующих шаблону
    while True:
        cursor, keys = await redis.scan(cursor, match=f'menu:{menu_id}/submenu:*', count=100)
        menu_keys.extend(keys)
        if cursor == 0:  # Если курсор вернулся в начало, завершаем цикл
            break

    # menu_keys = [key async for key in redis.scan(match=f'menu:{menu_id}/submenu:*')]
    if menu_keys:
        await redis.delete(*menu_keys)
    await redis.delete(f'menu:{menu_id}')
    await redis.delete('menus:all')

    return {'detail': 'menu deleted'}




