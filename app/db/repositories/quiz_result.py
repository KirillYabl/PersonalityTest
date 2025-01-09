from db.tables import QuizResult
from db.repositories.base import SQLAlchemyRepository

class QuizResultRepository(SQLAlchemyRepository):
    model = QuizResult
    primary_key_name = "uuid"