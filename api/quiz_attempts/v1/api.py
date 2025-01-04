from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Path

from api.quiz_attempts.v1.schema import CreateQuizAttemptIn
from schemas.sqlalchemy import SQLAlchemyOutModel
from services.create_quiz_attempt import create_quiz_attempt_s
from loguru import logger

router = APIRouter(
    tags=["Попытки прохождения тестов"],
    prefix="/quiz_attempts"
)

@router.post(
    path="/",
    summary="Создать попытку прохождения теста для юзера",
    response_model=create_quiz_attempt_s.out_model,
)
async def create_quiz_attempt(data: CreateQuizAttemptIn) -> list[SQLAlchemyOutModel]:
    result = await create_quiz_attempt_s(quiz_id=data.quiz_uuid, tg_user_id=data.tg_user_id)
    logger.trace(f"Результаты: {result}")
    return result