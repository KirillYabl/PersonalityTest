from sqlalchemy import Text, Integer, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

class Question(BaseModel):
    __tablename__ = "question"

    text: Mapped[str] = mapped_column(
        Text, 
        comment="Текст вопроса",
    )
    quiz_id: Mapped[str] = mapped_column(
        ForeignKey("quiz.uuid"), 
        index=True, 
        comment="Тест",
    )
    type_id: Mapped[str] = mapped_column(
        ForeignKey("question_type.uuid"), 
        index=True, 
        comment="Тип вопроса",
    )
    topic_id: Mapped[str] = mapped_column(
        ForeignKey("question_topic.uuid"), 
        index=True, 
        comment="Тема вопроса",
    )
    order: Mapped[int] = mapped_column(
        Integer, 
        default=0, 
        index=True, 
        comment="Порядок вопроса",
    )
    active: Mapped[bool] = mapped_column(
        Boolean, 
        index=True, 
        comment="Признак активности вопроса",
    )

    quiz = relationship(
        "Quiz", 
        back_populates="questions",
    )
    type = relationship(
        "QuestionType", 
        back_populates="questions",
    )
    topic = relationship(
        "QuestionTopic", 
        back_populates="questions",
    )
    answers = relationship(
        "QuestionAnswer", 
        back_populates="question", 
        cascade="all, delete",
    )

    __table_args__ = (
        UniqueConstraint("text", "quiz_id", name="uq_question"),
    )
