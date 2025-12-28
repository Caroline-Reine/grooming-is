from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import (
    User,
    Master,
    Breed,
    AgeGroup,
    Service,
    ServiceTariff,
    ExtraService
)

from app.auth import get_password_hash


# =====================================================
# HELPERS
# =====================================================
def get_db() -> Session:
    return SessionLocal()


def exists(db: Session, model, **kwargs) -> bool:
    return db.query(model).filter_by(**kwargs).first() is not None


# =====================================================
# USERS
# =====================================================
def init_users(db: Session):
    users = [
        # Администраторы
        ("admin1", "admin123", "admin", "Иванова Светлана Васильевна"),
        ("admin2", "admin123", "admin", "Петрова Анна Сергеевна"),

        # Руководитель
        ("manager", "manager123", "manager", "Смирнова Ольга Николаевна"),

        # Мастера
        ("master1", "master123", "master", "Иванов Дмитрий Андреевич"),
        ("master2", "master123", "master", "Кузнецова Мария Викторовна"),
        ("master3", "master123", "master", "Соколова Елена Игоревна"),
        ("master4", "master123", "master", "Попов Алексей Сергеевич"),
    ]

    for login, password, role, full_name in users:
        if exists(db, User, login=login):
            continue

        db.add(User(
            login=login,
            password=get_password_hash(password),
            role=role,
            full_name=full_name,
            active=True
        ))

    db.commit()


# =====================================================
# MASTERS
# =====================================================
def init_masters(db: Session):
    masters = [
        ("Иванов Дмитрий Андреевич", "A"),
        ("Кузнецова Мария Викторовна", "A"),
        ("Соколова Елена Игоревна", "B"),
        ("Попов Алексей Сергеевич", "B"),
    ]

    for name, group in masters:
        if exists(db, Master, name=name):
            continue

        db.add(Master(
            name=name,
            group=group,
            active=True
        ))

    db.commit()


# =====================================================
# AGE GROUPS
# =====================================================
def init_age_groups(db: Session):
    groups = [
        ("Щенок / Котёнок", 90),
        ("Взрослый", 100),
        ("Пожилой", 110),
    ]

    for name, factor in groups:
        if exists(db, AgeGroup, name=name):
            continue

        db.add(AgeGroup(
            name=name,
            price_factor=factor
        ))

    db.commit()


# =====================================================
# BREEDS
# =====================================================
def init_breeds(db: Session):
    dog_breeds = [
        # декоративные
        ("Чихуахуа", "dog", "decorative"),
        ("Йоркширский терьер", "dog", "decorative"),
        ("Мальтийская болонка", "dog", "decorative"),
        ("Померанский шпиц", "dog", "decorative"),
        ("Русский той", "dog", "decorative"),

        # средние
        ("Французский бульдог", "dog", "medium"),
        ("Бигль", "dog", "medium"),
        ("Ши-тцу", "dog", "medium"),
        ("Вельш-корги", "dog", "medium"),

        # крупные
        ("Лабрадор ретривер", "dog", "large"),
        ("Голден ретривер", "dog", "large"),
        ("Немецкая овчарка", "dog", "large"),
        ("Хаски", "dog", "large"),

        # очень крупные
        ("Сенбернар", "dog", "extra_large"),
        ("Алабай", "dog", "extra_large"),

        # дворняжка
        ("Дворняжка", "dog", None),
    ]

    cat_breeds = [
        ("Британская короткошерстная", "cat", "medium"),
        ("Сиамская", "cat", "medium"),
        ("Мейн-кун", "cat", "extra_large"),
        ("Норвежская лесная", "cat", "large"),
        ("Сфинкс", "cat", "medium"),
    ]

    for name, species, size in dog_breeds + cat_breeds:
        if exists(db, Breed, name=name, species=species):
            continue

        db.add(Breed(
            name=name,
            species=species,
            default_size=size
        ))

    db.commit()


# =====================================================
# SERVICES
# =====================================================
def init_services(db: Session):
    services = [
        "Комплексный уход",
        "Гигиенический уход",
        "Тримминг",
        "Стрижка",
        "Экспресс-линька",
    ]

    for name in services:
        if exists(db, Service, name=name):
            continue

        db.add(Service(name=name))

    db.commit()


# =====================================================
# SERVICE TARIFFS
# =====================================================
def init_tariffs(db: Session):
    service_map = {
        s.name: s.id for s in db.query(Service).all()
    }

    tariffs = [
        # decorative
        ("Комплексный уход", "decorative", 2000, 90),
        ("Гигиенический уход", "decorative", 1300, 60),
        ("Тримминг", "decorative", 2600, 90),
        ("Стрижка", "decorative", 2200, 90),

        # medium
        ("Комплексный уход", "medium", 2900, 120),
        ("Гигиенический уход", "medium", 2000, 90),
        ("Тримминг", "medium", 3000, 120),
        ("Стрижка", "medium", 2500, 120),

        # large
        ("Комплексный уход", "large", 4200, 180),
        ("Гигиенический уход", "large", 3200, 120),
        ("Тримминг", "large", 4900, 180),
        ("Стрижка", "large", 4300, 150),

        # extra_large
        ("Комплексный уход", "extra_large", 5500, 210),
        ("Гигиенический уход", "extra_large", 4700, 150),
        ("Тримминг", "extra_large", 8000, 210),
        ("Стрижка", "extra_large", 8000, 210),
    ]

    for service_name, size, price, duration in tariffs:
        service_id = service_map.get(service_name)
        if not service_id:
            continue

        if exists(db, ServiceTariff,
                  service_id=service_id,
                  size=size):
            continue

        db.add(ServiceTariff(
            service_id=service_id,
            size=size,
            price=price,
            duration=duration
        ))

    db.commit()


# =====================================================
# EXTRA SERVICES
# =====================================================
def init_extra_services(db: Session):
    extras = [
        ("Окрашивание шерсти", 500),
        ("Выбривание узора под машинку", 200),
        ("Стрижка когтей с подпиливанием", 300),
        ("Вычес шерсти, устранение колтунов (1 час)", 400),
        ("Доплата за агрессивность питомца", 500),
        ("Сухой уход для щенков/котят до 3 месяцев", 500),
    ]

    for name, price in extras:
        if exists(db, ExtraService, name=name):
            continue

        db.add(ExtraService(
            name=name,
            price=price
        ))

    db.commit()


# =====================================================
# MAIN ENTRY
# =====================================================
def init_all():
    db = get_db()

    init_users(db)
    init_masters(db)
    init_age_groups(db)
    init_breeds(db)
    init_services(db)
    init_tariffs(db)
    init_extra_services(db)

    db.close()
