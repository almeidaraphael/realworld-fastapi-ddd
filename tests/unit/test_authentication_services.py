"""Tests for enhanced authentication service layer functions."""

from unittest.mock import patch

import pytest

from app.domain.users.schemas import UserRead, UserWithToken
from app.service_layer.users.services import (
    get_current_user_with_token,
    get_current_user_with_token_from_request,
    get_current_user_with_token_optional,
)
from app.shared.exceptions import AuthenticationError


@pytest.mark.asyncio
async def test_get_current_user_with_token_from_request_missing_token():
    """
    GIVEN missing token (None)
    WHEN calling get_current_user_with_token_from_request
    THEN should raise AuthenticationError with MISSING_TOKEN error code
    """
    with pytest.raises(AuthenticationError) as exc_info:
        await get_current_user_with_token_from_request(None)

    assert exc_info.value.error_code == "MISSING_TOKEN"
    assert "Missing or invalid Authorization header" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_current_user_with_token_from_request_empty_token():
    """
    GIVEN empty token string
    WHEN calling get_current_user_with_token_from_request
    THEN should raise AuthenticationError with MISSING_TOKEN error code
    """
    with pytest.raises(AuthenticationError) as exc_info:
        await get_current_user_with_token_from_request("")
    
    assert exc_info.value.error_code == "MISSING_TOKEN"
    assert "Missing or invalid Authorization header" in exc_info.value.message


@pytest.mark.asyncio
async def test_get_current_user_with_token_from_request_valid_token(user_factory):
    """
    GIVEN valid token
    WHEN calling get_current_user_with_token_from_request
    THEN should return UserWithToken object
    """
    user = user_factory.build()
    token = "valid_token"
    
    with patch('app.service_layer.users.services._authenticate_user_from_token_impl') as mock_auth:
        mock_auth.return_value = UserRead.model_validate(user.__dict__)
        
        result = await get_current_user_with_token_from_request(token)
        
        assert isinstance(result, UserWithToken)
        assert result.email == user.email
        assert result.username == user.username
        assert result.token == token
        mock_auth.assert_called_once()


@pytest.mark.asyncio
async def test_get_current_user_with_token_valid_token(user_factory):
    """
    GIVEN valid token
    WHEN calling get_current_user_with_token
    THEN should return UserWithToken object
    """
    user = user_factory.build()
    token = "valid_token"
    
    with patch('app.service_layer.users.services._authenticate_user_from_token_impl') as mock_auth:
        mock_auth.return_value = UserRead.model_validate(user.__dict__)
        
        result = await get_current_user_with_token(token)
        
        assert isinstance(result, UserWithToken)
        assert result.email == user.email
        assert result.username == user.username
        assert result.token == token


@pytest.mark.asyncio
async def test_get_current_user_with_token_optional_valid_token(user_factory):
    """
    GIVEN valid token
    WHEN calling get_current_user_with_token_optional
    THEN should return UserWithToken object
    """
    user = user_factory.build()
    token = "valid_token"
    
    with patch('app.service_layer.users.services._authenticate_user_from_token_impl') as mock_auth:
        mock_auth.return_value = UserRead.model_validate(user.__dict__)
        
        result = await get_current_user_with_token_optional(token)
        
        assert isinstance(result, UserWithToken)
        assert result.email == user.email
        assert result.username == user.username
        assert result.token == token


@pytest.mark.asyncio
async def test_get_current_user_with_token_optional_invalid_token():
    """
    GIVEN invalid token that raises AuthenticationError
    WHEN calling get_current_user_with_token_optional
    THEN should return None instead of raising exception
    """
    token = "invalid_token"
    
    with patch('app.service_layer.users.services._authenticate_user_from_token_impl') as mock_auth:
        mock_auth.side_effect = AuthenticationError("Invalid token")
        
        result = await get_current_user_with_token_optional(token)
        
        assert result is None


@pytest.mark.asyncio
async def test_get_current_user_with_token_optional_value_error():
    """
    GIVEN token that causes ValueError during processing
    WHEN calling get_current_user_with_token_optional
    THEN should return None instead of raising exception
    """
    token = "malformed_token"
    
    with patch('app.service_layer.users.services._authenticate_user_from_token_impl') as mock_auth:
        mock_auth.side_effect = ValueError("Malformed token")
        
        result = await get_current_user_with_token_optional(token)
        
        assert result is None
