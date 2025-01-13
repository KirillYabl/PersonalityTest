from db.repositories.base import SQLAlchemyRepository
from db.tables.test_tables import TestBrand, TestCar


class TestCarRepository(SQLAlchemyRepository):
    model = TestCar
    primary_key_name = "uuid"


class TestBrandRepository(SQLAlchemyRepository):
    model = TestBrand
    primary_key_name = "uuid"
