from sqlmodel import Field, SQLModel


class Follower(SQLModel, table=True):
    follower_id: int = Field(foreign_key="user.id", primary_key=True)
    followee_id: int = Field(foreign_key="user.id", primary_key=True)
