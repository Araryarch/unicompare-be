import os
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

_SECRET_KEY: str | None = None
_users: dict[str, str] = {}

security = HTTPBearer()


def _get_secret() -> str:
    global _SECRET_KEY
    if _SECRET_KEY is None:
        _SECRET_KEY = os.getenv("UNICOMPARE_SECRET", secrets.token_hex(32))
    return _SECRET_KEY


def _seed_admin() -> None:
    user = os.getenv("UNICOMPARE_USERNAME", "admin")
    passwd = os.getenv("UNICOMPARE_PASSWORD", "admin")
    if user not in _users:
        _users[user] = passwd


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 600000)
    return f"{salt}:{dk.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    if ":" not in stored:
        return secrets.compare_digest(password, stored)
    salt, _ = stored.split(":", 1)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 600000)
    return secrets.compare_digest(f"{salt}:{dk.hex()}", stored)


async def register(username: str, password: str) -> bool:
    _seed_admin()
    if username in _users:
        return False
    _users[username] = _hash_password(password)
    return True


async def authenticate(username: str, password: str) -> str | None:
    _seed_admin()
    stored = _users.get(username)
    if stored is None or not _verify_password(password, stored):
        return None
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, _get_secret(), algorithm=ALGORITHM)


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    try:
        payload = jwt.decode(
            creds.credentials, _get_secret(), algorithms=[ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
