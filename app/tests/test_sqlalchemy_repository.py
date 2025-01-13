from typing import ClassVar

import pytest
from pydantic import Field
from sqlalchemy import func
from sqlalchemy.orm import Relationship

from db.database import get_db_session
from db.repositories.base import SQLAlchemyRepository
from resources.schema_constants import ServiceFields
from schemas.sqlalchemy import SQLAlchemyInModel, SQLAlchemyOutModel
from tests.factories.test_factories import TestCarFactory
from tests.test_tables import TestCar


class TestCarRepository(SQLAlchemyRepository):
    model = TestCar
    primary_key_name = "uuid"


class CarIn(SQLAlchemyInModel):
    name: str

    def to_orm(self) -> TestCar:
        return TestCar(
            name=self.name,
        )


class CarOut(SQLAlchemyOutModel):
    relationships: ClassVar[tuple[tuple[Relationship]]] = tuple()

    name: str = Field(..., json_schema_extra={ServiceFields.SORTING_FIELD: TestCar.name})

    def from_orm(model_obj: TestCar) -> "CarOut":
        return CarOut(
            name=model_obj.name,
        )


@pytest.mark.asyncio(loop_scope="session")
async def test_create_row() -> None:
    car_count_query = func.count(TestCar.uuid)
    async with get_db_session() as session:
        result = await session.execute(car_count_query)
        car_count_before = result.scalar()
    await TestCarRepository().create(in_data=CarIn(name="test"), out_data=CarOut)
    async with get_db_session() as session:
        result = await session.execute(car_count_query)
        car_count_after = result.scalar()
    msg = "Количество записей не увеличилось на 1, было {car_count_before}, стало {car_count_after}"
    assert car_count_after == car_count_before + 1, msg


@pytest.mark.asyncio(loop_scope="session")
async def test_get_row_by_id() -> None:
    car = await TestCarFactory.acreate()
    car_obj = await TestCarRepository().get_by_id(id=car.uuid, out_data=CarOut)
    assert car_obj is not None, "Машина не найдена"
    assert car_obj.name == car.name, "Неверное имя машины, ожидается {car.name}, получено {car_obj.name}"
