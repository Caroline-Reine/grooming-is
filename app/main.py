from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import Base, engine
from app.auth import router as auth_router
from app.clients import router as clients_router
from app.pets import router as pets_router
from app.orders import router as orders_router
from app.init_data import init_all
from app.masters import router as masters_router
from app.services import router as services_router
from app.breeds import router as breeds_router


Base.metadata.create_all(bind=engine)
init_all()

app = FastAPI(title="Grooming IS")

from fastapi.responses import FileResponse

@app.get("/login.html")
def login_page():
    return FileResponse("static/login.html")

@app.get("/")
def read_index():
    return FileResponse("static/index.html")


# 🔹 ПОДКЛЮЧАЕМ ФРОНТ
app.mount("/static", StaticFiles(directory="static"), name="static")


# 🔹 API
app.include_router(auth_router)
app.include_router(clients_router)
app.include_router(pets_router)
app.include_router(orders_router)
app.include_router(masters_router)
app.include_router(services_router)
app.include_router(breeds_router)
