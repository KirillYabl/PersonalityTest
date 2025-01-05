from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from core.errors import QuizNotFoundByIdException, UserNotFoundByTgIdException
from core.errors_base import ServiceExceptionGroup
from db.repositories.base import SQLAlchemyRepository
from db.repositories import QuizAttemptRepository, QuizRepository, UserRepository
from db.tables import User
from schemas.quiz import QuizIdOut
from schemas.quiz_attempt import QuizAttemptIdOut, QuizAttemptIn
from schemas.sqlalchemy import SQLAlchemyOutModel
from schemas.user import UserIdOut

async def _get_user_by_tg_id(tg_user_id: int, user_repository: SQLAlchemyRepository) -> UserIdOut | None:
    filters = (
        User.tg_user_id == tg_user_id,
    )
    users = await user_repository.get_many(*filters, out_data=UserIdOut)
    return users[0] if users else None

class _GetUserByTgIdP(Protocol):
    async def __call__(tg_user_id: int, user_repository: SQLAlchemyRepository) -> UserIdOut | None:
        ...

async def _create_quiz_attempt(
    quiz_id: UUID, 
    user_id: UUID, 
    out_model: SQLAlchemyOutModel, 
    quiz_attempt_repository: SQLAlchemyRepository,
) -> SQLAlchemyOutModel:
    in_data = QuizAttemptIn(
        quiz_id=quiz_id,
        user_id=user_id,
    )
    return await quiz_attempt_repository.create(in_data=in_data, out_data=out_model)

class _CreateQuizAttemptP(Protocol):
    async def __call__(
        quiz_id: UUID,
        user_id: UUID,
        out_model: SQLAlchemyOutModel,
        quiz_attempt_repository: SQLAlchemyRepository,
    ) -> SQLAlchemyOutModel:
        ...

@dataclass(frozen=True, kw_only=True, slots=True)
class CreateQuizAttemptService:
    out_model: SQLAlchemyOutModel = QuizAttemptIdOut

    _quiz_repository: SQLAlchemyRepository = QuizRepository()
    _quiz_attempt_repository: SQLAlchemyRepository = QuizAttemptRepository()
    _user_repository: SQLAlchemyRepository = UserRepository()
    _get_user_by_tg_id: _GetUserByTgIdP = _get_user_by_tg_id
    _create_quiz_attempt: _CreateQuizAttemptP = _create_quiz_attempt
    _exceptions_group_class: ServiceExceptionGroup = ServiceExceptionGroup

    async def __call__(self, quiz_id: UUID, tg_user_id: int) -> SQLAlchemyOutModel:
        _exceptions_group = self._exceptions_group_class("Ошибки в сервисе CreateQuizAttemptService", [ValueError()])

        user = await self._get_user_by_tg_id(tg_user_id=tg_user_id, user_repository=self._user_repository)
        if user is None:
            _exceptions_group.add_error(UserNotFoundByTgIdException(details=f"Пользователь с tg_id={tg_user_id} не найден."))
        
        quiz = await self._quiz_repository.get_by_id(id=quiz_id, out_data=QuizIdOut)
        if quiz is None:
            _exceptions_group.add_error(QuizNotFoundByIdException(details=f"Тест с quiz_id={str(quiz_id)} не найден."))

        _exceptions_group.raise_if_not_empty()

        return await self._create_quiz_attempt(
            quiz_id=quiz_id, 
            user_id=user.uuid,
            out_model=self.out_model, 
            quiz_attempt_repository=self._quiz_attempt_repository,
        )
    
create_quiz_attempt_s: CreateQuizAttemptService = CreateQuizAttemptService()