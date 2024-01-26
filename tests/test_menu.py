import pytest
import pytest_asyncio

# from fixtures import create_test_database, db_session, client, TEST_DB_URL
from httpx import AsyncClient
from app.main import app
from tests.conftest import init_db, client, TEST_DB_URL


@pytest.mark.usefixtures("init_db")
class TestMenuAPI:
    menu_id = None

    @pytest.mark.asyncio
    async def test_1_get_menus_empty(self, client: AsyncClient):
        # async with AsyncClient(app=app, base_url="http://test") as client:
        #     yield client
        print(f"!!!!!!{TEST_DB_URL=}!!!!!!")
        print(')))))))))))))))))))))))))))))))')
        response = await client.get("/api/v1/menus/")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_2_create_menu(self, client: AsyncClient):
        # async with AsyncClient(app=app, base_url='http://test') as client:
        #     yield client
        data = {"title": "Test Menu", "description": "Test Description"}
        response = await client.post("/api/v1/menus/", json=data)
        print('#############', response, '^^^^^^^^^^^^^^^^^^')
        assert response.status_code == 201
        print('&&&&&&&&&&&&&&&')
        print(response.json())
        print('&&&&&&&&&&&&&&&')
        TestMenuAPI.menu_id = response.json()["id"]

    @pytest.mark.asyncio
    async def test_3_get_all_menus(self, client: AsyncClient):
        response = await client.get("/api/v1/menus/")
        assert response.status_code == 200
        assert TestMenuAPI.menu_id in [menu["id"] for menu in response.json()]

    @pytest.mark.asyncio
    async def test_4_get_specific_menu(self, client: AsyncClient):
        response = await client.get(f"/api/v1/menus/{TestMenuAPI.menu_id}")
        assert response.status_code == 200
        assert response.json()["id"] == TestMenuAPI.menu_id

    @pytest.mark.asyncio
    async def test_5_update_menu(self, client: AsyncClient):
        update_data = {"title": "Updated Test Menu", "description": "Updated Description"}
        response = await client.patch(f"/api/v1/menus/{TestMenuAPI.menu_id}", json=update_data)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_6_get_specific_menu_after_update(self, client: AsyncClient):
        response = await client.get(f"/api/v1/menus/{TestMenuAPI.menu_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Test Menu"

    @pytest.mark.asyncio
    async def test_7_delete_menu(self, client: AsyncClient):
        response = await client.delete(f"/api/v1/menus/{TestMenuAPI.menu_id}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_8_get_menus_empty_after_delete(self, client: AsyncClient):
        response = await client.get("/api/v1/menus/")
        assert response.status_code == 200
        assert TestMenuAPI.menu_id not in [menu["id"] for menu in response.json()]
