from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from utils.timeutils import tz_now

constraint_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=constraint_convention)


class BaseModel(DeclarativeBase):
    __abstract__ = True
    metadata = metadata

    uuid: Mapped[UUID] = mapped_column(
        default=uuid4,
        primary_key=True,
        unique=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=tz_now,
        comment="Создано",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=tz_now,
        onupdate=tz_now,
        comment="Обновлено",
    )
