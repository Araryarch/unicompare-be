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
    CreateProgramRequest,
    CreateUniversityRequest,
    ProgramDeleteResponse,
    ProgramUpdateResponse,
    UniversityCreateResponse,
    UpdateProgramScoresRequest,
    UpdateUniversityRequest,
)
from app.university import service as university_service

from . import service

router = APIRouter()


@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    token = await service.authenticate(db, body.username, body.password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=token)


@router.post("/auth/register", response_model=TokenResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    token = await service.register(db, body.username, body.password)
    if token is None:
        raise HTTPException(status_code=409, detail="Username already exists")
    return TokenResponse(access_token=token)


@router.get("/auth/me", response_model=UserResponse)
async def me(user: dict = Depends(service.get_current_user)):
    return UserResponse(username=user["username"], role=user["role"])


@router.get("/admin/users", response_model=list[AdminUserResponse])
async def admin_list_users(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(service.require_admin),
):
    return await service.list_users(db)


@router.delete("/admin/users/{username}", response_model=DeletedUserResponse)
async def admin_delete_user(
    username: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(service.require_admin),
):
    if username == user["username"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    ok = await service.delete_user(db, username)
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


@router.put(
    "/admin/universities/{university_id}", response_model=UniversityCreateResponse
)
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


@router.put(
    "/admin/universities/{university_id}/programs",
    response_model=list[ProgramUpdateResponse],
)
async def admin_update_program_scores(
    university_id: str,
    body: UpdateProgramScoresRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(service.require_admin),
):
    result = await university_service.update_program_scores(db, university_id, body)
    if result is None:
        raise HTTPException(status_code=404, detail="University not found")
    return result


@router.post(
    "/admin/universities/{university_id}/programs",
    response_model=ProgramUpdateResponse,
)
async def admin_create_program(
    university_id: str,
    body: CreateProgramRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(service.require_admin),
):
    result = await university_service.create_program(db, university_id, body)
    if result is None:
        raise HTTPException(status_code=404, detail="University not found")
    return result


@router.delete("/admin/universities/{university_id}/programs/{program_id}")
async def admin_delete_program(
    university_id: str,
    program_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(service.require_admin),
):
    ok = await university_service.delete_program(db, program_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Program not found")
    return ProgramDeleteResponse(id=program_id, message=f"Program {program_id} deleted")
