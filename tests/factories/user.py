from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from db.tables import User

class UserFactory(SQLAlchemyFactory[User]):
    ...
