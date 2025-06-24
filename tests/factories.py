import secrets

from polyfactory.factories.pydantic_factory import ModelFactory

from app.domain.articles.schemas import ArticleAuthorOut, ArticleCreate
from app.domain.users.schemas import UserRead
from tests.factory_base import fake


class UserReadFactory(ModelFactory[UserRead]):
    __model__ = UserRead

    @classmethod
    def username(cls) -> str:
        base = fake.unique.user_name()
        suffix = secrets.token_hex(4)
        return f"{base}_{suffix}"

    @classmethod
    def email(cls) -> str:
        base = fake.unique.email()
        suffix = secrets.token_hex(4)
        user, domain = base.split("@", 1)
        return f"{user}_{suffix}@{domain}"

    bio: str = ""
    image: str = ""


class ArticleFactory(ModelFactory[ArticleCreate]):
    __model__ = ArticleCreate

    @classmethod
    def title(cls) -> str:
        return fake.unique.sentence(nb_words=4)[:-1]

    @classmethod
    def description(cls) -> str:
        return fake.paragraph(nb_sentences=2)

    @classmethod
    def body(cls) -> str:
        return fake.text(max_nb_chars=200)

    @classmethod
    def tagList(cls) -> list[str]:
        return [fake.word() for _ in range(fake.random_int(min=1, max=3))]


class ArticleAuthorFactory(ModelFactory[ArticleAuthorOut]):
    __model__ = ArticleAuthorOut

    username: str = fake.user_name()
    bio: str = fake.paragraph(nb_sentences=1)
    image: str = fake.image_url()
    following: bool = False
