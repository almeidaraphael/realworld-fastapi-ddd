from datetime import datetime, timezone

from slugify import slugify

from app.adapters.orm.unit_of_work import AsyncUnitOfWork
from app.adapters.repository.articles import ArticleRepository
from app.domain.articles.models import Article
from app.domain.articles.schemas import ArticleCreateRequest
from app.domain.users.schemas import UserWithToken


async def create_article(article: ArticleCreateRequest, user: UserWithToken):
    async with AsyncUnitOfWork() as uow:
        repo = ArticleRepository(uow.session)
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        slug = slugify(article.title)
        db_article = Article(
            slug=slug,
            title=article.title,
            description=article.description,
            body=article.body,
            tagList=article.tagList or [],
            author_id=user.id,
            created_at=now,
            updated_at=now,
        )
        created = await repo.add(db_article)
        # Build response dict as required by API schema
        return {
            "article": {
                "slug": created.slug,
                "title": created.title,
                "description": created.description,
                "body": created.body,
                "tagList": created.tagList,
                "createdAt": created.created_at,
                "updatedAt": created.updated_at,
                "favorited": False,
                "favoritesCount": 0,
                "author": {
                    "username": user.username,
                    "bio": user.bio or "",
                    "image": user.image or "",
                    "following": False,
                },
            }
        }
