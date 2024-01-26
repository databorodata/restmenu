from fastapi import FastAPI
# from contextlib import asynccontextmanager

from app.database import create_db_and_tables
from app.routers.router_dish import router as router_dish
from app.routers.router_submenu import router as router_submenu
from app.routers.router_menu import router as router_menu

app = FastAPI(title="Rest Menu")


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await create_db_and_tables()
# https://github.com/tiangolo/fastapi/releases/tag/0.93.0
# app = FastAPI(lifespan=lifespan)

app.include_router(router_menu)
app.include_router(router_submenu)
app.include_router(router_dish)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Rest Menu API"}