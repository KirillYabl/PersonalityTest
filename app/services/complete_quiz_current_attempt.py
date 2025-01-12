from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from loguru import logger

from api.questions.v1.api import get_quiz_questions_s
from core.errors import (
    QuizAttemptAlreadyHasResultException,
    QuizAttemptNotAllQuestionsAnsweredException,
    QuizAttemptNotFoundException,
)
from core.errors_base import ServiceExceptionGroup
from db.repositories import QuestionAnswerRepository, QuizAttemptRepository
from db.repositories.base import SQLAlchemyRepository
from db.repositories.quiz_result import QuizResultRepository
from db.tables import QuestionAnswer, QuizResult
from resources.schema_constants import ResultStatus
from schemas.question import QuestionOut
from schemas.question_answer import QuestionAnswerQuestionIdValueOut
from schemas.quiz_result import QuizResultIdOut, QuizResultIn
from schemas.sqlalchemy import SQLAlchemyOutModel
from selects.quiz_attempt import GetLastAttemptForUserP, get_last_attempt_for_user
from services.get_quiz_questions import GetQuizQuestionsService


async def _get_quiz_result_by_attempt(
    attempt_uuid: UUID,
    quiz_result_repository: SQLAlchemyRepository,
) -> QuizResultIdOut | None:
    """Найти результат по попытке прохождения теста.

    :param attempt_uuid: идентификатор попытки прохождения теста
    :param quiz_result_repository: репозиторий результатов теста
    :return: идентификатор результата или None
    """
    filters = (QuizResult.attempt_id == attempt_uuid,)
    results = await quiz_result_repository.get_many(*filters, out_data=QuizResultIdOut, limit=1)
    return results[0] if results else None


class _GetQuizResultByAttemptP(Protocol):
    async def __call__(
        attempt_uuid: UUID,
        quiz_result_repository: SQLAlchemyRepository,
    ) -> SQLAlchemyOutModel | None: ...


async def _create_quiz_result(
    attempt_uuid: UUID,
    out_model: SQLAlchemyOutModel,
    quiz_result_repository: SQLAlchemyRepository,
) -> QuizResultIdOut:
    """Создать результат прохождения квиза.

    Эта функция только создает результат ожидающий расчета.
    Расчет будет делаться асинхронно.

    :param attempt_uuid: идентификатор попытки прохождения теста
    :param out_model: модель, в которой будут отданы данные
    :param quiz_result_repository: репозиторий результатов теста
    :return: данные результата в модели out_model
    """
    in_data = QuizResultIn(
        attempt_id=attempt_uuid,
        data={
            "status": ResultStatus.PENDING,
        },
    )
    return await quiz_result_repository.create(in_data=in_data, out_data=out_model)


class _CreateQuizResultP(Protocol):
    async def __call__(
        attempt_uuid: UUID,
        out_model: SQLAlchemyOutModel,
        quiz_result_repository: SQLAlchemyRepository,
    ) -> SQLAlchemyOutModel: ...


async def _check_all_questions_of_attempt_answered(
    quiz_uuid: UUID,
    attempt_uuid: UUID,
    question_answer_repository: SQLAlchemyRepository,
    get_quiz_questions_service: GetQuizQuestionsService,
) -> list[QuestionOut]:
    """Првоерить, что на все вопросы даны ответы.

    Вопросы не требующие ответа или вопросы с ответом по умолчанию считаются отвеченными.

    :param quiz_uuid: идентификатор теста
    :param attempt_uuid: идентификатор попытки прохождения теста
    :param question_answer_repository: репозиторий ответов на вопросы
    :param get_quiz_questions_service: сервис по получению активных вопросов теста
    :return: список вопросов, на которые не были даны ответы
    """
    questions = await get_quiz_questions_service(quiz_id=quiz_uuid)
    filters = (QuestionAnswer.attempt_id == attempt_uuid,)
    question_answers = await question_answer_repository.get_many(*filters, out_data=QuestionAnswerQuestionIdValueOut)
    question_answer_value_mapping = {
        question_answer.question_id: question_answer.answer_value for question_answer in question_answers
    }

    not_answered_questions = []
    for question in questions:
        question_answer_value = question_answer_value_mapping.get(question.uuid)

        no_need_answer = not question.required or question.default
        answered = question_answer_value is not None
        if no_need_answer or answered:
            continue

        not_answered_questions.append(question)

    return not_answered_questions


class _CheckAllQuestionsOfAttemptAnsweredP(Protocol):
    async def __call__(
        quiz_uuid: UUID,
        attempt_uuid: UUID,
        question_answer_repository: SQLAlchemyRepository,
        get_quiz_questions_service: GetQuizQuestionsService,
    ) -> list[QuestionOut]: ...


@dataclass(frozen=True, kw_only=True, slots=True)
class CompleteQuizCurrentAttemptService:
    out_model: SQLAlchemyOutModel = QuizResultIdOut

    _quiz_attempt_repository: SQLAlchemyRepository = QuizAttemptRepository()
    _quiz_result_repository: SQLAlchemyRepository = QuizResultRepository()
    _question_answer_repository: SQLAlchemyRepository = QuestionAnswerRepository()
    _get_last_attempt_for_user: GetLastAttemptForUserP = get_last_attempt_for_user
    _get_quiz_questions_service: GetQuizQuestionsService = get_quiz_questions_s
    _get_quiz_result_by_attempt: _GetQuizResultByAttemptP = _get_quiz_result_by_attempt
    _create_quiz_result: _CreateQuizResultP = _create_quiz_result
    _check_all_questions_of_attempt_answered: _CheckAllQuestionsOfAttemptAnsweredP = (
        _check_all_questions_of_attempt_answered
    )
    _exceptions_group_class: type[ServiceExceptionGroup] = ServiceExceptionGroup

    async def __call__(self, quiz_uuid: UUID, user_uuid: UUID) -> SQLAlchemyOutModel:
        _exceptions_group = self._exceptions_group_class(
            "Ошибки в сервисе CompleteQuizCurrentAttemptService", [ValueError()]
        )

        logger.info(f"Нахожу последнюю попытку прохождения для юзера {user_uuid=}, {quiz_uuid=}")
        last_attempt = await self._get_last_attempt_for_user(
            user_uuid=user_uuid,
            quiz_uuid=quiz_uuid,
            quiz_attempt_repository=self._quiz_attempt_repository,
        )
        if not last_attempt:
            _exceptions_group.add_error(
                QuizAttemptNotFoundException(
                    details=f"Не найдено попыток прохождения для пользователя user_uuid={str(user_uuid)}"
                ),
            )
            _exceptions_group.raise_if_not_empty()
        logger.info(f"Последняя попытка прохождения для юзера {last_attempt=}")

        result = await self._get_quiz_result_by_attempt(
            attempt_uuid=last_attempt.uuid,
            quiz_result_repository=self._quiz_result_repository,
        )
        if result:
            _exceptions_group.add_error(
                QuizAttemptAlreadyHasResultException(
                    details=f"Для попытки attempt_uuid={str(last_attempt.uuid)} уже есть результат"
                ),
            )
            _exceptions_group.raise_if_not_empty()

        not_answered_questions = await self._check_all_questions_of_attempt_answered(
            quiz_uuid=quiz_uuid,
            attempt_uuid=last_attempt.uuid,
            question_answer_repository=self._question_answer_repository,
            get_quiz_questions_service=self._get_quiz_questions_service,
        )
        if not_answered_questions:
            details = {
                "message": "Не на все вопросы даны ответы",
                "not_answered_questions": [str(question.uuid) for question in not_answered_questions],
            }
            _exceptions_group.add_error(QuizAttemptNotAllQuestionsAnsweredException(details=details))

        _exceptions_group.raise_if_not_empty()

        return await self._create_quiz_result(
            attempt_uuid=last_attempt.uuid,
            out_model=self.out_model,
            quiz_result_repository=self._quiz_result_repository,
        )


complete_quiz_current_attempt_s: CompleteQuizCurrentAttemptService = CompleteQuizCurrentAttemptService()
