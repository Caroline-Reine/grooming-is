from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from app.models import PetSize, OrderStatus


# ---------- CLIENT ----------

class ClientRead(BaseModel):
    id: int
    full_name: str
    phone: Optional[str]

    class Config:
        from_attributes = True


# ---------- PET ----------

class PetInput(BaseModel):
    name: str
    species: str
    breed: Optional[str]
    size: PetSize


class PetRead(BaseModel):
    id: int
    name: str
    species: str
    breed: Optional[str]
    size: PetSize

    class Config:
        from_attributes = True


# ---------- SEARCH ----------

class ClientSearchResult(BaseModel):
    client: ClientRead
    pets: List[PetRead]


# ---------- ORDER ----------

class OrderCreate(BaseModel):
    phone: Optional[str]
    full_name: str

    pet: PetInput

    master_id: int
    service_id: int

    date: date
    start_time: str  # HH:MM

    extra_service_ids: Optional[list[int]] = []

    price: Optional[int]
    comment: Optional[str]



class OrderRead(BaseModel):
    id: int
    date: date
    start_time: str
    end_time: str
    price: int
    status: OrderStatus

    client_name: str
    pet_name: str
    service_name: str
    master_name: str

    class Config:
        from_attributes = True

# ---------- EXTRA SERVICES ----------

class ExtraServiceRead(BaseModel):
    id: int
    name: str
    price: int

    class Config:
        from_attributes = True
