class UserAlreadyExistsError(Exception):
    """Raised when a user with the given username or email already exists."""


class UserNotFoundError(Exception):
    """Raised when a user is not found."""
