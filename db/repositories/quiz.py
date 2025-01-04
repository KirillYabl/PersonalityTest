from db.tables import Quiz
from db.repositories.base import SQLAlchemyRepository

class QuizRepository(SQLAlchemyRepository):
    model = Quiz
    primary_key_name = "uuid"