from fastapi import APIRouter, Depends, HTTPException

from . import service
from .models import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter()


@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    token = await service.authenticate(body.username, body.password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=token)


@router.post("/auth/register", response_model=TokenResponse)
async def register(body: RegisterRequest):
    ok = await service.register(body.username, body.password)
    if not ok:
        raise HTTPException(status_code=409, detail="Username already exists")
    token = await service.authenticate(body.username, body.password)
    return TokenResponse(access_token=token)


@router.get("/auth/me", response_model=UserResponse)
async def me(username: str = Depends(service.get_current_user)):
    return UserResponse(username=username)
