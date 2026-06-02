import os
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .models import Role

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

_SECRET_KEY: str | None = None
_users: dict[str, dict] = {}
_favorites: dict[str, set[str]] = {}

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


def _seed_admin() -> None:
    user = os.getenv("UNICOMPARE_USERNAME", "admin")
    passwd = os.getenv("UNICOMPARE_PASSWORD", "admin")
    if user not in _users:
        _users[user] = {
            "password": _hash_password(passwd),
            "role": Role.ADMIN,
        }


def _build_token(username: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, _get_secret(), algorithm=ALGORITHM)


async def register(username: str, password: str) -> str | None:
    _seed_admin()
    if username in _users:
        return None
    _users[username] = {
        "password": _hash_password(password),
        "role": Role.USER,
    }
    return _build_token(username, Role.USER)


async def authenticate(username: str, password: str) -> str | None:
    _seed_admin()
    record = _users.get(username)
    if record is None or not _verify_password(password, record["password"]):
        return None
    return _build_token(username, record["role"])


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    try:
        payload = jwt.decode(
            creds.credentials, _get_secret(), algorithms=[ALGORITHM]
        )
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


async def get_favorites(username: str) -> list[str]:
    return sorted(_favorites.get(username, set()))


async def add_favorite(username: str, university_name: str) -> None:
    _favorites.setdefault(username, set()).add(university_name)


async def remove_favorite(username: str, university_name: str) -> bool:
    favs = _favorites.get(username)
    if favs is None or university_name not in favs:
        return False
    favs.discard(university_name)
    return True


async def list_users() -> list[dict]:
    return [
        {"username": u, "role": r["role"]}
        for u, r in _users.items()
    ]


async def delete_user(username: str) -> bool:
    if username not in _users:
        return False
    del _users[username]
    _favorites.pop(username, None)
    return True
