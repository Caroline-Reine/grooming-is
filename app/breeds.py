from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Breed
from app.auth import get_current_user

router = APIRouter(prefix="/breeds", tags=["Breeds"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def get_breeds(
    species: str = Query(..., description="dog или cat"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    breeds = db.query(Breed).filter(Breed.species == species).all()

    return [
        {
            "id": b.id,
            "name": b.name,
            "default_size": b.default_size,
        }
        for b in breeds
    ]
