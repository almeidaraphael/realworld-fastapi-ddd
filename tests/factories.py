from polyfactory.factories.pydantic_factory import ModelFactory

from app.domain.users.models import User
from tests.factory_base import fake


class UserFactory(ModelFactory[User]):
    __model__ = User

    username = fake.unique.user_name()
    email = fake.unique.email()
    hashed_password = fake.password()
    bio: str = ""
    image: str = ""
