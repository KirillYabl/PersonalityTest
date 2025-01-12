from db.repositories.base import SQLAlchemyRepository
from db.tables import QuestionAnswer


class QuestionAnswerRepository(SQLAlchemyRepository):
    model = QuestionAnswer
    primary_key_name = "uuid"
