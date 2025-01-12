from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class User(BaseModel):
    __tablename__ = "user"

    tg_user_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        index=True,
        comment="ID пользователя в TG",
    )
    tg_username: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        index=True,
        comment="Username в TG",
    )

    attempts = relationship(
        "QuizAttempt",
        back_populates="user",
        cascade="all, delete",
    )
