from fastapi import APIRouter, Depends

from core.jwt_auth import create_access_token
from core.tg_auth import get_or_create_user_from_tg
from schemas.user import UserIdOut
from schemas.token import Token

router = APIRouter(
    tags=["Аутентификация"],
    prefix="/auth"
)

@router.post(
    path="/token_from_tg",
    summary="Получить JWT токен для пользователей telegram",
    response_model=Token,
)
async def login_tg(user: UserIdOut = Depends(get_or_create_user_from_tg)) -> Token:
    return create_access_token(user=user)