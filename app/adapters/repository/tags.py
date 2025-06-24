"""Tags repository for data access operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.articles.orm import article_table


class TagsRepository:
    """Repository for tag-related database operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with a database session."""
        self.session = session

    async def get_all_tags(self) -> list[str]:
        """
        Get all unique tags from all articles in the system.

        Returns:
            A list of unique tag strings.
        """
        # Get all articles and extract unique tags from their tagList
        query = select(article_table.c.tagList)
        result = await self.session.execute(query)
        tag_lists = result.scalars().all()

        # Flatten all tag lists and get unique tags
        all_tags: set[str] = set()
        for tag_list in tag_lists:
            if tag_list:  # tag_list could be None or empty
                for tag in tag_list:
                    if tag.strip():  # Only add non-empty tags
                        all_tags.add(tag.strip())

        return sorted(list(all_tags))  # Return sorted list for consistency
