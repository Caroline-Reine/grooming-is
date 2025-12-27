from app.database import SessionLocal
from app.models import (
    User, Master, Service, ServiceTariff, ExtraService,
    Breed, AgeGroup,
    UserRole, PetSize
)
from app.auth import hash_password


def init_data():
    db = SessionLocal()

    # ---------- ЗАЩИТА ОТ ПОВТОРНОЙ ИНИЦИАЛИЗАЦИИ ----------
    if db.query(User).first():
        db.close()
        return

    # ================= USERS =================
    users = [
        User(login="admin1", password=hash_password("admin123"), role=UserRole.admin),
        User(login="admin2", password=hash_password("admin123"), role=UserRole.admin),
        User(login="manager", password=hash_password("manager123"), role=UserRole.manager),
    ]
    db.add_all(users)

    # ================= MASTERS (2/2) =================
    masters = [
        Master(name="Анна", group="A"),
        Master(name="Ольга", group="A"),
        Master(name="Ирина", group="B"),
        Master(name="Мария", group="B"),
    ]
    db.add_all(masters)

    # ================= AGE GROUPS =================
    age_groups = [
        AgeGroup(name="Щенок", price_factor=90),
        AgeGroup(name="Взрослый", price_factor=100),
        AgeGroup(name="Пожилой", price_factor=110),
    ]
    db.add_all(age_groups)

    # ================= BREEDS =================
    breeds = [
        # декоративные
        Breed(name="Йоркширский терьер", default_size=PetSize.decorative),
        Breed(name="Мальтезе", default_size=PetSize.decorative),
        Breed(name="Шпиц померанский", default_size=PetSize.decorative),
        Breed(name="Чихуахуа", default_size=PetSize.decorative),
        Breed(name="Той-терьер", default_size=PetSize.decorative),
        Breed(name="Китайская хохлатая", default_size=PetSize.decorative),

        # средние
        Breed(name="Мопс", default_size=PetSize.medium),
        Breed(name="Французский бульдог", default_size=PetSize.medium),
        Breed(name="Корги", default_size=PetSize.medium),
        Breed(name="Сиба-ину", default_size=PetSize.medium),
        Breed(name="Бигль", default_size=PetSize.medium),

        # крупные
        Breed(name="Лабрадор", default_size=PetSize.large),
        Breed(name="Хаски", default_size=PetSize.large),
        Breed(name="Немецкая овчарка", default_size=PetSize.large),
        Breed(name="Золотистый ретривер", default_size=PetSize.large),

        # очень крупные
        Breed(name="Сенбернар", default_size=PetSize.extra_large),
        Breed(name="Алабай", default_size=PetSize.extra_large),
        Breed(name="Ньюфаундленд", default_size=PetSize.extra_large),

        # беспородные
        Breed(name="Беспородная (мелкая)", default_size=PetSize.decorative),
        Breed(name="Беспородная (средняя)", default_size=PetSize.medium),
        Breed(name="Беспородная (крупная)", default_size=PetSize.large),
    ]
    db.add_all(breeds)

    # ================= SERVICES =================
    services = {
        "Комплексный уход": Service(name="Комплексный уход"),
        "Гигиенический уход": Service(name="Гигиенический уход"),
        "Тримминг": Service(name="Тримминг"),
        "Стрижка": Service(name="Стрижка"),
        "Экспресс-линька": Service(name="Экспресс-линька"),
    }
    db.add_all(services.values())
    db.flush()

    # ================= TARIFFS =================
    tariffs = [
        # декоративные
        ServiceTariff(services["Комплексный уход"].id, PetSize.decorative, 2000, 90),
        ServiceTariff(services["Гигиенический уход"].id, PetSize.decorative, 1300, 60),
        ServiceTariff(services["Тримминг"].id, PetSize.decorative, 2600, 90),
        ServiceTariff(services["Стрижка"].id, PetSize.decorative, 2200, 90),

        # средние
        ServiceTariff(services["Комплексный уход"].id, PetSize.medium, 2900, 120),
        ServiceTariff(services["Гигиенический уход"].id, PetSize.medium, 2000, 90),
        ServiceTariff(services["Тримминг"].id, PetSize.medium, 3000, 120),
        ServiceTariff(services["Стрижка"].id, PetSize.medium, 2500, 120),

        # крупные
        ServiceTariff(services["Комплексный уход"].id, PetSize.large, 4200, 150),
        ServiceTariff(services["Гигиенический уход"].id, PetSize.large, 3200, 120),
        ServiceTariff(services["Тримминг"].id, PetSize.large, 4900, 180),
        ServiceTariff(services["Стрижка"].id, PetSize.large, 4300, 150),

        # очень крупные
        ServiceTariff(services["Комплексный уход"].id, PetSize.extra_large, 5500, 180),
        ServiceTariff(services["Гигиенический уход"].id, PetSize.extra_large, 4700, 150),
        ServiceTariff(services["Тримминг"].id, PetSize.extra_large, 8000, 210),
        ServiceTariff(services["Стрижка"].id, PetSize.extra_large, 5500, 180),
    ]
    db.add_all(tariffs)

    # ================= EXTRA SERVICES =================
    extras = [
        ExtraService(name="Окрашивание шерсти", price=500),
        ExtraService(name="Выбривание узора", price=200),
        ExtraService(name="Стрижка когтей с подпиливанием", price=300),
        ExtraService(name="Вычес шерсти (1 час)", price=400),
        ExtraService(name="Доплата за агрессивность", price=500),
        ExtraService(name="Сухой уход для щенков до 3 месяцев", price=500),
    ]
    db.add_all(extras)

    db.commit()
    db.close()
