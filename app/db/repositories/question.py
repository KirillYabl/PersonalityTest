from db.repositories.base import SQLAlchemyRepository
from db.tables import Question


class QuestionRepository(SQLAlchemyRepository):
    model = Question
    primary_key_name = "uuid"
