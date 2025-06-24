"""
Test the standardized exception handling across domains.
"""

from fastapi import HTTPException, status

from app.domain.articles.exceptions import (
    ArticleNotFoundError,
    ArticlePermissionError,
    ArticleSlugConflictError,
    InvalidArticleDataError,
)
from app.domain.comments.exceptions import CommentNotFoundError, CommentPermissionError
from app.domain.profiles.exceptions import (
    CannotFollowYourselfError,
    ProfileNotFoundError,
    UserOrFollowerIdMissingError,
)
from app.domain.users.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.shared.exceptions import (
    AuthenticationError,
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionError,
    ValidationError,
    get_http_status_code,
    translate_domain_error_to_http,
)


class TestExceptionHierarchy:
    """Test that all domain exceptions inherit from correct base classes."""

    def test_user_exceptions_inherit_from_base_classes(self):
        """
        GIVEN domain user exceptions
        WHEN checked for inheritance
        THEN they inherit from correct base classes.
        """
        assert issubclass(UserAlreadyExistsError, ConflictError)
        assert issubclass(UserNotFoundError, NotFoundError)
        assert issubclass(InvalidCredentialsError, AuthenticationError)

    def test_profile_exceptions_inherit_from_base_classes(self):
        """
        GIVEN domain profile exceptions
        WHEN checked for inheritance
        THEN they inherit from correct base classes.
        """
        assert issubclass(ProfileNotFoundError, NotFoundError)
        assert issubclass(CannotFollowYourselfError, ValidationError)
        assert issubclass(UserOrFollowerIdMissingError, ValidationError)

    def test_article_exceptions_inherit_from_base_classes(self):
        """
        GIVEN domain article exceptions
        WHEN checked for inheritance
        THEN they inherit from correct base classes.
        """
        assert issubclass(ArticleNotFoundError, NotFoundError)
        assert issubclass(ArticlePermissionError, PermissionError)
        assert issubclass(ArticleSlugConflictError, ConflictError)
        assert issubclass(InvalidArticleDataError, ValidationError)

    def test_comment_exceptions_inherit_from_base_classes(self):
        """
        GIVEN domain comment exceptions
        WHEN checked for inheritance
        THEN they inherit from correct base classes.
        """
        assert issubclass(CommentNotFoundError, NotFoundError)
        assert issubclass(CommentPermissionError, PermissionError)


class TestHttpStatusMapping:
    """Test that domain exceptions map to correct HTTP status codes."""

    def test_not_found_error_maps_to_404(self):
        """GIVEN NotFoundError WHEN getting HTTP status THEN returns 404."""
        error = UserNotFoundError("User not found")
        assert get_http_status_code(error) == status.HTTP_404_NOT_FOUND

    def test_permission_error_maps_to_403(self):
        """GIVEN PermissionError WHEN getting HTTP status THEN returns 403."""
        error = ArticlePermissionError("Permission denied")
        assert get_http_status_code(error) == status.HTTP_403_FORBIDDEN

    def test_conflict_error_maps_to_409(self):
        """GIVEN ConflictError WHEN getting HTTP status THEN returns 409."""
        error = UserAlreadyExistsError("User already exists")
        assert get_http_status_code(error) == status.HTTP_409_CONFLICT

    def test_validation_error_maps_to_400(self):
        """GIVEN ValidationError WHEN getting HTTP status THEN returns 400."""
        error = CannotFollowYourselfError("Cannot follow yourself")
        assert get_http_status_code(error) == status.HTTP_400_BAD_REQUEST

    def test_authentication_error_maps_to_401(self):
        """GIVEN AuthenticationError WHEN getting HTTP status THEN returns 401."""
        error = InvalidCredentialsError("Invalid credentials")
        assert get_http_status_code(error) == status.HTTP_401_UNAUTHORIZED

    def test_unknown_domain_error_maps_to_500(self):
        """GIVEN unknown DomainError WHEN getting HTTP status THEN returns 500."""
        error = DomainError("Unknown error")
        assert get_http_status_code(error) == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestExceptionTranslation:
    """Test translation of domain exceptions to HTTPExceptions."""

    def test_translate_user_not_found_error(self):
        """GIVEN UserNotFoundError WHEN translated to HTTP THEN returns correct HTTPException."""
        error = UserNotFoundError("User with id 123 not found")
        http_exc = translate_domain_error_to_http(error)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_404_NOT_FOUND
        assert "User with id 123 not found" in http_exc.detail

    def test_translate_permission_error(self):
        """GIVEN PermissionError WHEN translated to HTTP THEN returns correct HTTPException."""
        error = CommentPermissionError("Only author can delete comment")
        http_exc = translate_domain_error_to_http(error)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_403_FORBIDDEN
        assert "Only author can delete comment" in http_exc.detail

    def test_translate_conflict_error(self):
        """GIVEN ConflictError WHEN translated to HTTP THEN returns correct HTTPException."""
        error = ArticleSlugConflictError("Article with slug 'test' already exists")
        http_exc = translate_domain_error_to_http(error)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_409_CONFLICT
        assert "Article with slug 'test' already exists" in http_exc.detail

    def test_translate_validation_error(self):
        """GIVEN ValidationError WHEN translated to HTTP THEN returns correct HTTPException."""
        error = CannotFollowYourselfError("Cannot follow yourself")
        http_exc = translate_domain_error_to_http(error)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot follow yourself" in http_exc.detail

    def test_error_code_included_in_detail(self):
        """
        GIVEN DomainError with error_code
        WHEN translated
        THEN error_code is included in detail.
        """
        error = DomainError("Something went wrong", error_code="CUSTOM_ERROR")
        http_exc = translate_domain_error_to_http(error)

        assert "CUSTOM_ERROR: Something went wrong" in http_exc.detail


class TestDomainErrorCreation:
    """Test creating domain errors with messages and error codes."""

    def test_domain_error_with_message_only(self):
        """GIVEN DomainError with message WHEN created THEN has correct properties."""
        error = DomainError("Test error")
        assert error.message == "Test error"
        assert error.error_code == "DomainError"  # Default to class name

    def test_domain_error_with_custom_error_code(self):
        """GIVEN DomainError with custom error_code WHEN created THEN has correct properties."""
        error = DomainError("Test error", error_code="CUSTOM_CODE")
        assert error.message == "Test error"
        assert error.error_code == "CUSTOM_CODE"

    def test_inherited_domain_error_default_code(self):
        """GIVEN inherited DomainError WHEN created THEN uses child class name as error_code."""
        error = UserNotFoundError("User not found")
        assert error.message == "User not found"
        assert error.error_code == "UserNotFoundError"
