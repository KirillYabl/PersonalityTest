from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class QuizAttempt(BaseModel):
    __tablename__ = "quiz_attempt"

    quiz_id: Mapped[str | None] = mapped_column(
        ForeignKey("quiz.uuid"), 
        nullable=True, 
        index=True, 
        comment="Тест",
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("user.uuid"), 
        index=True, 
        comment="Пользователь",
    )

    quiz = relationship(
        "Quiz", 
        back_populates="attempts",
    )
    user = relationship(
        "User", 
        back_populates="attempts",
    )
    answers = relationship(
        "QuestionAnswer", 
        back_populates="attempt", 
        cascade="all, delete",
    )
