from db.repositories.base import SQLAlchemyRepository
from db.tables import QuizResult


class QuizResultRepository(SQLAlchemyRepository):
    model = QuizResult
    primary_key_name = "uuid"
