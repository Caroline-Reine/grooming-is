from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Service
from app.auth import get_current_user

router = APIRouter(prefix="/services", tags=["Services"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def get_services(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    services = db.query(Service).all()

    return [
        {
            "id": s.id,
            "name": s.name,
        }
        for s in services
    ]
