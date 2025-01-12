from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from db.tables import QuizType


class QuizTypeFactory(SQLAlchemyFactory[QuizType]): ...
