from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from bimba3d_backend.app.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from bimba3d_backend.app.services.db import RefreshToken, User, db_session


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(subject: str, role: str) -> str:
    expires = _now_utc() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {"sub": subject, "role": role, "type": "access", "exp": expires}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(subject: str) -> tuple[str, str, datetime]:
    expires = _now_utc() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    token = jwt.encode(
        {"sub": subject, "type": "refresh", "jti": str(uuid.uuid4()), "exp": expires},
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return token, token_hash, expires


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc


def save_refresh_token(
    user_id: str,
    token_hash: str,
    expires_at: datetime,
    session: Session | None = None,
) -> str:
    token_id = str(uuid.uuid4())
    if session is not None:
        record = RefreshToken(
            id=token_id,
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at.replace(tzinfo=None),
        )
        session.add(record)
        return token_id

    with db_session() as session:
        record = RefreshToken(
            id=token_id,
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at.replace(tzinfo=None),
        )
        session.add(record)
    return token_id


def revoke_refresh_token(token: str) -> None:
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with db_session() as session:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        record = session.execute(stmt).scalar_one_or_none()
        if record and record.revoked_at is None:
            record.revoked_at = datetime.utcnow()


def validate_refresh_token(token: str) -> User:
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with db_session() as session:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        record = session.execute(stmt).scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=401, detail="Refresh token not found")
        if record.revoked_at is not None:
            raise HTTPException(status_code=401, detail="Refresh token revoked")
        if record.expires_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Refresh token expired")

        user_stmt = select(User).where(User.id == record.user_id)
        user = session.execute(user_stmt).scalar_one_or_none()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User is not active")
        return user


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any] | None:
    if not credentials:
        return None
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    return {
        "user_id": payload.get("sub"),
        "role": payload.get("role", "user"),
    }


def get_current_user_required(
    current: dict[str, Any] | None = Depends(get_current_user_optional),
) -> dict[str, Any]:
    if not current or not current.get("user_id"):
        raise HTTPException(status_code=401, detail="Authentication required")
    return current


def require_admin(current: dict[str, Any] = Depends(get_current_user_required)) -> dict[str, Any]:
    if current.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current
