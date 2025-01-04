from collections.abc import Callable
from functools import wraps
from contextvars import ContextVar
from typing import Any

from loguru import logger
from sqlalchemy import event

from db.database import get_db_session
from core.contextvars import query_count_context

def count_queries(func) -> Callable:
    @wraps(func)
    async def wrapped(*args, **kwargs) -> Any:
        query_count_context.set(0)

        def count_queries_handler(*_) -> None:
            query_count = query_count_context.get()
            query_count_context.set(query_count + 1)

        async with get_db_session() as session:
            event.listen(session.sync_session.bind, "after_cursor_execute", count_queries_handler)

            try:
                result = await func(*args, **kwargs)
            finally:
                event.remove(session.sync_session.bind, "after_cursor_execute", count_queries_handler)

                query_count = query_count_context.get()
                logger.debug(f"{func.__module__}.{func.__qualname__}: {query_count} запросов")

            return result

    return wrapped
