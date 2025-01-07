from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError

from core.config import settings
from schemas.user import UserIdOut
from schemas.token import Token

security = HTTPBearer()

def create_access_token(user: UserIdOut) -> Token:
    expire = datetime.now(timezone.utc) + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    to_encode = {
        "sub": str(user.uuid),
        "exp": int(expire.timestamp()),
    }
    encoded_jwt = jwt.encode(to_encode, settings.APP_SECRET_KEY.get_secret_value(), algorithm=settings.ACCESS_TOKEN_ALGORITHM)
    return Token(access_token=encoded_jwt)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserIdOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.APP_SECRET_KEY.get_secret_value(), algorithms=[settings.ACCESS_TOKEN_ALGORITHM])
        user_uuid: str = payload.get("sub")
    except InvalidTokenError:
        raise credentials_exception
    
    return UserIdOut(uuid=user_uuid)