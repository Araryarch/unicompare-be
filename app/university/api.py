from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from . import service
from .models import UniversityListResponse

router = APIRouter()


@router.get("/universities", response_model=UniversityListResponse)
async def get_universities(limit: int = Query(default=0, ge=0)):
    return await service.list_universities(limit)


@router.get("/universities/search", response_model=UniversityListResponse)
async def search_universities(q: str = Query(min_length=1)):
    return await service.search_universities(q)


@router.get("/universities/{university_name:path}")
async def get_university_detail(university_name: str):
    result = await service.get_university_detail(university_name)
    if result is None:
        return JSONResponse({"error": "university not found"}, status_code=404)
    return result
