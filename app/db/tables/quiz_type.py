from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class QuizType(BaseModel):
    __tablename__ = "quiz_type"

    name: Mapped[str] = mapped_column(
        String(100),
        comment="Название типа теста",
        unique=True,
    )

    quiz = relationship(
        "Quiz",
        back_populates="type",
    )
