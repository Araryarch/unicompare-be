from fastapi import APIRouter

from app.dto.source import SourcesResponse

from . import service

router = APIRouter()


@router.get("/sources", response_model=SourcesResponse)
async def get_sources():
    return await service.get_sources()
