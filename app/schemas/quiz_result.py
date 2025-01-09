from typing import Any, ClassVar
from uuid import UUID
from pydantic import Field
from sqlalchemy.orm import Relationship

from db.tables import QuizResult
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
    

class QuizResultIn(SQLAlchemyInModel):
    attempt_id: UUID
    data: dict[str, Any]

    def to_orm(self) -> QuizResult:
        return QuizResult(
            attempt_id=self.attempt_id,
            data=self.data,
        )