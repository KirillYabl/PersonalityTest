from typing import ClassVar
from uuid import UUID
from pydantic import Field
from sqlalchemy.orm import Relationship

from db.tables import Quiz
from schemas.sqlalchemy import SQLAlchemyOutModel
from resources.schema_constants import ServiceFields

class QuizOut(SQLAlchemyOutModel):
    relationships: ClassVar[tuple[tuple[Relationship]]] = (
        (Quiz.type,),
    )

    uuid: UUID = Field(..., **{ServiceFields.SORTING_FIELD: Quiz.uuid})
    parent_id: UUID | None = Field(..., **{ServiceFields.SORTING_FIELD: Quiz.parent_id})
    active: bool = Field(..., **{ServiceFields.SORTING_FIELD: Quiz.active})
    name: str = Field(..., **{ServiceFields.SORTING_FIELD: Quiz.name})
    type_name: str | None = Field(..., **{ServiceFields.SORTING_FIELD: Quiz.type_id})

    @classmethod
    def from_orm(cls, model_obj: Quiz) -> "QuizOut":
        return cls(
            uuid=model_obj.uuid,
            parent_id=model_obj.parent_id,
            active=model_obj.active,
            name=model_obj.name,
            type_name=model_obj.type.name,
        )
    
class QuizIdOut(SQLAlchemyOutModel):
    relationships: ClassVar[tuple[tuple[Relationship]]] = tuple()

    uuid: UUID = Field(..., **{ServiceFields.SORTING_FIELD: Quiz.uuid})

    @classmethod
    def from_orm(cls, model_obj: Quiz) -> "QuizIdOut":
        return cls(
            uuid=model_obj.uuid,
        )