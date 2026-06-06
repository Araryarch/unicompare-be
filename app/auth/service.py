import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dto.auth import Role
from app.models import User

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

_SECRET_KEY: str | None = None

security = HTTPBearer()


def _get_secret() -> str:
    global _SECRET_KEY
    if _SECRET_KEY is None:
        _SECRET_KEY = os.getenv("UNICOMPARE_SECRET", secrets.token_hex(32))
    return _SECRET_KEY


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 600000)
    return f"{salt}:{dk.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    salt, _ = stored.split(":", 1)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 600000)
    return secrets.compare_digest(f"{salt}:{dk.hex()}", stored)


async def _seed_admin(db: AsyncSession) -> None:
    result = await db.execute(select(User).where(User.username == os.getenv("UNICOMPARE_USERNAME", "admin")))
    if result.scalar_one_or_none() is not None:
        return
    user = os.getenv("UNICOMPARE_USERNAME", "admin")
    passwd = os.getenv("UNICOMPARE_PASSWORD", "admin")
    db.add(User(username=user, password=_hash_password(passwd), role=Role.ADMIN.value))
    await db.commit()


def _build_token(username: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, _get_secret(), algorithm=ALGORITHM)


async def register(db: AsyncSession, username: str, password: str) -> str | None:
    await _seed_admin(db)
    result = await db.execute(select(User).where(User.username == username))
    if result.scalar_one_or_none() is not None:
        return None
    db.add(User(username=username, password=_hash_password(password), role=Role.USER.value))
    await db.commit()
    return _build_token(username, Role.USER.value)


async def authenticate(db: AsyncSession, username: str, password: str) -> str | None:
    await _seed_admin(db)
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None or not _verify_password(password, user.password):
        return None
    return _build_token(username, user.role)


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    try:
        payload = jwt.decode(creds.credentials, _get_secret(), algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username, "role": role}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def require_admin(
    user: dict = Depends(get_current_user),
) -> dict:
    if user["role"] != Role.ADMIN.value:
        raise HTTPException(status_code=403, detail="Admin only")
    return user


async def list_users(db: AsyncSession) -> list[dict]:
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [{"username": u.username, "role": u.role} for u in users]


async def delete_user(db: AsyncSession, username: str) -> bool:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        return False
    await db.delete(user)
    await db.commit()
    return True
