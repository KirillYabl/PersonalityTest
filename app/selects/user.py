from typing import Protocol
from uuid import UUID

from db.repositories.base import SQLAlchemyRepository
from schemas.user import UserIdOut

async def get_user_by_id(user_id: UUID, user_repository: SQLAlchemyRepository) -> UserIdOut | None:
    return await user_repository.get_by_id(user_id, out_data=UserIdOut)

class GetUserByIdP(Protocol):
    async def __call__(user_id: UUID, user_repository: SQLAlchemyRepository) -> UserIdOut | None:
        ...