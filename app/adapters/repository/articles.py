from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.articles.models import Article


class ArticleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, article: Article) -> Article:
        self.session.add(article)
        await self.session.commit()
        await self.session.refresh(article)
        return article

    async def get_by_slug(self, slug: str) -> Article | None:
        result = await self.session.exec(select(Article).where(Article.slug == slug))
        return result.first()
