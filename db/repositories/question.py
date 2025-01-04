from db.tables import Question
from db.repositories.base import SQLAlchemyRepository

class QuestionRepository(SQLAlchemyRepository):
    model = Question
    primary_key_name = "uuid"