from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.tables.base import BaseModel


class TestCar(BaseModel):
    """Таблица машина для тестов.

    Нужна для тестирования репозиториев, в отрыве от схемы приложения.
    Импортировать в __init__ не нужно.
    """

    __tablename__ = "test_car"

    name: Mapped[str] = mapped_column(
        String(100),
        comment="Имя машины",
        unique=True,
    )
    brand_uuid: Mapped[str] = mapped_column(
        ForeignKey("test_brand.uuid"),
        comment="Бренд",
    )

    brand = relationship(
        "TestBrand",
        back_populates="cars",
        uselist=False,
    )


class TestBrand(BaseModel):
    """Таблица марка машины для тестов.

    Нужна для тестирования репозиториев, в отрыве от схемы приложения.
    Импортировать в __init__ не нужно.
    """

    __tablename__ = "test_brand"

    name: Mapped[str] = mapped_column(
        String(100),
        comment="Имя марки",
        unique=True,
    )

    cars = relationship(
        "TestCar",
        back_populates="brand",
    )
