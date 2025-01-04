from typing import ClassVar
from uuid import UUID
from pydantic import Field
from sqlalchemy.orm import Relationship

from db.tables import User
from schemas.sqlalchemy import SQLAlchemyOutModel
from resources.schema_constants import ServiceFields

class UserIdOut(SQLAlchemyOutModel):
    relationships: ClassVar[tuple[tuple[Relationship]]] = tuple()

    uuid: UUID = Field(..., **{ServiceFields.SORTING_FIELD: User.uuid})

    @classmethod
    def from_orm(cls, model_obj: User) -> "UserIdOut":
        return cls(
            uuid=model_obj.uuid,
        )