"""Auth business logic — user creation, verification, JWT tokens."""

import logging
from datetime import datetime, timezone, timedelta

import bcrypt
from jose import jwt, JWTError

from ..config import get_settings
from ..database import get_db

logger = logging.getLogger(__name__)


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def get_user(username: str) -> dict | None:
    """Fetch user by username."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT username, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    if not row:
        return None
    return {"username": row["username"], "password_hash": row["password_hash"]}


def create_user(username: str, password: str) -> dict:
    """Create a new user with hashed password."""
    if get_user(username):
        raise ValueError("User already exists")

    pw_hash = _hash_password(password)
    created_at = datetime.now(timezone.utc).isoformat()

    with get_db() as conn:
        conn.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username, pw_hash, created_at),
        )
        conn.commit()

    logger.info(f"User created: {username}")
    return {"username": username}


def authenticate_user(username: str, password: str) -> dict | None:
    """Verify credentials, return user dict or None."""
    user = get_user(username)
    if not user:
        return None
    if not _verify_password(password, user["password_hash"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generate a JWT access token."""
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> str | None:
    """Decode JWT token, return username or None."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        return username
    except JWTError:
        return None
