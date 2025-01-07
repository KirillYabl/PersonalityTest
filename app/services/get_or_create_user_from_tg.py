from dataclasses import dataclass

from db.repositories import UserRepository
from db.repositories.base import SQLAlchemyRepository
from schemas.sqlalchemy import SQLAlchemyOutModel
from telegram_webapp_auth.auth import TelegramUser
from loguru import logger

from schemas.user import CreateUserTgInData, UserIdOut
from selects.user import GetUserByTgIdP, get_user_by_tg_id

@dataclass(frozen=True, kw_only=True, slots=True)
class GetOrCreateUserFromTgService:
    _user_repository: SQLAlchemyRepository = UserRepository()
    _get_user_by_tg_id: GetUserByTgIdP = get_user_by_tg_id

    async def __call__(self, tg_user: TelegramUser, out_model=SQLAlchemyOutModel) -> SQLAlchemyOutModel:
        user = await self._get_user_by_tg_id(user_tg_id=tg_user.id, user_repository=UserRepository())
            
        if not user:
            logger.debug(f"Пользовать с tg_id={tg_user.id} не был найден, создаю пользователя {tg_user=}")
            create_user_data = CreateUserTgInData(tg_user_id=tg_user.id, tg_username=tg_user.username)
            user = await self._user_repository.create(in_data=create_user_data, out_data=out_model)
            logger.debug(f"Создан пользователь tg_id={tg_user.id}, tg_username={tg_user.username}, uuid={str(user.uuid)}")
        return user
    
get_or_create_user_from_tg_s: GetOrCreateUserFromTgService = GetOrCreateUserFromTgService()