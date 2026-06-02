import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

_SECRET_KEY: str | None = None


def _get_secret() -> str:
    global _SECRET_KEY
    if _SECRET_KEY is None:
        _SECRET_KEY = os.getenv("UNICOMPARE_SECRET", secrets.token_hex(32))
    return _SECRET_KEY


async def authenticate(username: str, password: str) -> str | None:
    expected_user = os.getenv("UNICOMPARE_USERNAME", "admin")
    expected_pass = os.getenv("UNICOMPARE_PASSWORD", "admin")
    if username != expected_user or password != expected_pass:
        return None
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, _get_secret(), algorithm=ALGORITHM)
