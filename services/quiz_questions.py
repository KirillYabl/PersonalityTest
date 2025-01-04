from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Protocol
from uuid import UUID

from db.tables import Question, Quiz
from schemas.questions import QuestionOut
from db.repositories import QuestionRepository, QuizRepository
from db.repositories.base import SQLAlchemyRepository
from schemas.quiz import QuizIdOut, QuizOut
from schemas.sqlalchemy import SQLAlchemyOutModel
from loguru import logger

async def _get_all_children_quizes(quiz_id: UUID, quiz_repository: QuizRepository) -> list[QuizIdOut]:
    """Получить все дочерние тесты от данного.

    Работает только с активными тестами. Все неактивные тесты и их дети не будут включены.
    Если входящий тест сам не активный, то ун его не будет детей.

    Т.к. иерархия тестов использует наивное дерево, то рекурсия реализована внутри 
    алгоритма для избегания лищних запросов или использования рекурсивного запроса в БД.

    TODO: кэширование

    :param quiz_id: идентификатор родительского теста
    :param quiz_repository: репозиторий тестов
    :return: список идентификаторов дочерних активных тестов
    """    
    all_quizes: list[QuizOut] = await quiz_repository.get_many(out_data=QuizOut)
    quizes_to_watch = [quiz for quiz in all_quizes if quiz.parent_id is None and quiz.active]
    quiz_parents_mapping = defaultdict(set)

    while quizes_to_watch:
        quiz = quizes_to_watch.pop(0)
        for child_quiz in all_quizes:
            if not child_quiz.active or child_quiz.parent_id != quiz.uuid:
                continue
            quiz_parents_mapping[child_quiz.uuid].add(quiz.uuid)
            quizes_to_watch.append(child_quiz)

    quiz_children = set()
    for quiz_uuid, quiz_parents in quiz_parents_mapping.items():
        if quiz_id in quiz_parents:
            quiz_children.add(quiz_uuid)
        
    return [QuizIdOut(uuid=quiz_uuid) for quiz_uuid in quiz_children]

class _GetAllChildrenQuizesP(Protocol):
    async def __call__(quiz_id: UUID, quiz_repository: QuizRepository) -> list[QuizIdOut]:
        ...

async def _get_active_questions_by_quiz_ids(
        quiz_ids: Iterable[UUID], 
        question_repository: QuizRepository,
        order_by: tuple[str],
        out_model: SQLAlchemyOutModel,
    ) -> list[SQLAlchemyOutModel]:
    """Получить активные вопросы по тестам.

    :param quiz_ids: перечень тестов, в которых искать вопросы, неактивные будут игнорироваться
    :param question_repository: репозиторий вопросов
    :param order_by: поля сортировки, могут быть пустым кортежем
    :return: список вопросов
    """        
    filters = (
        Question.quiz_id.in_(quiz_ids),
        Quiz.active == True,
        Question.active == True,
    )
    return await question_repository.get_many(*filters, out_data=out_model, order_by=order_by)

class _GetActiveQuestionsByQuizIdsP(Protocol):
    async def __call__(
            quiz_ids: Iterable[UUID], 
            question_repository: QuizRepository, 
            order_by: tuple[str],
            out_model: SQLAlchemyOutModel,
        ) -> list[SQLAlchemyOutModel]:
        ...

@dataclass(frozen=True, kw_only=True, slots=True)
class QuizQuestionsService:
    _quiz_repository: SQLAlchemyRepository = QuizRepository()
    _question_repository: SQLAlchemyRepository = QuestionRepository()
    _get_all_children_quizes: _GetAllChildrenQuizesP = _get_all_children_quizes
    _get_active_questions_by_quiz_ids: _GetActiveQuestionsByQuizIdsP = _get_active_questions_by_quiz_ids
    _out_model: SQLAlchemyOutModel = QuestionOut
    _order_by: tuple[str] = ("order",)

    async def __call__(self, quiz_id: UUID) -> list[SQLAlchemyOutModel]:
        logger.debug(f"Получаю дочерние тесты для {quiz_id=}")
        children_quizes = await self._get_all_children_quizes(
            quiz_id=quiz_id, 
            quiz_repository=self._quiz_repository,
        )
        quiz_ids = set([quiz_id]) | {quiz.uuid for quiz in children_quizes}
        logger.debug(f"Тест и его дочерние {quiz_ids=}")
        return await self._get_active_questions_by_quiz_ids(
            quiz_ids=quiz_ids, 
            question_repository=self._question_repository,
            order_by=self._order_by,
            out_model=self._out_model,
        )
    
get_quiz_questions_s: QuizQuestionsService = QuizQuestionsService()