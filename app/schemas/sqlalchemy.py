from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, ClassVar

from sqlalchemy.orm import Relationship
from pydantic import BaseModel

from db.tables.base import BaseModel as SQLBaseModel
from resources.schema_constants import ServiceFields

class RemoveServiceFieldsMixin:
    """Миксин удаления служебных полей из схемы pydantic для успешной сериализации."""
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler, /,):
        core_schema = cls._remove_service_fields_from_pydantic_core_schema(core_schema)
        return super().__get_pydantic_json_schema__(core_schema, handler)
    
    @staticmethod
    def _remove_service_fields_from_pydantic_core_schema(d: dict) -> dict[str, Any]:
        result = {}

        stack = [(result, d)]
        
        while stack:
            current_result, current = stack.pop()
            
            if isinstance(current, dict):
                for key, value in current.items():
                    if key not in ServiceFields.values():
                        if isinstance(value, (dict, list)):
                            new_value = {} if isinstance(value, dict) else []
                            current_result[key] = new_value
                            stack.append((new_value, value))
                        else:
                            current_result[key] = value
            elif isinstance(current, list):
                for i, item in enumerate(current):
                    if isinstance(item, (dict, list)):
                        new_item = {} if isinstance(item, dict) else []
                        current_result.append(new_item)
                        stack.append((new_item, item))
                    else:
                        current_result.append(item)
        return result  

class SQLAlchemyOutModel(RemoveServiceFieldsMixin, BaseModel, ABC):
    """Модель служебных полей для pydantic при использовании SQLAlchemy."""

    # Кортеж кортежей связей, которые нужно подгружать при запросах для избегания n+1, порядок важен
    # вложенный кортеж для вложенных связей, например User.groups -> Group.permisiions
    relationships: ClassVar[tuple[tuple[Relationship]]]

    @classmethod
    @abstractmethod
    def from_orm(cls, model_obj: SQLBaseModel) -> "SQLAlchemyOutModel":
        ...
    
class SQLAlchemyInModel(RemoveServiceFieldsMixin, BaseModel, ABC):
    @abstractmethod
    def to_orm(self) -> SQLBaseModel:
        ...