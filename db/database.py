from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, Generator
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession

from core.config import settings
from core.contextvars import db_session_context

async_engine = create_async_engine(
    url=settings.SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
    future=True,
)


async def get_db_session() -> AsyncSession:
    db_session = db_session_context.get()
    if db_session:
        return db_session
    
    db_session = async_session_maker()
    db_session_context.set(db_session)
    try:
        return db_session
    finally:
        await db_session.close()

@asynccontextmanager
async def transaction(session: AsyncSession) -> AsyncGenerator[None, Any, None]:
    if not session.in_transaction():
        async with session.begin():
            yield
    else:
        yield