from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db.tables.base import BaseModel


class TestCar(BaseModel):
    """Таблица машина для тестов.

    Нужна для тестирования репозиториев, в отрыве от схемы приложения.
    """

    __tablename__ = "test_car"

    name: Mapped[str] = mapped_column(
        String(100),
        comment="Имя машины",
        unique=True,
    )
