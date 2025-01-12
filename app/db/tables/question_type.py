from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class QuestionType(BaseModel):
    __tablename__ = "question_type"

    name: Mapped[str] = mapped_column(
        String(200),
        comment="Название типа вопроса",
    )
    params: Mapped[dict] = mapped_column(
        JSON,
        comment="Параметры типа вопроса",
    )

    questions = relationship(
        "Question",
        back_populates="type",
        cascade="all, delete",
    )
