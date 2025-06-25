"""
SQLAlchemy ORM mapping for Profile domain model (if needed).
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import registry

metadata = MetaData()
mapper_registry = registry()

# Profile is a view on User data, so no separate table mapping is needed.
# If Profile were to become a separate entity in the future, the mapping would look like:
#
# from app.domain.profiles.models import Profile
#
# profile_table = Table(
#     "profile",
#     metadata,
#     Column("id", Integer, primary_key=True),
#     Column("username", String, unique=True, nullable=False),
#     Column("bio", Text, default=""),
#     Column("image", String, default=""),
#     Column("user_id", Integer, ForeignKey("user.id"), nullable=False),
# )
#
# mapper_registry.map_imperatively(Profile, profile_table)

# Since Profile is just a view on User, no separate ORM mapping is needed.
