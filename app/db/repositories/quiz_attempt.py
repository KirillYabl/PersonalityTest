from db.tables import QuizAttempt
from db.repositories.base import SQLAlchemyRepository

class QuizAttemptRepository(SQLAlchemyRepository):
    model = QuizAttempt
    primary_key_name = "uuid"