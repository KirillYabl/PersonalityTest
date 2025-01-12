from db.repositories.base import SQLAlchemyRepository
from db.tables import QuizAttempt


class QuizAttemptRepository(SQLAlchemyRepository):
    model = QuizAttempt
    primary_key_name = "uuid"
