from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.source import SourcesResponse
from app.database import get_db

from . import service

router = APIRouter()


@router.get("/sources", response_model=SourcesResponse)
async def get_sources(db: AsyncSession = Depends(get_db)):
    return await service.get_sources(db)
