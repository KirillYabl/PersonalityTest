from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from db.tables import QuestionTopic


class QuestionTopicFactory(SQLAlchemyFactory[QuestionTopic]): ...
