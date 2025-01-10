from typing import Any, ClassVar
from uuid import UUID
from pydantic import BaseModel, Field
from sqlalchemy.orm import Relationship

from db.tables import QuizAttempt, QuizResult
from schemas.sqlalchemy import SQLAlchemyInModel, SQLAlchemyOutModel
from resources.schema_constants import ServiceFields

class QuizResultIdOut(SQLAlchemyOutModel):
    relationships: ClassVar[tuple[tuple[Relationship]]] = tuple()

    uuid: UUID = Field(..., **{ServiceFields.SORTING_FIELD: QuizResult.uuid})

    @classmethod
    def from_orm(cls, model_obj: QuizResult) -> "QuizResultIdOut":
        return cls(
            uuid=model_obj.uuid,
        )
    
class QuizResultOut(SQLAlchemyOutModel):
    relationships: ClassVar[tuple[tuple[Relationship]]] = tuple()

    uuid: UUID = Field(..., **{ServiceFields.SORTING_FIELD: QuizResult.uuid})
    attempt_id: UUID = Field(..., **{ServiceFields.SORTING_FIELD: QuizResult.attempt_id})
    data: dict[str, Any] | None = Field(..., **{ServiceFields.SORTING_FIELD: QuizResult.data})


    @classmethod
    def from_orm(cls, model_obj: QuizResult) -> "QuizResultOut":
        return cls(
            uuid=model_obj.uuid,
            attempt_id=model_obj.attempt_id,
            data=model_obj.data,
        )
    

class QuizResultWithAttemptAndQuizIdsOut(SQLAlchemyOutModel):
    relationships: ClassVar[tuple[tuple[Relationship]]] = (
        (QuizResult.attempt, QuizAttempt.quiz),
    )

    uuid: UUID = Field(..., **{ServiceFields.SORTING_FIELD: QuizResult.uuid})
    attempt_id: UUID = Field(..., **{ServiceFields.SORTING_FIELD: QuizResult.attempt_id})
    quiz_id: UUID = Field(..., **{ServiceFields.SORTING_FIELD: QuizAttempt.quiz_id})

    @classmethod
    def from_orm(cls, model_obj: QuizResult) -> "QuizResultWithAttemptAndQuizIdsOut":
        return cls(
            uuid=model_obj.uuid,
            attempt_id=model_obj.attempt_id,
            quiz_id=model_obj.attempt.quiz_id,
        )
    

class QuizResultIn(SQLAlchemyInModel):
    attempt_id: UUID
    data: dict[str, Any]

    def to_orm(self) -> QuizResult:
        return QuizResult(
            attempt_id=self.attempt_id,
            data=self.data,
        )
    
class QuizResultUpdateDataIn(BaseModel):
    data: dict[str, Any]
