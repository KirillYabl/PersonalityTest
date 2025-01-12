from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Response, status
from loguru import logger

from api.quiz_results.v1.schema import PersonalityTestResultOut
from core.jwt_auth import get_current_user
from schemas.user import UserIdOut
from services.get_quiz_result import get_quiz_result_s

router = APIRouter(tags=["Результаты тестов"], prefix="/quiz_results")


@router.get(
    path="/{quiz_result_uuid}",
    summary="Получить результат прохождения теста",
    response_model=PersonalityTestResultOut,
)
async def get_quiz_result(
    response: Response,
    quiz_result_uuid: Annotated[UUID, Path(title="UUID результата теста")],
    user: UserIdOut = Depends(get_current_user),
) -> PersonalityTestResultOut:
    calculated, quiz_result = await get_quiz_result_s(quiz_result_uuid=quiz_result_uuid)
    logger.trace(f"Результаты: {quiz_result}")
    if not calculated:
        response.status_code = status.HTTP_202_ACCEPTED
    return PersonalityTestResultOut.from_quiz_result(quiz_result)
