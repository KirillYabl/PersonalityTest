from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from tests.test_tables import TestCar
from utils.test_utils import SQLAlchemyFactoryMixin


class TestCarFactory(SQLAlchemyFactoryMixin, SQLAlchemyFactory[TestCar]): ...
