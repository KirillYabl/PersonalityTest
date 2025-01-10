from collections import defaultdict
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from core.errors import NotAllQuizTypesCalculatedError, QuizResultNotFoundException
from core.errors_base import ServiceExceptionGroup
from core.types import JSON
from db.repositories.quiz_result import QuizResultRepository
from db.tables import QuestionAnswer, Quiz
from resources.schema_constants import ResultStatus
from schemas.question import QuestionOut
from db.repositories import QuestionAnswerRepository, QuestionRepository, QuizRepository
from db.repositories.base import SQLAlchemyRepository
from schemas.question_answer import QuestionAnswerQuestionIdValueOut
from schemas.quiz import QuizOut
from schemas.quiz_result import QuizResultUpdateDataIn, QuizResultWithAttemptAndQuizIdsOut
from schemas.sqlalchemy import SQLAlchemyOutModel
from loguru import logger

from selects.question import GetActiveQuestionsByQuizIdsP, get_active_questions_by_quiz_ids
from selects.quiz import GetAllChildrenQuizesP, get_all_children_quizes
    

async def _get_quiz_result_by_uuid(
    result_uuid: UUID, 
    quiz_result_repository: SQLAlchemyRepository,
) -> QuizResultWithAttemptAndQuizIdsOut | None:
    return await quiz_result_repository.get_by_id(id=result_uuid, out_data=QuizResultWithAttemptAndQuizIdsOut)

class _GetQuizResultByUuidP(Protocol):
    async def __call__(
        result_uuid: UUID, 
        quiz_result_repository: SQLAlchemyRepository,
    ) -> QuizResultWithAttemptAndQuizIdsOut | None:
        ...

async def _calculate_quizes_results(
    quiz: QuizOut,
    quiz_questions: list[QuestionOut],
    quiz_result: QuizResultWithAttemptAndQuizIdsOut,
    question_answer_repository: SQLAlchemyRepository,
) -> JSON:
    """Рассчитать результаты теста.

    :param quiz: тест
    :param quiz_questions: вопросы теста (включают также вопросы родительсикх тестов, нужна фильтрация)
    :param quiz_result: объекта записи результата теста
    :param question_answer_repository: репозиторий ответа на вопрос
    :return: результат теста
    """    
    quiz_type_questions = [question for question in quiz_questions if question.quiz_name == quiz.name]
    filters = (
        QuestionAnswer.attempt_id == quiz_result.attempt_id,
        QuestionAnswer.question_id.in_([question.uuid for question in quiz_type_questions]),
    )
    quiz_type_question_answers = await question_answer_repository.get_many(*filters, out_data=QuestionAnswerQuestionIdValueOut)
    quiz_type_question_answers_mapping = {answer.question_id: answer.answer_value for answer in quiz_type_question_answers}
    match quiz.type_name:

        case "PersonalityCharacterTest":
            # принцип расчета, вычислить нормированный на 1 балл 
            # по каждой категории (топику), как сумма всех на сумму максимальных баллов
            temp_result = defaultdict(lambda: defaultdict(int))
            for question in quiz_type_questions:
                answer = quiz_type_question_answers_mapping.get(question.uuid)
                if answer is None:
                    answer = question.default
                temp_result[question.topic_name]["points"] += answer
                temp_result[question.topic_name]["max_points"] += question.max_value
            result = defaultdict(int)
            for question_type, value in temp_result.items():
                result[question_type] = value["points"] / value["max_points"]

        case "PersonalityApprecationTest":
            # принцип расчета, по каждой категории вычислить баллы и найти 2 категории с максимальным числом баллов
            temp_result = defaultdict(int)
            for question in quiz_type_questions:
                answer = quiz_type_question_answers_mapping.get(question.uuid)
                if answer is None:
                    answer = question.default
                temp_result[question.topic_name] += int(answer)
            pick_first_n_appreciations = 2
            result = sorted(temp_result, key=lambda question_type: temp_result[question_type], reverse=True)[:pick_first_n_appreciations]

        case "PersonalityValuesTest":
            # принцип расчета, по каждой категории вычислить баллы и найти 2 категории с максимальным числом баллов
            temp_result = defaultdict(int)
            for question in quiz_type_questions:
                answer = quiz_type_question_answers_mapping.get(question.uuid)
                if answer is None:
                    answer = question.default
                temp_result[question.topic_name] += answer
            pick_first_n_appreciations = 2
            result = sorted(temp_result, key=lambda question_type: temp_result[question_type], reverse=True)[:pick_first_n_appreciations]

        case _:
            result = None
            
    return result

class _CalculateQuizesResultsP:
    async def __call__(
        quiz: QuizOut,
        quiz_questions: list[QuestionOut],
        quiz_result: QuizResultWithAttemptAndQuizIdsOut,
        question_answer_repository: SQLAlchemyRepository,
    ) -> JSON:
        ...

async def _record_quiz_result(
    quiz_result: QuizResultWithAttemptAndQuizIdsOut, 
    data: dict[JSON],
    quiz_result_repository: SQLAlchemyRepository,
) -> None:
    """Записать результаты теста.

    :param quiz_result: результат теста
    :param data: данные для записи
    :param quiz_result_repository: репозиторий результата теста
    """    
    in_data = QuizResultUpdateDataIn(
        data=data,
    )
    await quiz_result_repository.update_one(id=quiz_result.uuid, in_data=in_data, out_data=None)

class _RecordQuizResultP:
    async def __call__(
        quiz_result: QuizResultWithAttemptAndQuizIdsOut, 
        data: dict[JSON],
        quiz_result_repository: SQLAlchemyRepository,
    ) -> None:
        ...
    

@dataclass(frozen=True, kw_only=True, slots=True)
class CalculateQuizResultService:
    _quiz_repository: SQLAlchemyRepository = QuizRepository()
    _quiz_result_repository: SQLAlchemyRepository = QuizResultRepository()
    _question_repository: SQLAlchemyRepository = QuestionRepository()
    _question_answer_repository: SQLAlchemyRepository = QuestionAnswerRepository()
    _get_all_children_quizes: GetAllChildrenQuizesP = get_all_children_quizes
    _get_active_questions_by_quiz_ids: GetActiveQuestionsByQuizIdsP = get_active_questions_by_quiz_ids
    _get_quiz_result_by_uuid: _GetQuizResultByUuidP = _get_quiz_result_by_uuid
    _calculate_quizes_results: _CalculateQuizesResultsP = _calculate_quizes_results
    _record_quiz_result: _RecordQuizResultP = _record_quiz_result
    _expected_quiz_types: tuple[str] = (
        "PersonalityCharacterTest",
        "PersonalityApprecationTest",
        "PersonalityValuesTest",
    )
    _exceptions_group_class: type[ServiceExceptionGroup] = ServiceExceptionGroup

    async def __call__(self, result_uuid: UUID) -> list[SQLAlchemyOutModel]:
        _exceptions_group = self._exceptions_group_class("Ошибки в сервисе CalculateQuizResultService", [ValueError()])

        logger.debug(f"Нахожу результат по {result_uuid=}")
        quiz_result = await _get_quiz_result_by_uuid(
            result_uuid=result_uuid,
            quiz_result_repository=self._quiz_result_repository,
        )
        if quiz_result is None:
            _exceptions_group.add_error(QuizResultNotFoundException(details=f"Результат теста по {result_uuid=} не найден"))
            _exceptions_group.raise_if_not_empty()
        logger.info(f"Результат теста: {quiz_result}")

        await self._record_quiz_result(
            quiz_result=quiz_result, 
            data={"status": ResultStatus.IN_PROCESS},
            quiz_result_repository=self._quiz_result_repository,
        )
        
        quiz_id = quiz_result.quiz_id
        logger.debug(f"Получаю дочерние тесты для {quiz_id=}")
        children_quizes = await self._get_all_children_quizes(
            quiz_id=quiz_id, 
            quiz_repository=self._quiz_repository,
        )
        quiz_ids = set([quiz_id]) | {quiz.uuid for quiz in children_quizes}
        filters = (
            Quiz.uuid.in_(quiz_ids),
        )
        logger.debug(f"Тест и его дочерние {quiz_ids=}")

        quizes = await self._quiz_repository.get_many(*filters, out_data=QuizOut)
        quizes_questions = await self._get_active_questions_by_quiz_ids(
            quiz_ids=quiz_ids, 
            question_repository=self._question_repository,
            out_model=QuestionOut,
        )
        quizes_calculated = 0
        calculated_quiz_results = {}
        for quiz in quizes:
            if quiz.type_name not in self._expected_quiz_types:
                continue
            quiz_questions = [question for question in quizes_questions if question.quiz_name == quiz.name]
            calculated_quiz_result = await self._calculate_quizes_results(
                quiz=quiz,
                quiz_questions=quiz_questions,
                quiz_result=quiz_result,
                question_answer_repository=self._question_answer_repository,
            )
            calculated_quiz_results[quiz.type_name] = calculated_quiz_result
            quizes_calculated += 1
        if len(calculated_quiz_results) != len(self._expected_quiz_types):
            _exceptions_group.add_error(
                NotAllQuizTypesCalculatedError(
                    details=(
                        f"Не все типы тестов рассчитаны, ожидаемается: {self._expected_quiz_types}, "
                        f"рассчитаны: {list(calculated_quiz_results.keys())}"
                    )
                )
            )
        _exceptions_group.raise_if_not_empty()
        calculated_quiz_results["status"] = ResultStatus.DONE
        await self._record_quiz_result(
            quiz_result=quiz_result, 
            data=calculated_quiz_results,
            quiz_result_repository=self._quiz_result_repository,
        )
        logger.info(f"Расчет результата {result_uuid=} завершен")

            
    
calculate_quiz_result_s: CalculateQuizResultService = CalculateQuizResultService()