from collections.abc import Iterable
from typing import Protocol
from uuid import UUID

from sqlalchemy.sql.expression import true

from api.question_answers.v1.api import SQLAlchemyOutModel
from db.repositories.base import SQLAlchemyRepository
from db.tables import Question, Quiz


async def get_active_questions_by_quiz_ids(
    quiz_ids: Iterable[UUID],
    question_repository: SQLAlchemyRepository,
    out_model: SQLAlchemyOutModel,
    order_by: tuple[str] = tuple(),
) -> list[SQLAlchemyOutModel]:
    """Получить активные вопросы по тестам.

    :param quiz_ids: перечень тестов, в которых искать вопросы, неактивные будут игнорироваться
    :param question_repository: репозиторий вопросов
    :param out_model: модель для результатов
    :param order_by: поля сортировки, могут быть пустым кортежем
    :return: список вопросов
    """
    filters = (
        Question.quiz_id.in_(quiz_ids),
        Quiz.active == true(),
        Question.active == true(),
    )
    return await question_repository.get_many(*filters, out_data=out_model, order_by=order_by)


class GetActiveQuestionsByQuizIdsP(Protocol):
    async def __call__(
        quiz_ids: Iterable[UUID],
        question_repository: SQLAlchemyRepository,
        order_by: tuple[str],
        out_model: SQLAlchemyOutModel,
    ) -> list[SQLAlchemyOutModel]: ...
