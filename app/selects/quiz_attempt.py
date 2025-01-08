from typing import Protocol
from uuid import UUID

from db.repositories.base import SQLAlchemyRepository
from db.tables import QuizAttempt
from schemas.quiz_attempt import QuizAttemptIdDatesOut

async def get_last_attempt_for_user(
    user_uuid: UUID, 
    quiz_uuid: UUID,
    quiz_attempt_repository: SQLAlchemyRepository,
) -> QuizAttemptIdDatesOut | None:
    """Получить последнюю попытку прохождения юзером

    :param user_uuid: идентификатор юзера
    :param user_uuid: идентификатор теста
    :param quiz_attempt_repository: репозиторий попыток прохождения
    :return: последняя попытка или None
    """
    filters = (
        QuizAttempt.user_id == user_uuid,
        QuizAttempt.quiz_id == quiz_uuid,
    )
    last_attempt = await quiz_attempt_repository.get_many(
        *filters, 
        out_data=QuizAttemptIdDatesOut, 
        order_by=("-created_at",), 
        limit=1,
    )
    return last_attempt[0] if last_attempt else None

class GetLastAttemptForUserP(Protocol):
    async def __call__(
        user_uuid: UUID, 
        quiz_uuid: UUID,
        quiz_attempt_repository: SQLAlchemyRepository,
    ) -> QuizAttemptIdDatesOut | None:
        ...