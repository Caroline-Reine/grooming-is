from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.database import SessionLocal
from app.models import Pet
from app.schemas import PetRead
from app.auth import oauth2_scheme

SECRET_KEY = "SECRET_KEY_CHANGE_ME"
ALGORITHM = "HS256"

router = APIRouter(prefix="/pets", tags=["Pets"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Not authenticated")


# 🔍 Получить всех питомцев (для справки / отладки)
@router.get("", response_model=list[PetRead])
def get_pets(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return db.query(Pet).all()


# 🔍 Получить питомцев конкретного клиента
@router.get("/by-client/{client_id}", response_model=list[PetRead])
def get_pets_by_client(
    client_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return db.query(Pet).filter(Pet.client_id == client_id).all()
