from dataclasses import dataclass
from uuid import UUID

from loguru import logger

from schemas.question import QuestionOut
from db.repositories import QuestionRepository, QuizRepository
from db.repositories.base import SQLAlchemyRepository
from schemas.sqlalchemy import SQLAlchemyOutModel
from selects.question import GetActiveQuestionsByQuizIdsP, get_active_questions_by_quiz_ids
from selects.quiz import GetAllChildrenQuizesP, get_all_children_quizes

@dataclass(frozen=True, kw_only=True, slots=True)
class GetQuizQuestionsService:
    out_model: SQLAlchemyOutModel = QuestionOut
    
    _quiz_repository: SQLAlchemyRepository = QuizRepository()
    _question_repository: SQLAlchemyRepository = QuestionRepository()
    _get_all_children_quizes: GetAllChildrenQuizesP = get_all_children_quizes
    _get_active_questions_by_quiz_ids: GetActiveQuestionsByQuizIdsP = get_active_questions_by_quiz_ids
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
            out_model=self.out_model,
        )
    
get_quiz_questions_s: GetQuizQuestionsService = GetQuizQuestionsService()