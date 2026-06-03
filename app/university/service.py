import logging
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import University, Program
from app.dto.university import (
    ProgramItem,
    UniversityDetail,
    UniversityListItem,
    UniversityListResponse,
)
from app.utils.normalize_name import normalize_name

log = logging.getLogger(__name__)


async def list_universities(db: AsyncSession, limit: int = 0) -> UniversityListResponse:
    stmt = select(University).options(selectinload(University.programs)).order_by(University.name)
    if limit > 0:
        stmt = stmt.limit(limit)
    
    result = await db.execute(stmt)
    universities = result.scalars().all()
    
    # Need total count
    count_stmt = select(func.count(University.id))
    total = await db.scalar(count_stmt)

    return UniversityListResponse(
        total=total or 0,
        universities=[
            UniversityListItem(
                id=u.id,
                name=u.name,
                sources=u.sources,
                program_count=len(u.programs),
            )
            for u in universities
        ],
    )


async def search_universities(db: AsyncSession, q: str) -> UniversityListResponse:
    ql = q.lower()
    stmt = select(University).options(selectinload(University.programs)).where(
        or_(
            func.lower(University.name).contains(ql),
            func.lower(University.id).contains(ql)
        )
    ).order_by(University.name)
    
    result = await db.execute(stmt)
    universities = result.scalars().all()
    
    return UniversityListResponse(
        total=len(universities),
        universities=[
            UniversityListItem(
                id=u.id,
                name=u.name,
                sources=u.sources,
                program_count=len(u.programs),
            )
            for u in universities
        ],
    )


async def get_university_detail(db: AsyncSession, university_name: str) -> UniversityDetail | None:
    ql = university_name.lower().strip()
    qn = normalize_name(university_name)
    
    stmt = select(University).options(selectinload(University.programs)).where(
        or_(
            func.lower(University.name).contains(ql),
            func.lower(University.id).contains(ql),
            func.lower(University.name).contains(qn),
            func.lower(University.id).contains(qn)
        )
    ).limit(1)
    
    result = await db.execute(stmt)
    uni = result.scalars().first()
    
    if not uni:
        return None
        
    programs = sorted(uni.programs, key=lambda x: x.score or 0, reverse=True)
    
    return UniversityDetail(
        id=uni.id,
        name=uni.name,
        sources=uni.sources,
        program_count=len(programs),
        programs=[
            ProgramItem(
                name=p.name,
                score_text=p.score_text,
                degree=p.degree or "",
                score=p.score,
                source_count=p.source_count
            ) for p in programs
        ],
    )
