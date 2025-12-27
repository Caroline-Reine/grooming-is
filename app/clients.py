from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models import Client
from app.schemas import ClientSearchResult, ClientRead, PetRead
from app.auth import oauth2_scheme
from jose import jwt, JWTError

SECRET_KEY = "SECRET_KEY_CHANGE_ME"
ALGORITHM = "HS256"

router = APIRouter(prefix="/clients", tags=["Clients"])


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


# 🔍 SEARCH BY PHONE
@router.get("/search/phone", response_model=ClientSearchResult)
def search_by_phone(
    phone: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    client = db.query(Client).filter(Client.phone == phone).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return {
        "client": client,
        "pets": client.pets,
    }


# 🔍 SEARCH BY NAME (partial)
@router.get("/search/name", response_model=List[ClientSearchResult])
def search_by_name(
    name: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    clients = db.query(Client).filter(
        Client.full_name.ilike(f"%{name}%")
    ).all()

    return [
        {
            "client": c,
            "pets": c.pets
        }
        for c in clients
    ]
