"""
SQLAlchemy ORM mapping for Profile domain model (if needed).
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import registry

metadata = MetaData()
mapper_registry = registry()

# Example: If you want to map a Profile, define the table and mapping here.
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
# class Profile:
#     id: int
#     username: str
#     bio: str
#     image: str
#     user_id: int
#
# mapper_registry.map_imperatively(Profile, profile_table)

# If Profile is just a view on User, you may not need a separate ORM mapping.
