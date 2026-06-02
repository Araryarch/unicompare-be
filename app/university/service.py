import asyncio
import logging

from app.config import ALL_SOURCES
from app.utils.merger import merge_universities
from app.utils.normalize_name import normalize_name

from app.dto.university import (
    ProgramItem,
    UniversityDetail,
    UniversityListItem,
    UniversityListResponse,
)

log = logging.getLogger(__name__)

_merged_cache: list[dict] | None = None


async def get_merged() -> list[dict]:
    global _merged_cache
    if _merged_cache is not None:
        return _merged_cache
    results = await asyncio.gather(*[fn() for _, _, fn in ALL_SOURCES])
    _merged_cache = merge_universities(*results)
    return _merged_cache


async def list_universities(limit: int = 0) -> UniversityListResponse:
    data = await get_merged()
    if limit > 0:
        data = data[:limit]
    return UniversityListResponse(
        total=len(data),
        universities=[
            UniversityListItem(
                id=u["id"],
                name=u["name"],
                sources=u["sources"],
                program_count=len(u["programs"]),
            )
            for u in data
        ],
    )


async def search_universities(q: str) -> UniversityListResponse:
    data = await get_merged()
    ql = q.lower()
    results = [u for u in data if ql in u["name"].lower() or ql in u["id"]]
    return UniversityListResponse(
        total=len(results),
        universities=[
            UniversityListItem(
                id=u["id"],
                name=u["name"],
                sources=u["sources"],
                program_count=len(u["programs"]),
            )
            for u in results
        ],
    )


async def get_university_detail(university_name: str) -> UniversityDetail | None:
    data = await get_merged()
    ql = university_name.lower().strip()
    qn = normalize_name(university_name)
    matches = [
        u
        for u in data
        if ql in u["id"]
        or ql in u["name"].lower()
        or qn in u["id"]
        or qn in u["name"].lower()
    ]
    if not matches:
        return None
    uni = matches[0]
    programs = sorted(uni["programs"], key=lambda x: x["score"] or 0, reverse=True)
    return UniversityDetail(
        id=uni["id"],
        name=uni["name"],
        sources=uni["sources"],
        program_count=len(programs),
        programs=[ProgramItem(**p) for p in programs],
    )
