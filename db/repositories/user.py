from db.tables import User
from db.repositories.base import SQLAlchemyRepository

class UserRepository(SQLAlchemyRepository):
    model = User
    primary_key_name = "uuid"