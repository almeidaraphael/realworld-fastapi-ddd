"""Tags service layer."""

from app.adapters.orm.unit_of_work import AsyncUnitOfWork
from app.adapters.repository.tags import TagsRepository


async def get_tags() -> list[str]:
    """
    Get all unique tags from articles in the system.

    Returns:
        A list of unique tag strings sorted alphabetically.
    """
    async with AsyncUnitOfWork() as uow:
        tags_repo = TagsRepository(uow.session)
        return await tags_repo.get_all_tags()
