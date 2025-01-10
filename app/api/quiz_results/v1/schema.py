from uuid import UUID
from pydantic import BaseModel

from resources.schema_constants import QuizTypeName
from schemas.quiz_result import QuizResultOut


class PersonalityTestResultOut(BaseModel):
    uuid: UUID
    attempt_uuid: UUID
    status: str
    character_result: dict[str, float]
    apprecation_result: list[str]
    values_result: list[str]

    @classmethod
    def from_quiz_result(cls, quiz_result: QuizResultOut) -> "PersonalityTestResultOut":
        return cls(
            uuid=quiz_result.uuid,
            attempt_uuid=quiz_result.attempt_id,
            status=quiz_result.data.get("status"),
            character_result=quiz_result.data.get(QuizTypeName.PERSONALITY_CHARACTER),
            apprecation_result=quiz_result.data.get(QuizTypeName.PERSONALITY_APPRECATION),
            values_result=quiz_result.data.get(QuizTypeName.PERSONALITY_VALUES),
        )