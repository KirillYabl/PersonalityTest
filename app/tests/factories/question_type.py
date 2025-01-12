from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from db.tables import QuestionType


class QuestionTypeFactory(SQLAlchemyFactory[QuestionType]): ...
