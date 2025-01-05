from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Path

from schemas.sqlalchemy import SQLAlchemyOutModel
from services.get_quiz_questions import get_quiz_questions_s
from loguru import logger

router = APIRouter(
    tags=["Вопросы тестов"],
    prefix="/questions"
)

@router.get(
    path="/{quiz_uuid}",
    summary="Получить все вопросы теста (включая вопросы дочерних тестов)",
    response_model=list[get_quiz_questions_s.out_model],
)
async def get_quiz_questions(
    quiz_uuid: Annotated[UUID, Path(title="UUID родительского теста")],
) -> list[SQLAlchemyOutModel]:
    result = await get_quiz_questions_s(quiz_id=quiz_uuid)
    logger.trace(f"Результаты: {result}")
    return result