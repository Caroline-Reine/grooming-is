from fastapi import FastAPI
from app.database import Base, engine
from app.models import User

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Grooming IS")

@app.get("/")
def root():
    return {"status": "OK", "message": "Сервис работает"}
