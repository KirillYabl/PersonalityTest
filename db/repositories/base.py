from typing import TypeVar
from collections.abc import Iterable, Mapping
from abc import ABC, abstractmethod
from venv import logger

from sqlalchemy import BinaryExpression, BooleanClauseList, desc, select, update, delete
from sqlalchemy.orm import joinedload, aliased
from pydantic import BaseModel

from resources.schema_constants import ServiceFields
from schemas.sqlalchemy import SQLAlchemyInModel, SQLAlchemyOutModel
from db.database import get_db_session, get_db_session, transaction
from db.tables.base import BaseModel as SQLBaseModel

InData = TypeVar("InData")  # входные данные (список фильтров или значения полей и т.д.)
OutData = TypeVar("InData")  # модель, в которой отдавать данные
Id = TypeVar("Id")

class BaseRepository(ABC):
    """
    Базовый репозиторий.
    
    Для всех методов пользователь указывает, в какой модели возвращать данные.
    Так можно не писать методы под каждый возвращаемый тип данных, а определять 
    способ преобразования в схеме.
    При этом в схеме может быть например указано, что такие-то модели еще нужно 
    подгрузить для избегания N+1 и репозиторий поймет что делать.
    """

    @abstractmethod
    async def create(self, in_data: InData, out_data: OutData, **kwargs) -> OutData:
        """Создать запись."""

    @abstractmethod
    async def create_many(self, in_datas: Iterable[InData], out_data: OutData, **kwargs) -> Iterable[OutData]:
        """Создать много записей."""

    @abstractmethod
    async def update_one(self, id: Id, in_data: InData, out_data: OutData, **kwargs) -> OutData:
        """Обновить одну запись.
        
        Идентификатор передается отдельно, т.к. это не данные для обновления.
        """

    @abstractmethod
    async def update_many(self, in_data: Mapping[Id, InData], out_data: OutData, **kwargs) -> Iterable[OutData]:
        """Обновить множество записей.
        
        Идентификатор передается отдельно, т.к. это не данные для обновления.
        """

    @abstractmethod
    async def update_same_many(self, ids: Iterable[Id], in_data: InData, out_data: OutData, **kwargs) -> Iterable[OutData]:
        """Обновить множество записей одинаковыми полями."""

    @abstractmethod
    async def delete_by_ids(self, ids: Iterable[Id], **kwargs) -> None:
        """Удалить множество записей по идентификаторам."""

    @abstractmethod
    async def get_by_id(self, id: Id, out_data: OutData, **kwargs) -> OutData | None:
        """Получить одну запись по идентификатру."""

    @abstractmethod
    async def get_many(self, filter: InData, out_data: OutData, **kwargs) -> Iterable[OutData]:
        """Получить множество записей по фильтру."""


class SQLAlchemyRepository(BaseRepository):
    model: SQLBaseModel

    # TODO: поддержка композитного первичного ключа или его отсутствия
    primary_key_name: str

    async def create(self, in_data: SQLAlchemyInModel, out_data: SQLAlchemyOutModel, **kwargs) -> SQLAlchemyOutModel:
        session = await get_db_session()
        obj = in_data.to_orm()

        async with transaction(session=session):
            session.add(obj)
            await session.flush()
            id = getattr(obj, self.primary_key_name)

        return await self.get_by_id(id=id, out_data=out_data)
    
    async def create_many(self, in_datas: Iterable[InData], out_data: OutData, **kwargs) -> Iterable[OutData]:
        pass
        
    async def update_one(self, id: Id, in_data: BaseModel, out_data: SQLAlchemyOutModel, **kwargs) -> SQLAlchemyOutModel:
        session = await get_db_session()
        stmt = update(self.model).where(getattr(self.model, self.primary_key_name)==id).values(**in_data.model_dump())

        async with transaction(session=session):
            await session.execute(statement=stmt)

        return await self.get_by_id(id=id, out_data=out_data)

    async def update_many(self, in_data: Mapping[Id, InData], out_data: OutData, **kwargs) -> Iterable[OutData]:
        pass

    async def update_same_many(self, ids: Iterable[Id], in_data: InData, out_data: OutData, **kwargs) -> Iterable[OutData]:
        pass

    async def delete_by_ids(self, ids: Iterable[Id], **kwargs) -> None:
        session = await get_db_session()
        stmt = delete(self.model).filter(getattr(self.model, self.primary_key_name).in_(list(ids)))
        async with transaction(session=session):
            await session.execute(statement=stmt)


    async def get_by_id(self, id: Id, out_data: SQLAlchemyOutModel, **kwargs) -> SQLAlchemyOutModel | None:
        results = await self.get_many(getattr(self.model, self.primary_key_name) == id, out_data=out_data)
        return results[0] if results else None

    async def get_many(
            self, 
            *filters: BooleanClauseList | BinaryExpression,  # TODO: сделать универсально через out_data
            out_data: SQLAlchemyOutModel, 
            order_by: tuple[str] = tuple(),
            limit: int | None = None,
            offset: int | None = None,
        ) -> list[OutData]:
        """Получить много записей по фильтру.

        :param filters: перечень условий для фильтрации в таком же виде, как они передаются в filter в sqlalchemy
        :param out_data: класс, в котором укзано какие поля возвращать обратно и какие модели подгружать
        :param order_by: перечень полей для фильтрации
        
            Допустимый выбор это строковое название одного из полей из out_data. 
            Там задана правило, как сортировать поле.
            Можно указывать знак "-" перед полем, это значит desc сортировка.
        :param limit: limit из SQL
        :param offset: offset из SQL
        :return: список моделей типа out_data, удовлетворяющих фильтрации
        """        
        session = await get_db_session()
        stmt = select(self.model).filter(*filters)

        relationship_models = {}
        for relationships in out_data.relationships:
            for relationship in relationships:
                relationship_models[relationship.property.mapper.class_.__name__] = relationship.property.mapper.class_

        if order_by:
            sorting_fields = []
            for column_name in order_by:
                descending = False
                if column_name.startswith("-"):
                    column_name = column_name[1:]
                    descending = True
                
                out_data_column = out_data.model_fields.get(column_name)
                if out_data_column is None:
                    logger.warning(f"Не удалось сделать сортировку по {column_name} т.к. не найдено в модели")
                    continue
                
                has_json_schema = hasattr(out_data_column, "json_schema_extra")
                sorting_field = None
                if has_json_schema:
                    sorting_field = out_data_column.json_schema_extra.get(ServiceFields.SORTING_FIELD)

                if sorting_field is None:
                    logger.warning(f"Не удалось сделать сортировку по {column_name} т.к. в модели не заданы правила сортировки")
                    continue

                if descending:
                    sorting_field = desc(sorting_field)

                sorting_fields.append(sorting_field)
            stmt = stmt.order_by(*sorting_fields)

        if limit is not None:
            stmt = stmt.limit(limit)

        if offset is not None:
            stmt = stmt.offset(offset)

        if out_data.relationships:
            for sub_relationships in out_data.relationships:
                joins = [[relationship_models[sub_relationships[0].property.mapper.class_.__name__], sub_relationships[0]]]
                options = joinedload(sub_relationships[0])
                for sub_relationship in sub_relationships[1:]:
                    options = options.joinedload(sub_relationship)
                    joins.append([relationship_models[sub_relationship.property.mapper.class_.__name__], sub_relationship])
                stmt = stmt.options(options)
                for j in joins:
                    stmt = stmt.join(*j)

        result = await session.execute(statement=stmt)

        return [out_data.from_orm(model_obj=row[0]) for row in result.fetchall()]
