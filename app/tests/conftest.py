import asyncio
from collections.abc import Generator
from typing import Any

import pytest
import pytest_asyncio

from db.database import async_engine
from db.tables.base import BaseModel


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, Any, None]:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True, loop_scope="session")
async def setup_and_teardown_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)
    await async_engine.dispose()
