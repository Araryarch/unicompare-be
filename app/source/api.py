from fastapi import APIRouter

from . import service
from .models import SourcesResponse

router = APIRouter()


@router.get("/sources", response_model=SourcesResponse)
async def get_sources():
    return await service.get_sources()
