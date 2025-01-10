from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from loguru import logger
from pydantic import BaseModel

from core.errors import InvalidAnswersException, QuizAttemptNotFoundException, UserNotFoundByTgIdException
from core.errors_base import ServiceExceptionGroup
from db.database import get_db_session, transaction
from db.repositories.base import SQLAlchemyRepository
from db.repositories import QuestionAnswerRepository, QuestionRepository, QuizAttemptRepository, UserRepository
from db.tables import Question, QuestionAnswer
from schemas.question import QuestionTypeInfoOut
from schemas.question_answer import QuestionAnswerIdOut
from schemas.sqlalchemy import SQLAlchemyOutModel
from selects.quiz_attempt import GetLastAttemptForUserP, get_last_attempt_for_user
from selects.user import GetUserByIdP, get_user_by_id

class _CurrentQuestionAnswerDTO(BaseModel):
    question_uuid: UUID
    value: bool | str | int

async def _validate_answers(answers: list[_CurrentQuestionAnswerDTO], question_repository: SQLAlchemyRepository) -> list[list[str]]:
    """Валидировать ответы в зависимости от типа.

    :param answers: ответы
    :param question_repository: репозиторий вопросов
    :return: список ошибок, если нет ошибок, то пустой список, иначе список такой же длины, что и список ответов.

        Если в первом ответе нет ошибок, а во втором есть. То первый элемент будет пустым списком, а второй не пустым списком.
    """    
    filters = (
        Question.uuid.in_({answer.question_uuid for answer in answers}),
    )
    questions: list[QuestionTypeInfoOut] = await question_repository.get_many(*filters, out_data=QuestionTypeInfoOut)
    questions = {question.uuid: question for question in questions}

    errors = [[]] * len(answers)
    has_errors = False
    for i, answer in enumerate(answers):
        question = questions.get(answer.question_uuid)
        suberrors = []
        if not question:
            suberrors.append(f"question_uuid={str(answer.question_uuid)} не найден")
            has_errors = True
            errors[i] = suberrors
            continue
        
        logger.info(f"{question.answer_type=} {answer.value=}")
        match question.answer_type:
            case "integer":
                if type(answer.value) != int:  # строгое сравнение, т.к. там хранится json и например isinstance(True, int) == True
                    suberrors.append(
                        f"question_uuid={str(answer.question_uuid)}, value={answer.value} не {question.answer_type}"
                    )
                    has_errors = True
                    errors[i] = suberrors
                    continue

                if isinstance(question.min_value, int) and answer.value < question.min_value:
                    suberrors.append(
                        f"question_uuid={str(answer.question_uuid)}, value={answer.value} меньше минимального {question.min_value}"
                    )
                if isinstance(question.max_value, int) and answer.value > question.max_value:
                    suberrors.append(
                        f"question_uuid={str(answer.question_uuid)}, value={answer.value} больше максимального {question.max_value}"
                    )

                if suberrors:
                    errors[i] = suberrors
                    has_errors = True
            
            case "boolean":
                if type(answer.value) != bool:
                    suberrors.append(
                        f"question_uuid={str(answer.question_uuid)}, value={answer.value} не {question.answer_type}"
                    )
                    has_errors = True
                    errors[i] = suberrors
            case _:
                if not isinstance(answer.value, bool):
                    suberrors.append(
                        f"question_uuid={str(answer.question_uuid)}, value={answer.value} неизвестный тип {question.answer_type}"
                    )
                    has_errors = True
                    errors[i] = suberrors

    if not has_errors:
        return []
    return errors

class _ValidateAnswersP(Protocol):
    async def __call__(answers: list[_CurrentQuestionAnswerDTO], question_repository: SQLAlchemyRepository) -> list[list[str]]:
        ...

async def _delete_old_answers(
    quiz_attempt_uuid: UUID, 
    answers: list[_CurrentQuestionAnswerDTO],
    question_answer_repository: SQLAlchemyRepository,
) -> None:
    """Удалить старые ответы на данные вопросы.

    :param quiz_attempt_uuid: идентификатор попытки
    :param answers: ответы
    :param question_answer_repository: репозиторий ответов на вопросы
    """    
    filters = (
        QuestionAnswer.attempt_id == quiz_attempt_uuid,
        QuestionAnswer.question_id.in_({answer.question_uuid for answer in answers}),
    )
    answer_questions: list[QuestionAnswerIdOut] = await question_answer_repository.get_many(*filters, out_data=QuestionAnswerIdOut)
    await question_answer_repository.delete_by_ids(ids={answer_question.uuid for answer_question in answer_questions})

class _DeleteOldAnswersP(Protocol):
    async def __call__(
        quiz_attempt_uuid: UUID, 
        answers: list[_CurrentQuestionAnswerDTO],
        question_answer_repository: SQLAlchemyRepository,
    ) -> None:
        ...

async def _insert_answers(
    quiz_attempt_uuid: UUID, 
    answers: list[_CurrentQuestionAnswerDTO],
    question_answer_repository: SQLAlchemyRepository,
) -> None:
    """Вставить ответы на вопросы.

    Не проверяется, что на вопрос в попытке уже был дан ответ, необходимо заранее удалить старые ответы.

    :param quiz_attempt_uuid: идентификатор попытки
    :param answers: ответы
    :param question_answer_repository: репозиторий ответов на вопросы
    """    
    values = []
    for answer in answers:
        values.append(
            {
                "attempt_id": quiz_attempt_uuid,
                "question_id": answer.question_uuid,
                "options": {
                    "value": answer.value,
                }
            }
        )
    await question_answer_repository.create_many(in_datas=values, out_data=None)

class _InsertAnswersP(Protocol):
    async def __call__(
        quiz_attempt_uuid: UUID, 
        answers: list[_CurrentQuestionAnswerDTO],
        question_answer_repository: SQLAlchemyRepository,
    ) -> None:
        ...


@dataclass(frozen=True, kw_only=True, slots=True)
class AnswerCurrentQuestionsService:
    _question_answer_repository: SQLAlchemyRepository = QuestionAnswerRepository()
    _quiz_attempt_repository: SQLAlchemyRepository = QuizAttemptRepository()
    _question_repository: SQLAlchemyRepository = QuestionRepository()

    _validate_answers: _ValidateAnswersP = _validate_answers
    _get_last_attempt_for_user: GetLastAttemptForUserP = get_last_attempt_for_user
    _delete_old_answers: _DeleteOldAnswersP = _delete_old_answers
    _insert_answers: _InsertAnswersP = _insert_answers

    _exceptions_group_class: type[ServiceExceptionGroup] = ServiceExceptionGroup

    async def __call__(self, user_uuid: UUID, quiz_uuid: UUID, answers: list[BaseModel]) -> SQLAlchemyOutModel:
        _exceptions_group = self._exceptions_group_class("Ошибки в сервисе AnswerCurrentQuestionsService", [ValueError()])
        logger.info("Начинаю работу сервиса")

        answers = [_CurrentQuestionAnswerDTO(**answer.model_dump()) for answer in answers]
        logger.debug(f"Получены ответы: {answers}")
        logger.info("Начинаю валидаюцию ответов")

        errors = await self._validate_answers(answers=answers, question_repository=self._question_repository)
        if errors:
            _exceptions_group.add_error(InvalidAnswersException(details=errors))
            logger.info("Валидация прошла с ошибками")
            logger.debug(f"Ошибки валидации ответов: {errors}")

        logger.info(f"Нахожу последнюю попытку прохождения для юзера {user_uuid=}")
        last_attempt = await self._get_last_attempt_for_user(
            user_uuid=user_uuid, 
            quiz_uuid=quiz_uuid,
            quiz_attempt_repository=self._quiz_attempt_repository,
        )
        if not last_attempt:
            _exceptions_group.add_error(QuizAttemptNotFoundException(
                details=f"Не найдено попыток прохождения для пользователя user_uuid={str(user_uuid)}"),
            )
            _exceptions_group.raise_if_not_empty()
        logger.info(f"Последняя попытка прохождения для юзера {last_attempt=}")

        _exceptions_group.raise_if_not_empty()

        logger.info("Начинаю сохранение ответов")
        async with get_db_session() as session:
            async with transaction(session=session):
                logger.info("Удаляю старые ответы")
                await self._delete_old_answers(
                    quiz_attempt_uuid=last_attempt.uuid, 
                    answers=answers, 
                    question_answer_repository=self._question_answer_repository,
                )
                await session.flush()
                logger.info("Загружаю новые ответы")
                await self._insert_answers(
                    quiz_attempt_uuid=last_attempt.uuid, 
                    answers=answers, 
                    question_answer_repository=self._question_answer_repository,
                )
                logger.info("Ответы успешно загружены")

        return None
    
answer_current_questions_s: AnswerCurrentQuestionsService = AnswerCurrentQuestionsService()