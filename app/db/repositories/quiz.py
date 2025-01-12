from db.repositories.base import SQLAlchemyRepository
from db.tables import Quiz


class QuizRepository(SQLAlchemyRepository):
    model = Quiz
    primary_key_name = "uuid"
