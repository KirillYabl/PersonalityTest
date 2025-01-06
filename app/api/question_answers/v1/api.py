from uuid import UUID
from fastapi import APIRouter
from loguru import logger

from api.question_answers.v1.schema import AnswerCurrentQuestionIn
from schemas.sqlalchemy import SQLAlchemyOutModel
from services.get_current_questions_answers import get_current_questions_answers_s
from services.answer_current_questions import answer_current_questions_s

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

@router.put(
    path="/{user_uuid}",
    summary="Дать ответы по последней попытке",
    response_model=list[get_current_questions_answers_s.out_model],
)
async def answer_current_questions(user_uuid: UUID, answers: list[AnswerCurrentQuestionIn]) -> list[SQLAlchemyOutModel]:
    await answer_current_questions_s(user_uuid=user_uuid, answers=answers)
    result = await get_current_questions_answers_s(user_uuid=user_uuid)
    logger.trace(f"Результаты: {result}")
    return result