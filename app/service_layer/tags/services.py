"""Tags service layer."""

from app.adapters.orm.unit_of_work import AsyncUnitOfWork
from app.adapters.repository.tags import TagsRepository
from app.shared.transaction import transactional


@transactional()
async def get_tags(uow: AsyncUnitOfWork) -> list[str]:
    """
    Get all unique tags from articles in the system.

    Returns:
        A list of unique tag strings sorted alphabetically.
    """
    tags_repo = TagsRepository(uow.session)
    return await tags_repo.get_all_tags()


# Keep original function for backward compatibility during migration
async def get_tags_original() -> list[str]:
    """Original get_tags function - kept for backward compatibility."""
    async with AsyncUnitOfWork() as uow:
        tags_repo = TagsRepository(uow.session)
        return await tags_repo.get_all_tags()
