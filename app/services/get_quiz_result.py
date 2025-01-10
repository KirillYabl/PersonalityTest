from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from loguru import logger

from db.repositories.quiz_result import QuizResultRepository
from resources.schema_constants import ResultStatus
from schemas.question import QuestionOut
from db.repositories import QuestionRepository, QuizRepository
from db.repositories.base import SQLAlchemyRepository
from schemas.quiz_result import QuizResultOut
from schemas.sqlalchemy import SQLAlchemyOutModel
from selects.question import GetActiveQuestionsByQuizIdsP, get_active_questions_by_quiz_ids
from selects.quiz import GetAllChildrenQuizesP, get_all_children_quizes

async def _get_quiz_result_by_id(
    quiz_result_uuid: UUID,
    quiz_result_repository: SQLAlchemyRepository,
) -> QuizResultOut:
    """Получить результат теста по идентификатору.

    :param quiz_result_uuid: идентификатор результата теста
    :param quiz_result_repository: репозиторий результата теста
    :return: результат теста
    """    
    return await quiz_result_repository.get_by_id(id=quiz_result_uuid, out_data=QuizResultOut)

class _GetQuizResultByIdP(Protocol):
    async def __call__(
        quiz_result_uuid: UUID,
        quiz_result_repository: SQLAlchemyRepository,
    ) -> QuizResultOut:
        ...

@dataclass(frozen=True, kw_only=True, slots=True)
class GetQuizResultService:
    out_model: SQLAlchemyOutModel = QuizResultOut
    
    _quiz_result_repository: SQLAlchemyRepository = QuizResultRepository()
    _get_quiz_result_by_id: _GetQuizResultByIdP = _get_quiz_result_by_id


    async def __call__(self, quiz_result_uuid: UUID) -> tuple[bool, SQLAlchemyOutModel]:
        quiz_result = await self._get_quiz_result_by_id(
            quiz_result_uuid=quiz_result_uuid, 
            quiz_result_repository=self._quiz_result_repository,
        )
        calculated = quiz_result.data.get("status") == ResultStatus.DONE
        return calculated, quiz_result
    
get_quiz_result_s: GetQuizResultService = GetQuizResultService()