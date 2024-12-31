from typing import ClassVar

from db.tables.base import BaseModel

class SQLAlchemyModel:
    """Модель служебных полей для pydantic при использовании SQLAlchemy."""
    joinedload_models: ClassVar[tuple[BaseModel]]  # Список моделей, которые нужно подгружать при запросах для избегания n+1