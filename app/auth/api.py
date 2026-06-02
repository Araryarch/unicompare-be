from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from . import service
from .models import (
    AdminUserResponse,
    FavoriteRequest,
    FavoriteResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


class DeletedUserResponse(BaseModel):
    username: str

router = APIRouter()


@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    token = await service.authenticate(body.username, body.password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=token)


@router.post("/auth/register", response_model=TokenResponse)
async def register(body: RegisterRequest):
    if len(body.username) < 3:
        raise HTTPException(status_code=422, detail="Username too short (min 3)")
    if len(body.password) < 4:
        raise HTTPException(status_code=422, detail="Password too short (min 4)")
    token = await service.register(body.username, body.password)
    if token is None:
        raise HTTPException(status_code=409, detail="Username already exists")
    return TokenResponse(access_token=token)


@router.get("/auth/me", response_model=UserResponse)
async def me(user: dict = Depends(service.get_current_user)):
    return UserResponse(username=user["username"], role=user["role"])


@router.get("/favorites", response_model=FavoriteResponse)
async def list_favorites(user: dict = Depends(service.get_current_user)):
    favs = await service.get_favorites(user["username"])
    return FavoriteResponse(favorites=favs)


@router.post("/favorites", response_model=FavoriteResponse)
async def add_favorite(
    body: FavoriteRequest,
    user: dict = Depends(service.get_current_user),
):
    await service.add_favorite(user["username"], body.university_name)
    favs = await service.get_favorites(user["username"])
    return FavoriteResponse(favorites=favs)


@router.delete("/favorites/{university_name}", response_model=FavoriteResponse)
async def remove_favorite(
    university_name: str,
    user: dict = Depends(service.get_current_user),
):
    ok = await service.remove_favorite(user["username"], university_name)
    if not ok:
        raise HTTPException(status_code=404, detail="Favorite not found")
    favs = await service.get_favorites(user["username"])
    return FavoriteResponse(favorites=favs)


@router.get("/admin/users", response_model=list[AdminUserResponse])
async def admin_list_users(user: dict = Depends(service.require_admin)):
    return await service.list_users()


@router.delete("/admin/users/{username}", response_model=DeletedUserResponse)
async def admin_delete_user(
    username: str,
    user: dict = Depends(service.require_admin),
):
    if username == user["username"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    ok = await service.delete_user(username)
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return DeletedUserResponse(username=username)
