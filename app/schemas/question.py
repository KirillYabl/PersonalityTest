from typing import ClassVar
from uuid import UUID
from pydantic import Field
from sqlalchemy.orm import Relationship

from db.tables import Question, QuestionTopic, QuestionType, Quiz
from resources.schema_constants import ServiceFields
from schemas.sqlalchemy import SQLAlchemyOutModel

class QuestionOut(SQLAlchemyOutModel):
    relationships: ClassVar[tuple[tuple[Relationship]]] = (
        (Question.quiz,),
        (Question.type,),
        (Question.topic,),
    )

    uuid: UUID = Field(..., **{ServiceFields.SORTING_FIELD: Question.uuid})
    text: str = Field(..., **{ServiceFields.SORTING_FIELD: Question.text})
    quiz_name: str = Field(..., **{ServiceFields.SORTING_FIELD: Quiz.name})
    type_name: str = Field(..., **{ServiceFields.SORTING_FIELD: QuestionType.name})
    required: bool = Field(..., **{ServiceFields.SORTING_FIELD: QuestionType.params["required"]})
    default: bool | str | int | None =  Field(None, **{ServiceFields.SORTING_FIELD: QuestionType.params["default"]})
    type_type: str =  Field(None, **{ServiceFields.SORTING_FIELD: QuestionType.params["type"]})
    min_value: int | None =  Field(None, **{ServiceFields.SORTING_FIELD: QuestionType.params["min_value"]})
    max_value: int | None =  Field(None, **{ServiceFields.SORTING_FIELD: QuestionType.params["max_value"]})
    topic_name: str = Field(..., **{ServiceFields.SORTING_FIELD: QuestionTopic.name})
    order: int = Field(..., **{ServiceFields.SORTING_FIELD: Question.order})

    @classmethod
    def from_orm(cls, model_obj: Question) -> "QuestionOut":
        return cls(
            uuid=model_obj.uuid,
            text=model_obj.text,
            quiz_name=model_obj.quiz.name,
            type_name=model_obj.type.name,
            required=model_obj.type.params.get("required"),
            default=model_obj.type.params.get("default"),
            type_type=model_obj.type.params.get("type"),
            min_value=model_obj.type.params.get("min_value"),
            max_value=model_obj.type.params.get("max_value"),
            topic_name=model_obj.topic.name,
            order=model_obj.order,
        )