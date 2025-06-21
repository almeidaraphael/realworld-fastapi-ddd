from datetime import timedelta

import pytest

from app.shared.jwt import create_access_token, decode_access_token


def test_create_access_token() -> None:
    """
    GIVEN a payload for a JWT
    WHEN create_access_token is called with the payload and expiry
    THEN it should return a valid JWT string with three parts
    """
    data: dict[str, object] = {"sub": "test@example.com"}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))
    assert isinstance(token, str)
    assert token.count(".") == 2  # JWT has 3 parts


def test_decode_access_token_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    GIVEN a valid JWT token
    WHEN decode_access_token is called
    THEN it should return the original payload data
    """
    data: dict[str, object] = {"sub": "test@example.com"}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))
    decoded = decode_access_token(token)
    assert decoded["sub"] == "test@example.com"


def test_decode_access_token_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    GIVEN an invalid JWT token
    WHEN decode_access_token is called
    THEN it should raise a ValueError indicating the token is invalid
    """
    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token("not.a.valid.token")
