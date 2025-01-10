from enum import StrEnum

from utils.resourcesutils import EnumValuesMixin

class ServiceFields(EnumValuesMixin, StrEnum):
    """Дополнительные поля в моделях и служебные, их не нужно сериализовывать и они могут быть несериализуемые."""
    SORTING_FIELD = "sorting_field"

class ResultStatus:
    PENDING = "PENDING"
    IN_PROCESS = "IN_PROCESS"
    ERROR = "ERROR"
    DONE = "DONE"

class QuizTypeName:
    PERSONALITY_CHARACTER = "PersonalityCharacterTest"
    PERSONALITY_APPRECATION = "PersonalityApprecationTest"
    PERSONALITY_VALUES = "PersonalityValuesTest"