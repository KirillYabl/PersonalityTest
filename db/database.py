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
)

@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, Any, None]:
    db_session = db_session_context.get()
    if db_session:
        yield db_session
        return
    
    async with async_session_maker() as db_session:
        try:
            db_session_context.set(db_session)
            yield db_session
        except SQLAlchemyError:
            await db_session.rollback()
            raise
        finally:
            await db_session.close()
            db_session_context.set(None)

@asynccontextmanager
async def transaction(session: AsyncSession) -> AsyncGenerator[None, Any, None]:
    if not session.in_transaction():
        async with session.begin():
            yield
    else:
        yield