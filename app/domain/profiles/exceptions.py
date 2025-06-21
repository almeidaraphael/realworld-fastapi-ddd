class ProfileNotFoundError(Exception):
    """Raised when a profile is not found."""


class CannotFollowYourselfError(Exception):
    """Raised when a user tries to follow themselves."""


class UserOrFollowerIdMissingError(Exception):
    """Raised when a user or follower has no id."""
