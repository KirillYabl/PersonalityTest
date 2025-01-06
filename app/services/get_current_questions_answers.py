from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Protocol
from uuid import UUID

from schemas.question_answer import QuestionAnswerQuestionIdValueOut
from db.tables import Question, QuestionAnswer, Quiz, QuizAttempt
from schemas.question import QuestionOut
from db.repositories import QuestionAnswerRepository, QuestionRepository, QuizAttemptRepository, QuizRepository
from db.repositories.base import SQLAlchemyRepository
from schemas.quiz import QuizIdOut, QuizOut
from schemas.quiz_attempt import QuizAttemptIdDatesOut
from schemas.sqlalchemy import SQLAlchemyOutModel
from loguru import logger

async def _get_last_attempt_for_user(
    user_uuid: UUID, 
    quiz_attempt_repository: SQLAlchemyRepository,
) -> QuizAttemptIdDatesOut | None:
    """Получить последнюю попытку прохождения юзером

    :param user_uuid: идентификатор юзера
    :param quiz_attempt_repository: репозиторий попыток прохождения
    :return: последняя попытка или None
    """
    filters = (
        QuizAttempt.user_id == user_uuid,
    )
    last_attempt = await quiz_attempt_repository.get_many(
        *filters, 
        out_data=QuizAttemptIdDatesOut, 
        order_by=("-created_at",), 
        limit=1,
    )
    return last_attempt[0] if last_attempt else None

class _GetLastAttemptForUserP(Protocol):
    async def __call__(
        user_uuid: UUID, 
        quiz_attempt_repository: SQLAlchemyRepository,
    ) -> QuizAttemptIdDatesOut | None:
        ...

async def _get_answers_for_questions_by_attempt(
    quiz_attempt_uuid: UUID,
    question_answer_repository: SQLAlchemyRepository,
    order_by: tuple[str],
    out_model: SQLAlchemyOutModel,
) -> list[SQLAlchemyOutModel]:
    """Получить ответы пользователя на вопросы по попытке.

    :param quiz_attempt_uuid: идентификатор попытки прохождения
    :param question_answer_repository: репозиторий ответов на вопросы
    :param order_by: поля сортировки, могут быть пустым кортежем
    :param out_model: модель для результатов
    :return: список ответов на вопросы
    """        
    filters = (
        QuestionAnswer.attempt_id == quiz_attempt_uuid,
    )
    return await question_answer_repository.get_many(*filters, out_data=out_model, order_by=order_by)

class _GetAnswersForQuestionsByAttemptP(Protocol):
    async def __call__(
        quiz_attempt_uuid: UUID,
        question_answer_repository: SQLAlchemyRepository,
        order_by: tuple[str],
        out_model: SQLAlchemyOutModel,
    ) -> list[SQLAlchemyOutModel]:
        ...

@dataclass(frozen=True, kw_only=True, slots=True)
class GetCurrentQuestionsAnswersService:
    out_model: SQLAlchemyOutModel = QuestionAnswerQuestionIdValueOut
    
    _quiz_attempt_repository: SQLAlchemyRepository = QuizAttemptRepository()
    _question_answer_repository: SQLAlchemyRepository = QuestionAnswerRepository()
    _get_last_attempt_for_user: _GetLastAttemptForUserP = _get_last_attempt_for_user
    _get_answers_for_questions_by_attempt: _GetAnswersForQuestionsByAttemptP = _get_answers_for_questions_by_attempt
    _order_by: tuple[str] = tuple()

    async def __call__(self, user_uuid: UUID) -> list[SQLAlchemyOutModel]:
        logger.debug(f"Нахожу последнюю попытку прохождения для юзера {user_uuid=}")
        last_attempt = await self._get_last_attempt_for_user(
            user_uuid=user_uuid, 
            quiz_attempt_repository=self._quiz_attempt_repository,
        )
        if not last_attempt:
            logger.warning(f"Не найдено попыток прохождения")
            return []
        
        return await self._get_answers_for_questions_by_attempt(
            quiz_attempt_uuid=last_attempt.uuid,
            question_answer_repository=self._question_answer_repository,
            order_by=self._order_by,
            out_model=self.out_model,
        )
    
get_current_questions_answers_s: GetCurrentQuestionsAnswersService = GetCurrentQuestionsAnswersService()