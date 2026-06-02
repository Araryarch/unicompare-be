from enum import StrEnum

from pydantic import BaseModel


class Role(StrEnum):
    ADMIN = "admin"
    USER = "user"


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    username: str
    role: str = "user"


class AdminUserResponse(BaseModel):
    username: str
    role: str = "user"


class DeletedUserResponse(BaseModel):
    username: str


class FavoriteRequest(BaseModel):
    university_name: str


class FavoriteResponse(BaseModel):
    favorites: list[str]
