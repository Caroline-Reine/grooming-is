from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.database import SessionLocal
from app.models import Master
from app.auth import oauth2_scheme

SECRET_KEY = "SECRET_KEY_CHANGE_ME"
ALGORITHM = "HS256"

router = APIRouter(prefix="/masters", tags=["Masters"])


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


@router.get("")
def get_masters(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Получить список активных мастеров
    """
    return db.query(Master).filter(Master.active == True).all()
