from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Path
from loguru import logger

from api.question_answers.v1.schema import AnswerCurrentQuestionIn
from core.jwt_auth import get_current_user
from schemas.sqlalchemy import SQLAlchemyOutModel
from schemas.user import UserIdOut
from services.get_current_questions_answers import get_current_questions_answers_s
from services.answer_current_questions import answer_current_questions_s

router = APIRouter(
    tags=["Ответы тестов"],
    prefix="/question_answers"
)

@router.get(
    path="/{quiz_uuid}",
    summary="Получить ответы по последней попытке",
    response_model=list[get_current_questions_answers_s.out_model],
)
async def get_current_quiz_attempt(
    quiz_uuid: Annotated[UUID, Path(title="UUID родительского теста")],
    user: UserIdOut = Depends(get_current_user),
) -> list[SQLAlchemyOutModel]:
    result = await get_current_questions_answers_s(user_uuid=user.uuid, quiz_uuid=quiz_uuid)
    logger.trace(f"Результаты: {result}")
    return result

@router.put(
    path="/{quiz_uuid}",
    summary="Дать ответы по последней попытке",
    response_model=list[get_current_questions_answers_s.out_model],
)
async def answer_current_questions(
    answers: list[AnswerCurrentQuestionIn], 
    quiz_uuid: Annotated[UUID, Path(title="UUID родительского теста")],
    user: UserIdOut = Depends(get_current_user),
) -> list[SQLAlchemyOutModel]:
    await answer_current_questions_s(user_uuid=user.uuid, quiz_uuid=quiz_uuid, answers=answers)
    result = await get_current_questions_answers_s(user_uuid=user.uuid, quiz_uuid=quiz_uuid)
    logger.trace(f"Результаты: {result}")
    return result