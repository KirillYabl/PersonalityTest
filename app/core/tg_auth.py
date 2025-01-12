import http

from fastapi import Depends, HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from telegram_webapp_auth.auth import TelegramAuthenticator, TelegramUser, generate_secret_key
from telegram_webapp_auth.errors import InvalidInitDataError

from core.config import settings
from schemas.user import UserIdOut
from services.get_or_create_user_from_tg import get_or_create_user_from_tg_s

telegram_authentication_schema = HTTPBearer()


async def get_telegram_authenticator() -> TelegramAuthenticator:
    secret_key = generate_secret_key(settings.TELEGRAM_BOT_TOKEN.get_secret_value())
    return TelegramAuthenticator(secret_key)


async def get_tg_user(
    auth_cred: HTTPAuthorizationCredentials = Depends(telegram_authentication_schema),
    telegram_authenticator: TelegramAuthenticator = Depends(get_telegram_authenticator),
) -> TelegramUser:
    try:
        user = telegram_authenticator.verify_token(auth_cred.credentials)
    except InvalidInitDataError:
        raise HTTPException(
            status_code=http.HTTPStatus.FORBIDDEN,
            detail="Forbidden access.",
        )
    except Exception:
        raise HTTPException(
            status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Internal error.",
        )

    return user


async def get_or_create_user_from_tg(tg_user: TelegramUser = Depends(get_tg_user)) -> UserIdOut:
    return await get_or_create_user_from_tg_s(tg_user=tg_user, out_model=UserIdOut)
