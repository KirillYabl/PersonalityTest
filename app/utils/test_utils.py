from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from db.database import get_db_session, transaction
from db.tables.base import BaseModel


async def create_and_get(factory: SQLAlchemyFactory, **kwargs) -> BaseModel:
    """Создать и вернуть объект фабрикой.

    Это работает лучше __async_session__ в фабрике, т.к. __async_session__
    не закрывает сессию и появляются варнинги и ошибки

    :param factory: фабрика
    :return: объект SQLAlchemy
    """
    obj = factory.build(**kwargs)
    async with get_db_session() as session:
        async with transaction(session=session):
            session.add(obj)
            await session.flush()
            return obj


class SQLAlchemyFactoryMixin:
    @classmethod
    async def acreate(cls, **kwargs) -> BaseModel:
        return await create_and_get(factory=cls, **kwargs)
