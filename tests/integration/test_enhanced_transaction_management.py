"""
Integration tests for the enhanced transaction management system.

These tests demonstrate that the new transaction management works correctly
with the existing service layer and API endpoints.
"""

import asyncio

import pytest
from httpx import AsyncClient

from app.domain.users.exceptions import UserAlreadyExistsError
from app.domain.users.schemas import NewUserRequest, UserCreate, UserLogin, UserLoginRequest
from app.service_layer.users.services import authenticate_user, create_user, get_user_by_email


def create_test_user_data(suffix: str = "") -> UserCreate:
    """Create test user data."""
    return UserCreate(
        username=f"testuser{suffix}", email=f"test{suffix}@example.com", password="testpassword123"
    )


class TestEnhancedTransactionManagement:
    """Test the enhanced transaction management in the service layer."""

    async def test_create_user_with_enhanced_transaction_management(self) -> None:
        """
        GIVEN the enhanced user service with @transactional decorator
        WHEN creating a new user
        THEN it should successfully create the user with automatic transaction management
        """
        # Create test data
        user_data = create_test_user_data("1")
        user_request = NewUserRequest(user=user_data)

        # Call the enhanced service function
        # The UoW is automatically injected by the @transactional decorator
        result = await create_user(user_request)

        # Verify the result
        assert result.username == user_data.username
        assert result.email == user_data.email
        assert result.id is not None

    async def test_authenticate_user_with_enhanced_transaction_management(self) -> None:
        """
        GIVEN the enhanced user service with @transactional decorator
        WHEN authenticating an existing user
        THEN it should successfully authenticate with automatic transaction management
        """
        # Create a user first
        user_data = create_test_user_data("2")
        user_request = NewUserRequest(user=user_data)
        created_user = await create_user(user_request)

        # Now authenticate the user
        login_data = UserLogin(email=user_data.email, password=user_data.password)
        login_request = UserLoginRequest(user=login_data)

        # Call the enhanced service function
        result = await authenticate_user(login_request)

        # Verify the result
        assert result is not None
        assert result.username == created_user.username
        assert result.email == created_user.email

    async def test_safe_get_user_by_email_with_nonexistent_user(self) -> None:
        """
        GIVEN the enhanced get_user_by_email service with reraise=False
        WHEN attempting to get a non-existent user
        THEN it should return None instead of raising an exception
        """
        # Call the enhanced service function with a non-existent email
        result = await get_user_by_email("nonexistent@example.com")

        # Verify that it returns None instead of raising an exception
        assert result is None

    async def test_transaction_rollback_on_exception(self) -> None:
        """
        GIVEN the enhanced user service with @transactional decorator
        WHEN an exception occurs during user creation
        THEN the transaction should be automatically rolled back
        """
        # Create a user first
        user_data = create_test_user_data("3")
        user_request = NewUserRequest(user=user_data)
        await create_user(user_request)

        # Try to create the same user again (should fail due to unique constraints)
        with pytest.raises(UserAlreadyExistsError):
            await create_user(user_request)

        # Verify that the database state is consistent (user exists only once)
        result = await get_user_by_email(user_data.email)
        assert result is not None
        assert result.email == user_data.email

    async def test_api_endpoint_with_enhanced_services(self, async_client: AsyncClient) -> None:
        """
        GIVEN the API endpoints using the enhanced services
        WHEN making API calls
        THEN they should work correctly with the enhanced transaction management
        """
        # Test user registration endpoint
        user_data = {
            "user": {
                "username": "testuser4",
                "email": "test4@example.com",
                "password": "testpassword123",
            }
        }

        response = await async_client.post("/api/users", json=user_data)

        # Verify successful registration
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["user"]["username"] == "testuser4"
        assert response_data["user"]["email"] == "test4@example.com"
        assert "token" in response_data["user"]

        # Test login endpoint
        login_data = {"user": {"email": "test4@example.com", "password": "testpassword123"}}

        response = await async_client.post("/api/users/login", json=login_data)

        # Verify successful login
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["user"]["username"] == "testuser4"
        assert response_data["user"]["email"] == "test4@example.com"
        assert "token" in response_data["user"]

    async def test_concurrent_user_creation_with_transaction_management(self) -> None:
        """
        GIVEN the enhanced user service with @transactional decorator
        WHEN creating multiple users concurrently
        THEN each transaction should be handled independently and correctly
        """
        # Create multiple user data sets
        user_data_list = [create_test_user_data(str(i + 5)) for i in range(3)]
        user_requests = [NewUserRequest(user=data) for data in user_data_list]

        # Create users concurrently
        results = await asyncio.gather(*[create_user(request) for request in user_requests])

        # Verify all users were created successfully
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.username == user_data_list[i].username
            assert result.email == user_data_list[i].email
            assert result.id is not None

        # Verify all users exist in the database
        for user_data in user_data_list:
            user = await get_user_by_email(user_data.email)
            assert user is not None
            assert user.email == user_data.email

    async def test_service_backward_compatibility(self) -> None:
        """
        GIVEN both original and enhanced service functions
        WHEN calling the original functions
        THEN they should still work for backward compatibility
        """
        # Import the original functions for testing
        from app.service_layer.users.services import (
            authenticate_user_original,
            create_user_original,
            get_user_by_email_original,
        )

        # Test original create_user function
        user_data = create_test_user_data("8")
        user_request = NewUserRequest(user=user_data)

        # Call the original function
        result_original = await create_user_original(user_request)

        # Verify it works the same as the enhanced version
        assert result_original.username == user_data.username
        assert result_original.email == user_data.email
        assert result_original.id is not None

        # Test original authenticate_user function
        login_data = UserLogin(email=user_data.email, password=user_data.password)
        login_request = UserLoginRequest(user=login_data)

        result_auth_original = await authenticate_user_original(login_request)

        assert result_auth_original is not None
        assert result_auth_original.username == user_data.username
        assert result_auth_original.email == user_data.email

        # Test original get_user_by_email function
        result_get_original = await get_user_by_email_original(user_data.email)

        assert result_get_original is not None
        assert result_get_original.email == user_data.email

    async def test_enhanced_vs_original_consistency(self) -> None:
        """
        GIVEN both enhanced and original service functions
        WHEN performing the same operations with both
        THEN they should produce consistent results
        """
        from app.service_layer.users.services import create_user_original

        # Create user with enhanced service
        user_data_enhanced = create_test_user_data("9")
        user_request_enhanced = NewUserRequest(user=user_data_enhanced)
        result_enhanced = await create_user(user_request_enhanced)

        # Create user with original service
        user_data_original = create_test_user_data("10")
        user_request_original = NewUserRequest(user=user_data_original)
        result_original = await create_user_original(user_request_original)

        # Both should have the same structure and behavior
        assert isinstance(result_enhanced, type(result_original))
        assert result_enhanced.id is not None
        assert result_original.id is not None

        # Both users should be retrievable
        retrieved_enhanced = await get_user_by_email(user_data_enhanced.email)
        retrieved_original = await get_user_by_email(user_data_original.email)

        assert retrieved_enhanced is not None
        assert retrieved_original is not None
        assert retrieved_enhanced.email == user_data_enhanced.email
        assert retrieved_original.email == user_data_original.email
