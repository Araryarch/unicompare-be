from fastapi import APIRouter, Query

from . import service
from .models import CompareResponse

router = APIRouter()


@router.get("/compare", response_model=CompareResponse)
async def compare(
    score: float = Query(),
    q: str = Query(default=""),
    universities: str = Query(default=""),
    limit: int = Query(default=50, ge=1, le=500),
):
    return await service.compare_score(
        score=score,
        q=q,
        universities=universities,
        limit=limit,
    )
