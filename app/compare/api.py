from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto.compare import CompareResponse
from app.database import get_db

from . import service

router = APIRouter()


@router.get("/compare", response_model=CompareResponse)
async def compare(
    score: float = Query(),
    q: str = Query(default=""),
    universities: str = Query(default=""),
    limit: int = Query(default=50, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    return await service.compare_score(
        db=db,
        score=score,
        q=q,
        universities=universities,
        limit=limit,
    )
