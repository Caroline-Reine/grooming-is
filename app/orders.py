from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, time, date
from typing import Optional, List

from app.database import SessionLocal
from app.models import (
    Client,
    Pet,
    Master,
    Service,
    ServiceTariff,
    ExtraService,
    Order,
    OrderExtraService
)
from app.schemas import OrderCreate, OrderRead
from app.auth import oauth2_scheme
from jose import jwt, JWTError

SECRET_KEY = "SECRET_KEY_CHANGE_ME"
ALGORITHM = "HS256"

router = APIRouter(prefix="/orders", tags=["Orders"])


# =====================================================
# DB
# =====================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =====================================================
# AUTH
# =====================================================
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Not authenticated")


# =====================================================
# CREATE ORDER
# =====================================================
@router.post("", response_model=OrderRead)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # ---------- CLIENT ----------
    client = None

    if data.phone:
        client = db.query(Client).filter(Client.phone == data.phone).first()

    if not client:
        client = db.query(Client).filter(
            Client.full_name == data.full_name
        ).first()

    if not client:
        client = Client(
            full_name=data.full_name,
            phone=data.phone
        )
        db.add(client)
        db.commit()
        db.refresh(client)

    # ---------- PET ----------
    pet = db.query(Pet).filter(
        Pet.client_id == client.id,
        Pet.name == data.pet.name,
        Pet.species == data.pet.species
    ).first()

    if not pet:
        pet = Pet(
            name=data.pet.name,
            species=data.pet.species,
            breed_id=data.pet.breed_id,
            age_group_id=data.pet.age_group_id,
            size=data.pet.size,
            client_id=client.id
        )
        db.add(pet)
        db.commit()
        db.refresh(pet)

    # ---------- MASTER ----------
    master = db.query(Master).get(data.master_id)
    if not master or not master.active:
        raise HTTPException(400, "Некорректный мастер")

    # ---------- SERVICE & TARIFF ----------
    tariff = db.query(ServiceTariff).filter(
        ServiceTariff.service_id == data.service_id,
        ServiceTariff.size == pet.size
    ).first()

    if not tariff:
        raise HTTPException(400, "Нет тарифа для выбранной услуги и размера")

    start_dt = datetime.strptime(data.start_time, "%H:%M")
    end_dt = start_dt + timedelta(minutes=tariff.duration)

    if start_dt.time() < time(9, 0) or end_dt.time() > time(20, 0):
        raise HTTPException(400, "Вне рабочего времени")

    # ---------- CONFLICT CHECK ----------
    conflict = db.query(Order).filter(
        Order.master_id == master.id,
        Order.date == data.date,
        Order.start_time < end_dt.time(),
        Order.end_time > start_dt.time()
    ).first()

    if conflict:
        raise HTTPException(400, "Время занято")

    # ---------- PRICE CALCULATION ----------
    final_price = tariff.price

    # возраст
    if pet.age_group:
        final_price = int(
            final_price * pet.age_group.price_factor / 100
        )

    # доп. услуги
    extras: List[ExtraService] = []
    if data.extra_service_ids:
        extras = db.query(ExtraService).filter(
            ExtraService.id.in_(data.extra_service_ids)
        ).all()

        final_price += sum(e.price for e in extras)

    # ---------- CREATE ORDER ----------
    order = Order(
        client_id=client.id,
        pet_id=pet.id,
        master_id=master.id,
        service_id=data.service_id,
        price=data.price or final_price,
        date=data.date,
        start_time=start_dt.time(),
        end_time=end_dt.time(),
        comment=data.comment
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    # ---------- LINK EXTRA SERVICES ----------
    for extra in extras:
        db.add(OrderExtraService(
            order_id=order.id,
            extra_service_id=extra.id
        ))

    db.commit()

    service = db.query(Service).get(data.service_id)

    return {
        "id": order.id,
        "date": order.date,
        "start_time": order.start_time.strftime("%H:%M"),
        "end_time": order.end_time.strftime("%H:%M"),
        "price": order.price,
        "status": order.status,
        "client_name": client.full_name,
        "pet_name": pet.name,
        "service_name": service.name,
        "master_name": master.name
    }


# =====================================================
# GET ORDERS FOR SCHEDULE
# =====================================================
@router.get("/schedule", response_model=list[OrderRead])
def get_orders_for_schedule(
    date_from: date = Query(...),
    date_to: date = Query(...),
    master_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    q = db.query(Order).filter(
        Order.date >= date_from,
        Order.date <= date_to
    )

    if master_id:
        q = q.filter(Order.master_id == master_id)

    orders = q.all()
    result = []

    for o in orders:
        result.append({
            "id": o.id,
            "date": o.date,
            "start_time": o.start_time.strftime("%H:%M"),
            "end_time": o.end_time.strftime("%H:%M"),
            "price": o.price,
            "status": o.status,
            "client_name": o.client.full_name,
            "pet_name": o.pet.name,
            "service_name": o.service.name,
            "master_name": o.master.name
        })

    return result
