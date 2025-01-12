from typing import ClassVar
from uuid import UUID

from pydantic import Field
from sqlalchemy.orm import Relationship

from db.tables import QuestionAnswer
from resources.schema_constants import ServiceFields
from schemas.sqlalchemy import SQLAlchemyOutModel


class QuestionAnswerQuestionIdValueOut(SQLAlchemyOutModel):
    relationships: ClassVar[tuple[tuple[Relationship]]] = tuple()

    question_id: UUID = Field(..., **{ServiceFields.SORTING_FIELD: QuestionAnswer.question_id})
    answer_value: bool | str | int = Field(..., **{ServiceFields.SORTING_FIELD: QuestionAnswer.options["value"]})

    @classmethod
    def from_orm(cls, model_obj: QuestionAnswer) -> "QuestionAnswerQuestionIdValueOut":
        return cls(
            question_id=model_obj.question_id,
            answer_value=model_obj.options.get("value"),
        )


class QuestionAnswerIdOut(SQLAlchemyOutModel):
    relationships: ClassVar[tuple[tuple[Relationship]]] = tuple()

    uuid: UUID = Field(..., **{ServiceFields.SORTING_FIELD: QuestionAnswer.uuid})

    @classmethod
    def from_orm(cls, model_obj: QuestionAnswer) -> "QuestionAnswerIdOut":
        return cls(
            uuid=model_obj.uuid,
        )
