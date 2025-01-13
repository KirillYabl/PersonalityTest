from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from db.tables.test_tables import TestBrand, TestCar
from utils.test_utils import SQLAlchemyFactoryMixin


class TestBrandFactory(SQLAlchemyFactoryMixin, SQLAlchemyFactory[TestBrand]): ...


class TestCarFactory(SQLAlchemyFactoryMixin, SQLAlchemyFactory[TestCar]):
    __set_relationships__ = True
