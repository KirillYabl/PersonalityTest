from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class QuizResult(BaseModel):
    __tablename__ = "quiz_result"

    attempt_id: Mapped[str] = mapped_column(
        ForeignKey("quiz_attempt.uuid"), 
        index=True, 
        unique=True,
        comment="Попытка прохождения",
    )

    data: Mapped[dict] = mapped_column(
        JSON, 
        comment="Результаты, тут нельзя выделить структуру, специфично в завиимости от теста",
    )

    attempt = relationship(
        "QuizAttempt", 
        back_populates="result",
    )
