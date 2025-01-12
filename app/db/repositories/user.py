from db.repositories.base import SQLAlchemyRepository
from db.tables import User


class UserRepository(SQLAlchemyRepository):
    model = User
    primary_key_name = "uuid"
