from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.auth import router as auth_router
from app.clients import router as clients_router
from app.pets import router as pets_router
from app.orders import router as orders_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Grooming IS")

# 🔹 ПОДКЛЮЧАЕМ ФРОНТ
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# 🔹 API
app.include_router(auth_router)
app.include_router(clients_router)
app.include_router(pets_router)
app.include_router(orders_router)
