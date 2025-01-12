from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from db.tables import Quiz


class QuizFactory(SQLAlchemyFactory[Quiz]):
    active = True
