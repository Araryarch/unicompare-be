import logging
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import University, Program
from app.dto.compare import CompareResponse, CompareUniversity
from app.dto.university import ProgramItem
from app.utils.normalize_name import normalize_name

log = logging.getLogger(__name__)


async def compare_score(
    db: AsyncSession,
    score: float,
    q: str = "",
    universities: str = "",
    limit: int = 50,
) -> CompareResponse:
    
    stmt = select(University).options(selectinload(University.programs))
    
    if universities:
        uni_ids = [normalize_name(n) for n in universities.split(",")]
        # Match if any uni_id is in university id
        conditions = [University.id.contains(n) for n in uni_ids]
        stmt = stmt.where(or_(*conditions))

    result = await db.execute(stmt)
    data = result.scalars().all()
    
    # In-memory filter for programs, similar to original logic, 
    # as querying exact relational logic with search 'q' across both uni name and prog name is complex in one query,
    # but we can do it efficiently since the dataset is small.
    # We could do a join, but let's stick to the fast approach.
    
    if q:
        ql = q.lower()
        filtered = []
        for u in data:
            if ql in u.name.lower() or any(ql in p.name.lower() for p in u.programs):
                filtered.append(u)
    else:
        filtered = data

    results = []
    for u in filtered:
        eligible = [
            p for p in u.programs if p.score is not None and score >= p.score
        ]
        if q:
            ql = q.lower()
            eligible = [p for p in eligible if ql in p.name.lower()]
        if eligible:
            eligible.sort(key=lambda x: x.score, reverse=True)
            results.append(
                CompareUniversity(
                    id=u.id,
                    name=u.name,
                    sources=u.sources,
                    eligible_count=len(eligible),
                    program_count=len(u.programs),
                    eligible_programs=[
                        ProgramItem(
                            name=p.name,
                            score_text=p.score_text,
                            degree=p.degree or "",
                            score=p.score,
                            source_count=p.source_count
                        ) for p in eligible
                    ],
                )
            )

    results.sort(key=lambda x: x.eligible_count, reverse=True)
    return CompareResponse(
        user_score=score,
        total=len(results),
        universities=results[:limit],
    )
