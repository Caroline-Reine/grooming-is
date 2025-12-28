from sqlalchemy import (
    Column, Integer, String, Boolean,
    ForeignKey, Date, Time, Enum
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


# ===================== ENUMS =====================

class UserRole(str, enum.Enum):
    admin = "admin"
    master = "master"
    manager = "manager"


class OrderStatus(str, enum.Enum):
    planned = "Запланирована"
    done = "Выполнена"
    canceled = "Отменена"


class PetSize(str, enum.Enum):
    decorative = "Декоративный"
    medium = "Средний"
    large = "Крупный"
    extra_large = "Очень крупный"


# ===================== USERS =====================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    active = Column(Boolean, default=True)


# ===================== MASTERS =====================

class Master(Base):
    __tablename__ = "masters"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    group = Column(String, nullable=False)  # A / B
    active = Column(Boolean, default=True)


# ===================== SERVICES =====================

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class ServiceTariff(Base):
    __tablename__ = "service_tariffs"

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    size = Column(Enum(PetSize), nullable=False)

    price = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)  # minutes

    service = relationship("Service")


class ExtraService(Base):
    __tablename__ = "extra_services"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)


# ===================== AGE GROUPS =====================

class AgeGroup(Base):
    __tablename__ = "age_groups"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    # процент от базовой цены (90 / 100 / 110)
    price_factor = Column(Integer, nullable=False)


# ===================== BREEDS =====================

class Breed(Base):
    __tablename__ = "breeds"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)  # dog / cat

    # если None — размер выбирается вручную (дворняжки)
    default_size = Column(Enum(PetSize), nullable=True)


# ===================== CLIENTS & PETS =====================

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)

    pets = relationship("Pet", back_populates="client")


class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    species = Column(String, nullable=False)

    breed_id = Column(Integer, ForeignKey("breeds.id"), nullable=True)
    age_group_id = Column(Integer, ForeignKey("age_groups.id"), nullable=False)

    size = Column(Enum(PetSize), nullable=False)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)

    client = relationship("Client", back_populates="pets")
    breed = relationship("Breed")
    age_group = relationship("AgeGroup")


# ===================== ORDERS =====================

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    master_id = Column(Integer, ForeignKey("masters.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    price = Column(Integer, nullable=False)

    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    status = Column(Enum(OrderStatus), default=OrderStatus.planned)
    comment = Column(String, nullable=True)


# -------- ORDER <-> EXTRA SERVICES --------

class OrderExtraService(Base):
    __tablename__ = "order_extra_services"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    extra_service_id = Column(Integer, ForeignKey("extra_services.id"))

    order = relationship("Order", backref="extra_services")
    extra_service = relationship("ExtraService")
