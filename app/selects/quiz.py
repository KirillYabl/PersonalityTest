from collections import defaultdict
from typing import Protocol
from uuid import UUID

from db.repositories.base import SQLAlchemyRepository
from schemas.quiz import QuizIdOut, QuizOut


async def get_all_children_quizes(quiz_id: UUID, quiz_repository: SQLAlchemyRepository) -> list[QuizIdOut]:
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


class GetAllChildrenQuizesP(Protocol):
    async def __call__(quiz_id: UUID, quiz_repository: SQLAlchemyRepository) -> list[QuizIdOut]: ...
