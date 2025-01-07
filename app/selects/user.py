from typing import Protocol
from uuid import UUID

from db.repositories.base import SQLAlchemyRepository
from db.tables import User
from schemas.user import UserIdOut

async def get_user_by_id(user_id: UUID, user_repository: SQLAlchemyRepository) -> UserIdOut | None:
    return await user_repository.get_by_id(user_id, out_data=UserIdOut)

class GetUserByIdP(Protocol):
    async def __call__(user_id: UUID, user_repository: SQLAlchemyRepository) -> UserIdOut | None:
        ...

async def get_user_by_tg_id(user_tg_id: UUID, user_repository: SQLAlchemyRepository) -> UserIdOut | None:
    filters = (
        User.tg_user_id == user_tg_id,
    )
    users = await user_repository.get_many(*filters, out_data=UserIdOut, limit=1)
    return users[0] if users else None

class GetUserByTgIdP(Protocol):
    async def __call__(user_tg_id: UUID, user_repository: SQLAlchemyRepository) -> UserIdOut | None:
        ...