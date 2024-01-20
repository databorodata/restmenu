import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.schemas import MenuModel
from app.models import Menu

router = APIRouter(
    prefix="/api/v1/menus",
    tags=["menu"]
)

'''
Задача:
Посмотреть список меню
путь:
{{LOCAL_URL}}/api/v1/menus
пример ответа:
[
    {
        "id": "a2eb416c-2245-4526-bb4b-6343d5c5016f",
        "title": "My menu 1",
        "description": "My menu description 1",
        "submenus_count": 0,
        "dishes_count": 0
    }
]
'''

@router.get("/")
async def get_list_menu(session: AsyncSession = Depends(get_async_session)):
    query = select(Menu)
    res = await session.execute(query)
    result_orm = res.scalars().all()
    print(result_orm)
    result_dto = [MenuModel.model_validate(row, from_attributes=True) for row in result_orm]
    print(result_dto)
    return result_dto


'''
Задача:
Посмотреть определенное меню
путь:
{{LOCAL_URL}}/api/v1/menus/{{api_test_menu_id}}
пример ответа:
{
    "id": "a2eb416c-2245-4526-bb4b-6343d5c5016f",
    "title": "My menu 1",
    "description": "My menu description 1",
    "submenus_count": 0,
    "dishes_count": 0
}

или 

{
    "detail": "menu not found"
}
'''


@router.get("/{api_test_menu_id}")
async def get_menu(api_test_menu_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
        query = select(Menu).filter_by(id=api_test_menu_id)
        print(query)
        result = await session.execute(query)
        result_orm = result.scalars().one_or_none()
        if result_orm is not None:
            print(result_orm)
            result_dto = MenuModel.model_validate(result_orm, from_attributes=True)
            print(result_dto)
            return result_dto
        else:
            raise HTTPException(status_code=404, detail="menu not found")




'''
Задача:
Создать меню
путь:
{{LOCAL_URL}}/api/v1/menus
пример ответа:
{
    "id": "9a5bce5f-4462-4d12-a66c-d59584b19ee8",
    "title": "My menu 1",
    "description": "My menu description 1",
    "submenus_count": 0,
    "dishes_count": 0
}
'''

@router.post("/")
async def create_menu(new_menu: MenuModel, session: AsyncSession = Depends(get_async_session)):
    stmt = insert(Menu).values(**new_menu.model_dump())
    await session.execute(stmt)
    await session.commit()
    # return new_menu
    # return {"status": "success"}


'''
Задача:
Обновить определенное меню
путь:
{{LOCAL_URL}}/api/v1/menus/{{api_test_menu_id}}
пример ответа:
{
    "id": "a2eb416c-2245-4526-bb4b-6343d5c5016f",
    "title": "My updated menu 1",
    "description": "My updated menu description 1",
    "submenus_count": 0,
    "dishes_count": 0
}

или 

{
    "detail": "menu not found"
}
'''


# @router.patch("/{api_test_menu_id}")
# async def update_menu(
#         api_test_menu_id: uuid.UUID,
#         up_menu: CreateMenu,
#         session: AsyncSession = Depends(get_async_session)
# ):
#     try:
#         stmt = update(menu).filter_by(id=api_test_menu_id).values(**up_menu.model_dump())
#         await session.execute(stmt)
#         await session.commit()
#         return {"status": "success", **up_menu.model_dump()}
#     except:
#         return {"detail": "menu not found"}

@router.patch("/{api_test_menu_id}")
async def update_menu(
        api_test_menu_id: uuid.UUID,
        up_menu: MenuModel,
        session: AsyncSession = Depends(get_async_session)
):
    query = select(Menu).filter_by(id=api_test_menu_id)
    result = await session.execute(query)
    result_orm = result.scalars().one_or_none()
    if result_orm is not None:
        stmt = update(Menu).filter_by(id=api_test_menu_id).values(**up_menu.model_dump())
        await session.execute(stmt)
        await session.commit()
        # return up_menu
    else:
        raise HTTPException(status_code=404, detail="menu not found")







'''
Задача:
Удалить меню
путь:
{{LOCAL_URL}}/api/v1/menus/{{api_test_menu_id}}
пример ответа:
{
    "status": true,
    "message": "The menu has been deleted"
}
'''

# @router.delete("/{api_test_menu_id}")
# async def delete_menu(api_test_menu_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
#     try:
#         stmt = delete(menu).filter_by(id=api_test_menu_id)
#         await session.execute(stmt)
#         await session.commit()
#         return {"status": "success", "message": "The menu has been deleted"}
#     except:
#         return {"detail": "menu not found"}


@router.delete("/{api_test_menu_id}")
async def delete_menu(api_test_menu_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    query = select(Menu).filter_by(id=api_test_menu_id)
    result = await session.execute(query)
    result_orm = result.scalars().one_or_none()
    if result_orm is not None:
        stmt = delete(Menu).filter_by(id=api_test_menu_id)
        await session.execute(stmt)
        await session.commit()
    else:
        raise HTTPException(status_code=404, detail="menu not found")





    # try:
    #     stmt = delete(menu).filter_by(id=api_test_menu_id)
    #     await session.execute(stmt)
    #     await session.commit()
    #     return {"status": "success", "message": "The menu has been deleted"}
    # except:
    #     return {"detail": "menu not found"}


'''    
Инструкция по работе с постман (см. доп. материалы):
Нажимаем import (1 на скрине) и переносим 2 прикрепленных выше файла в окно 
постман. Один файл - коллекция тестов, второй - переменные окружения. 
В диалоговом окне подтверждаем импорт. После этого должна появиться коллекция (подчернута на скрине) menu app.
Выбираем переменные окружения (2 на скрине) из выпадающего списка
После этого можем зайти в коллекцию menu app и запустить каждый тест вручную. 

Для этого открываем коллекцию menu app, выбираем 
Тестовый сценарий -> CRUD для меню -> Просматривает список меню(или любой другой) у 
нас в центральной части появляется запрос, нажимаем Send и запрос летит в наше приложение.
Если хотим запустит сразу всю коллекцию тестов, т
о жмем на три точки (3 на скрине) рядом с коллекцией и выбираем Run.'''