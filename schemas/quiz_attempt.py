from typing import ClassVar
from uuid import UUID
from pydantic import Field
from sqlalchemy.orm import Relationship

from db.tables import QuizAttempt
from schemas.sqlalchemy import SQLAlchemyInModel, SQLAlchemyOutModel
from resources.schema_constants import ServiceFields

class QuizAttemptIdOut(SQLAlchemyOutModel):
    relationships: ClassVar[tuple[tuple[Relationship]]] = tuple()

    uuid: UUID = Field(..., **{ServiceFields.SORTING_FIELD: QuizAttempt.uuid})

    @classmethod
    def from_orm(cls, model_obj: QuizAttempt) -> "QuizAttemptIdOut":
        return cls(
            uuid=model_obj.uuid,
        )
    
class QuizAttemptIn(SQLAlchemyInModel):
    quiz_id: UUID
    user_id: UUID

    def to_orm(self) -> QuizAttempt:
        return QuizAttempt(
            quiz_id=self.quiz_id,
            user_id=self.user_id,
        )