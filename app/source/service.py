from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Source
from app.dto.source import SourceInfo, SourcesResponse

async def get_sources(db: AsyncSession) -> SourcesResponse:
    stmt = select(Source).order_by(Source.name)
    result = await db.execute(stmt)
    sources = result.scalars().all()
    
    total = sum(s.count for s in sources)
    
    return SourcesResponse(
        sources=[
            SourceInfo(name=s.name, label=s.label, count=s.count)
            for s in sources
        ],
        total=total,
    )
