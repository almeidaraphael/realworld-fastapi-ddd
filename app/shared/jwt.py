# JWT utility functions

from datetime import datetime, timedelta, timezone

import jwt

from app.config.settings import get_app_settings
from app.shared import JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM


def create_access_token(data: dict[str, object], expires_delta: timedelta | None = None) -> str:
    settings = get_app_settings()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, object]:
    settings = get_app_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])
        return dict(payload)
    except jwt.PyJWTError as err:
        raise ValueError("Invalid token") from err
