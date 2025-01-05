from sqlalchemy import ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class QuestionAnswer(BaseModel):
    __tablename__ = "question_answer"

    attempt_id: Mapped[str] = mapped_column(
        ForeignKey("quiz_attempt.uuid"), 
        index=True, 
        comment="Попытка",
    )
    question_id: Mapped[str] = mapped_column(
        ForeignKey("question.uuid"), 
        index=True, 
        comment="Вопрос",
    )
    options: Mapped[dict] = mapped_column(
        JSON, 
        comment="Параметры ответа",
    )

    attempt = relationship(
        "QuizAttempt", 
        back_populates="answers",
    )
    question = relationship(
        "Question", 
        back_populates="answers",
    )

    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_question_answer"),
    )
