from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.tables.base import BaseModel


class Quiz(BaseModel):
    # TODO: materialized path
    __tablename__ = "quiz"

    name: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        index=True,
        comment="Название теста",
    )
    parent_id: Mapped[str | None] = mapped_column(
        ForeignKey("quiz.uuid"),
        nullable=True,
        comment="Родительский тест",
    )
    active: Mapped[bool] = mapped_column(
        Boolean,
        index=True,
        comment="Признак активности теста",
    )
    type_id: Mapped[str | None] = mapped_column(
        ForeignKey("quiz_type.uuid"),
        nullable=True,
        unique=True,
        comment="Тип теста",
    )

    parent = relationship(
        "Quiz",
        remote_side="Quiz.uuid",
    )
    questions = relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete",
    )
    attempts = relationship(
        "QuizAttempt",
        back_populates="quiz",
        cascade="all, delete",
    )
    type = relationship(
        "QuizType",
        back_populates="quiz",
        uselist=False,
    )
