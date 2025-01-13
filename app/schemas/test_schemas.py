from typing import ClassVar
from uuid import UUID

from pydantic import Field
from sqlalchemy.orm import Relationship

from db.tables.test_tables import TestBrand, TestCar
from resources.schema_constants import ServiceFields
from schemas.sqlalchemy import SQLAlchemyInModel, SQLAlchemyOutModel


class CarIn(SQLAlchemyInModel):
    name: str

    def to_orm(self) -> TestCar:
        return TestCar(
            name=self.name,
        )


class BrandIn(SQLAlchemyInModel):
    name: str

    def to_orm(self) -> TestBrand:
        return TestBrand(
            name=self.name,
        )


class CarOut(SQLAlchemyOutModel):
    relationships: ClassVar[tuple[tuple[Relationship]]] = tuple()

    name: str = Field(..., json_schema_extra={ServiceFields.SORTING_FIELD: TestCar.name})

    @classmethod
    def from_orm(cls, model_obj: TestCar) -> "CarOut":
        return cls(
            name=model_obj.name,
        )


class BrandOut(SQLAlchemyOutModel):
    relationships: ClassVar[tuple[tuple[Relationship]]] = tuple()

    uuid: UUID = Field(..., json_schema_extra={ServiceFields.SORTING_FIELD: TestBrand.uuid})
    name: str = Field(..., json_schema_extra={ServiceFields.SORTING_FIELD: TestBrand.name})

    @classmethod
    def from_orm(cls, model_obj: TestCar) -> "BrandOut":
        return cls(
            uuid=model_obj.uuid,
            name=model_obj.name,
        )


class CarBrandOut(SQLAlchemyOutModel):
    relationships: ClassVar[tuple[tuple[Relationship]]] = ((TestCar.brand,),)

    uuid: UUID = Field(..., json_schema_extra={ServiceFields.SORTING_FIELD: TestCar.uuid})
    name: str = Field(..., json_schema_extra={ServiceFields.SORTING_FIELD: TestCar.name})
    brand_name: str = Field(..., json_schema_extra={ServiceFields.SORTING_FIELD: TestBrand.name})

    @classmethod
    def from_orm(cls, model_obj: TestCar) -> "CarBrandOut":
        return cls(
            uuid=model_obj.uuid,
            name=model_obj.name,
            brand_name=model_obj.brand.name,
        )
