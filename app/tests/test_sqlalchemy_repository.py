import pytest
from sqlalchemy import func

from db.database import get_db_session
from db.repositories.test_repositories import TestBrandRepository, TestCarRepository
from db.tables.test_tables import TestBrand, TestCar
from schemas.test_schemas import BrandIn, BrandOut, CarBrandOut
from tests.factories.test_factories import TestBrandFactory, TestCarFactory


@pytest.mark.asyncio(loop_scope="session")
async def test_create_row() -> None:
    count_query = func.count(TestBrand.uuid)
    async with get_db_session() as session:
        result = await session.execute(count_query)
        count_before = result.scalar()
    obj = await TestBrandRepository().create(in_data=BrandIn(name="test"), out_data=BrandOut)
    assert isinstance(obj, BrandOut)
    async with get_db_session() as session:
        result = await session.execute(count_query)
        count_after = result.scalar()
    assert count_after == count_before + 1


@pytest.mark.asyncio(loop_scope="session")
async def test_get_row_by_id() -> None:
    frow = await TestBrandFactory.acreate()
    rrow = await TestBrandRepository().get_by_id(id=frow.uuid, out_data=BrandOut)
    assert rrow is not None
    assert isinstance(rrow, BrandOut)
    assert rrow.name == frow.name


@pytest.mark.asyncio(loop_scope="session")
async def test_get_row_by_id_with_rel() -> None:
    frow = await TestCarFactory.acreate()
    rrow = await TestCarRepository().get_by_id(id=frow.uuid, out_data=CarBrandOut)
    assert rrow is not None
    assert isinstance(rrow, CarBrandOut)
    assert rrow.name == frow.name
    assert rrow.brand_name == frow.brand.name


@pytest.mark.asyncio(loop_scope="session")
async def test_get_many_rows_count() -> None:
    count = 2
    ids = []
    for _ in range(count):
        frow = await TestBrandFactory.acreate()
        ids.append(frow.uuid)
    rows = await TestBrandRepository().get_many(TestBrand.uuid.in_(ids), out_data=BrandOut)
    assert len(rows) == count
    assert all(isinstance(row, BrandOut) for row in rows)
    assert all(row.uuid in ids for row in rows)


@pytest.mark.asyncio(loop_scope="session")
async def test_get_many_order() -> None:
    count = 2
    ids = []
    frows = []
    for _ in range(count):
        frow = await TestCarFactory.acreate()
        ids.append(frow.uuid)
        frows.append(frow)

    rows = await TestCarRepository().get_many(TestCar.uuid.in_(ids), out_data=CarBrandOut, order_by=["brand_name"])
    assert len([row.brand.name for row in frows]) == len(set(row.brand_name for row in rows))
    assert [row.brand.name for row in sorted(frows, key=lambda x: x.brand.name)] == [row.brand_name for row in rows]

    rows = await TestCarRepository().get_many(TestCar.uuid.in_(ids), out_data=CarBrandOut, order_by=["-brand_name"])
    assert len([row.brand.name for row in frows]) == len(set(row.brand_name for row in rows))
    assert [row.brand.name for row in sorted(frows, key=lambda x: x.brand.name, reverse=True)] == [
        row.brand_name for row in rows
    ]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_many_order_few_fields() -> None:
    pairs = 2
    count_in_pair = 2
    ids = []
    frows = []
    brand_names = []
    brand_name_names_pairs = []
    for _ in range(pairs):
        brand = await TestBrandFactory.acreate()
        brand_names.append(brand.name)
        for _ in range(count_in_pair):
            frow = await TestCarFactory.acreate(brand=brand)
            ids.append(frow.uuid)
            frows.append(frow)
            brand_name_names_pairs.append((brand.name, frow.name))

    rows = await TestCarRepository().get_many(
        TestCar.uuid.in_(ids), out_data=CarBrandOut, order_by=["-brand_name", "name"]
    )
    assert len(set(row.brand_name for row in rows)) == pairs

    sorted_brand_name_brand_pairs = []
    for brand_name in sorted(brand_names, reverse=True):
        pairs_with_brand_name = [pair for pair in brand_name_names_pairs if pair[0] == brand_name]
        sorted_brand_name_brand_pairs += sorted(pairs_with_brand_name)

    assert sorted_brand_name_brand_pairs == [(row.brand_name, row.name) for row in rows]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_many_offset_limit() -> None:
    limit = 1
    offset = 1
    count = 2
    ids = []
    frows = []
    for _ in range(count):
        frow = await TestBrandFactory.acreate()
        ids.append(frow.uuid)
        frows.append(frow)
    ids = sorted(ids)

    rows = await TestBrandRepository().get_many(
        TestBrand.uuid.in_(ids),
        out_data=BrandOut,
        limit=limit,
        offset=offset,
        order_by=["uuid"],
    )
    assert len(rows) == limit
    assert rows[0].uuid == ids[offset]
