"""Authentication primitives for the API."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import uuid
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings

if TYPE_CHECKING:
    from app.models.entities import User

_bearer = HTTPBearer(auto_error=False)
_SCRYPT_N, _SCRYPT_R, _SCRYPT_P = 2**14, 8, 1


def _get_db():
    from app.db.session import get_db

    yield from get_db()


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def hash_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters")
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P)
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${_encode(salt)}${_encode(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, n, r, p, salt_text, digest_text = encoded.split("$")
        if scheme != "scrypt":
            return False
        expected = _decode(digest_text)
        actual = hashlib.scrypt(password.encode(), salt=_decode(salt_text), n=int(n), r=int(r), p=int(p))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _signing_secret() -> str:
    secret = get_settings().jwt_secret
    if len(secret) < 32:
        raise RuntimeError("JWT_SECRET must be configured with at least 32 characters")
    return secret


def create_access_token(user_id: uuid.UUID) -> str:
    settings = get_settings()
    expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": str(user_id), "exp": expires}, _signing_secret(), algorithm=settings.jwt_algorithm)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(_get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    settings = get_settings()
    try:
        payload = jwt.decode(credentials.credentials, _signing_secret(), algorithms=[settings.jwt_algorithm])
        user_id = uuid.UUID(str(payload["sub"]))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Authentication is not configured") from exc
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token") from exc
    from app.models.entities import User

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive or unavailable")
    return user


def require_roles(*allowed_roles: str):
    """Create a dependency that permits only users with an allowed role."""
    allowed = {role.lower() for role in allowed_roles}

    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role.name.lower() not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role permissions")
        return user

    return dependency
