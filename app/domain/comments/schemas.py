from pydantic import BaseModel


class CommentCreate(BaseModel):
    """Schema for creating a new comment."""

    body: str


class CommentCreateRequest(BaseModel):
    """Request wrapper for comment creation."""

    comment: CommentCreate


class CommentAuthor(BaseModel):
    """Author information for comment responses."""

    username: str
    bio: str = ""
    image: str = ""
    following: bool = False


class CommentOut(BaseModel):
    """Comment response schema."""

    id: int
    createdAt: str
    updatedAt: str
    body: str
    author: CommentAuthor


class CommentResponse(BaseModel):
    """Single comment response wrapper."""

    comment: CommentOut


class CommentsResponse(BaseModel):
    """Multiple comments response wrapper."""

    comments: list[CommentOut]
