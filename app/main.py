from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers.router_dish import router as router_dish
from app.routers.router_submenu import router as router_submenu
from app.routers.router_menu import router as router_menu
from app.routers.complex import router as complex_query

app = FastAPI(title="Rest Menu")


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()


app.include_router(router_menu)
app.include_router(router_submenu)
app.include_router(router_dish)
app.include_router(complex_query)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Rest Menu API"}