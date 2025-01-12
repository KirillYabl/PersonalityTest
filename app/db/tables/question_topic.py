from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class QuestionTopic(BaseModel):
    __tablename__ = "question_topic"

    name: Mapped[str] = mapped_column(
        String(100),
        comment="Тема вопроса",
    )

    questions = relationship(
        "Question",
        back_populates="topic",
        cascade="all, delete",
    )
