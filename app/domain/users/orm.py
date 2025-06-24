"""
SQLAlchemy ORM mapping for User and Follower domain models.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import registry

from app.domain.users.models import Follower, User
from app.shared.metadata import metadata

mapper_registry = registry()

user_table = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String, unique=True, nullable=False),
    Column("email", String, unique=True, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("bio", Text, default=""),
    Column("image", String, default=""),
)

follower_table = Table(
    "follower",
    metadata,
    Column("follower_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("followee_id", Integer, ForeignKey("user.id"), primary_key=True),
)

mapper_registry.map_imperatively(User, user_table)
mapper_registry.map_imperatively(Follower, follower_table)
