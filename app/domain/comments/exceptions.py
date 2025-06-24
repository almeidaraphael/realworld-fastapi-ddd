class CommentNotFoundError(Exception):
    """Raised when a comment is not found."""


class CommentPermissionError(Exception):
    """Raised when a user doesn't have permission to delete a comment."""
