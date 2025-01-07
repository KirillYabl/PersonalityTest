from fastapi import APIRouter, Depends
from loguru import logger

from api.quiz_attempts.v1.schema import CreateQuizAttemptIn
from core.jwt_auth import get_current_user
from schemas.sqlalchemy import SQLAlchemyOutModel
from schemas.user import UserIdOut
from services.create_quiz_attempt import create_quiz_attempt_s

router = APIRouter(
    tags=["Попытки прохождения тестов"],
    prefix="/quiz_attempts"
)

@router.post(
    path="/",
    summary="Создать попытку прохождения теста для юзера",
    response_model=create_quiz_attempt_s.out_model,
)
async def create_quiz_attempt(
    data: CreateQuizAttemptIn,
    user: UserIdOut = Depends(get_current_user),
) -> list[SQLAlchemyOutModel]:
    result = await create_quiz_attempt_s(quiz_id=data.quiz_uuid, user_id=user.uuid)
    logger.trace(f"Результаты: {result}")
    return result