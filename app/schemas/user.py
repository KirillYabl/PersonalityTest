from typing import ClassVar
from uuid import UUID
from pydantic import Field
from sqlalchemy.orm import Relationship

from db.tables import User
from schemas.sqlalchemy import SQLAlchemyInModel, SQLAlchemyOutModel
from resources.schema_constants import ServiceFields

class UserIdOut(SQLAlchemyOutModel):
    relationships: ClassVar[tuple[tuple[Relationship]]] = tuple()

    uuid: UUID = Field(..., **{ServiceFields.SORTING_FIELD: User.uuid})

    @classmethod
    def from_orm(cls, model_obj: User) -> "UserIdOut":
        return cls(
            uuid=model_obj.uuid,
        )
    
class CreateUserTgInData(SQLAlchemyInModel):
    tg_user_id: int
    tg_username: str

    def to_orm(self) -> "CreateUserTgInData":
        return User(
            tg_user_id=self.tg_user_id,
            tg_username=self.tg_username,
        )