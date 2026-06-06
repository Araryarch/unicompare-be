from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dto.auth import (
    AdminUserResponse,
    DeletedUserResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.dto.university import (
    CreateUniversityRequest,
    UpdateUniversityRequest,
    UniversityCreateResponse,
)
from app.university import service as university_service

from . import service

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


@router.post("/admin/universities", response_model=UniversityCreateResponse)
async def admin_create_university(
    body: CreateUniversityRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(service.require_admin),
):
    uni = await university_service.create_university(db, body)
    return UniversityCreateResponse(id=uni.id, name=uni.name, sources=uni.sources)


@router.put("/admin/universities/{university_id}", response_model=UniversityCreateResponse)
async def admin_update_university(
    university_id: str,
    body: UpdateUniversityRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(service.require_admin),
):
    uni = await university_service.update_university(db, university_id, body)
    if uni is None:
        raise HTTPException(status_code=404, detail="University not found")
    return UniversityCreateResponse(id=uni.id, name=uni.name, sources=uni.sources)


@router.delete("/admin/universities/{university_id}")
async def admin_delete_university(
    university_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(service.require_admin),
):
    ok = await university_service.delete_university(db, university_id)
    if not ok:
        raise HTTPException(status_code=404, detail="University not found")
    return {"message": f"University {university_id} deleted"}
