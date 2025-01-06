from db.tables import QuestionAnswer
from db.repositories.base import SQLAlchemyRepository

class QuestionAnswerRepository(SQLAlchemyRepository):
    model = QuestionAnswer
    primary_key_name = "uuid"