from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core.config import settings

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
