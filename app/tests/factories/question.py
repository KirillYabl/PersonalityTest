from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from db.tables import Question
from utils.testutils import Sequence


class QuestionFactory(SQLAlchemyFactory[Question]):

    active = True
    order = Sequence(func=lambda n: n)
