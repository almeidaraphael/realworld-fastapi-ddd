"""
SQLAlchemy ORM mapping for Tag domain models.

This module contains the SQLAlchemy mappings for tag domain models.

Note: Tags are currently stored as arrays within articles (tagList column)
rather than as separate database entities. This ORM file is provided for
architectural consistency but doesn't contain actual mappings since tags
don't have their own table.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import registry

metadata = MetaData()
mapper_registry = registry()

# Tags are currently stored as ARRAY(String) in the article table's tagList column
# rather than as separate entities with their own table. If tags were to become
# separate entities in the future, the mapping would look like:
#
# tag_table = Table(
#     "tag",
#     metadata,
#     Column("id", Integer, primary_key=True),
#     Column("name", String, unique=True, nullable=False),
#     Column("usage_count", Integer, default=0),
# )
#
# mapper_registry.map_imperatively(Tag, tag_table)
