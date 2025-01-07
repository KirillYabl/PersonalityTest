from uuid import UUID
from pydantic import BaseModel, Field

class CreateQuizAttemptIn(BaseModel):
    quiz_uuid: UUID = Field(..., title="UUID родительского теста")