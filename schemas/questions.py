from typing import ClassVar
from uuid import UUID
from pydantic import BaseModel

from db.tables import Question, Quiz, QuestionType, QuestionTopic
from db.tables.base import BaseModel as SQLBaseModel
from schemas.sqlalchemy import SQLAlchemyModel

class QuestionOut(BaseModel, SQLAlchemyModel):
    joinedload_models: ClassVar[tuple[SQLBaseModel]] = (Quiz, QuestionType, QuestionTopic)

    uuid: UUID
    text: str
    quiz_name: str
    type_name: str
    required: bool
    default: bool | str | int | None = None
    type_type: str
    min_value: int | None = None
    max_value: int | None = None
    topic_name: str
    order: int

    @classmethod
    def from_orm(cls, question: Question) -> "QuestionOut":
        return cls(
            uuid=question.uuid,
            text=question.text,
            quiz_name=question.quiz.name,
            type_name=question.type.name,
            required=question.type.params.get("required"),
            default=question.type.params.get("default"),
            type_type=question.type.params.get("type"),
            min_value=question.type.params.get("min_value"),
            max_value=question.type.params.get("max_value"),
            topic_name=question.topic.name,
            order=question.order,
        )