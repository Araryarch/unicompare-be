import logging

from app.dto.compare import CompareResponse, CompareUniversity
from app.dto.university import ProgramItem
from app.university.service import get_merged
from app.utils.normalize_name import normalize_name

log = logging.getLogger(__name__)


async def compare_score(
    score: float,
    q: str = "",
    universities: str = "",
    limit: int = 50,
) -> CompareResponse:
    data = await get_merged()

    if universities:
        uni_ids = [normalize_name(n) for n in universities.split(",")]
        filtered = [u for u in data if any(n in u["id"] for n in uni_ids)]
    else:
        filtered = data

    if q:
        ql = q.lower()
        filtered = [
            u
            for u in filtered
            if ql in u["name"].lower()
            or any(ql in p["name"].lower() for p in u["programs"])
        ]

    results = []
    for u in filtered:
        eligible = [
            p for p in u["programs"] if p["score"] is not None and score >= p["score"]
        ]
        if q:
            ql = q.lower()
            eligible = [p for p in eligible if ql in p["name"].lower()]
        if eligible:
            eligible.sort(key=lambda x: x["score"], reverse=True)
            results.append(
                CompareUniversity(
                    id=u["id"],
                    name=u["name"],
                    sources=u["sources"],
                    eligible_count=len(eligible),
                    program_count=len(u["programs"]),
                    eligible_programs=[ProgramItem(**p) for p in eligible],
                )
            )

    results.sort(key=lambda x: x.eligible_count, reverse=True)
    return CompareResponse(
        user_score=score,
        total=len(results),
        universities=results[:limit],
    )
