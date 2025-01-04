from contextvars import ContextVar

from sqlalchemy.ext.asyncio.session import AsyncSession


db_session_context: ContextVar[AsyncSession | None] = ContextVar("db_session", default=None)
query_count_context: ContextVar[int] = ContextVar("query_count", default=0)