from uuid import UUID
from pydantic import BaseModel, Field

class AnswerCurrentQuestionIn(BaseModel):
    question_uuid: UUID = Field(..., title="UUID вопроса")
    value: bool | str | int = Field(..., title="Ответ")
