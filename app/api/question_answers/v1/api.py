from uuid import UUID
from fastapi import APIRouter
from loguru import logger

from schemas.sqlalchemy import SQLAlchemyOutModel
from services.get_current_questions_answers import get_current_questions_answers_s

router = APIRouter(
    tags=["Ответы тестов"],
    prefix="/question_answers"
)

@router.get(
    path="/{user_uuid}",
    summary="Получить ответы по последней попытке",
    response_model=list[get_current_questions_answers_s.out_model],
)
async def create_quiz_attempt(user_uuid: UUID) -> list[SQLAlchemyOutModel]:
    result = await get_current_questions_answers_s(user_uuid=user_uuid)
    logger.trace(f"Результаты: {result}")
    return result