from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.university import ProgramsResponse, UniversityListResponse
from app.database import get_db
from . import service

router = APIRouter()


@router.get("/universities", response_model=UniversityListResponse)
async def get_universities(limit: int = Query(default=0, ge=0), db: AsyncSession = Depends(get_db)):
    return await service.list_universities(db, limit)


@router.get("/universities/search", response_model=UniversityListResponse)
async def search_universities(q: str = Query(min_length=1), db: AsyncSession = Depends(get_db)):
    return await service.search_universities(db, q)


@router.get("/universities/{university_id}/programs", response_model=ProgramsResponse)
async def get_university_programs(university_id: str, db: AsyncSession = Depends(get_db)):
    result = await service.list_programs(db, university_id)
    if result is None:
        return JSONResponse({"error": "university not found"}, status_code=404)
    return result


@router.get("/universities/{university_name:path}")
async def get_university_detail(university_name: str, db: AsyncSession = Depends(get_db)):
    result = await service.get_university_detail(db, university_name)
    if result is None:
        return JSONResponse({"error": "university not found"}, status_code=404)
    return result
