from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.value_generators.constrained_numbers import get_increment

from db.tables import Question
from utils.testutils import Sequence

class QuestionFactory(SQLAlchemyFactory[Question]):

    active = True
    order = Sequence(func=lambda n: n)
