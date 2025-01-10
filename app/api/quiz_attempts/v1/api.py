from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, BackgroundTasks
from loguru import logger

from api.quiz_attempts.v1.schema import CreateQuizAttemptIn
from core.jwt_auth import get_current_user
from schemas.sqlalchemy import SQLAlchemyOutModel
from schemas.user import UserIdOut
from services.create_quiz_attempt import create_quiz_attempt_s
from services.complete_quiz_current_attempt import complete_quiz_current_attempt_s
from services.calculate_quiz_result import calculate_quiz_result_s

router = APIRouter(
    tags=["Попытки прохождения тестов"],
    prefix="/quiz_attempts"
)

@router.post(
    path="",
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

@router.post(
    path="/current/complete/{quiz_uuid}",
    summary="Закончить прохождение теста по последней попытке",
    response_model=complete_quiz_current_attempt_s.out_model,
)
async def complete_quiz_current_attempt(
    quiz_uuid: Annotated[UUID, Path(title="UUID теста")],
    background_tasks: BackgroundTasks,
    user: UserIdOut = Depends(get_current_user),
) -> list[SQLAlchemyOutModel]:
    result = await complete_quiz_current_attempt_s(quiz_uuid=quiz_uuid, user_uuid=user.uuid)
    background_tasks.add_task(calculate_quiz_result_s, result_uuid=result.uuid)
    logger.trace(f"Результаты: {result}")
    return result