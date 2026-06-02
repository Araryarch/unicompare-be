import asyncio

from app.config import ALL_SOURCES

from .models import SourceInfo, SourcesResponse


async def get_sources() -> SourcesResponse:
    results = await asyncio.gather(*[fn() for _, _, fn in ALL_SOURCES])
    return SourcesResponse(
        sources=[
            SourceInfo(name=name, label=label, count=len(r))
            for (name, label, _), r in zip(ALL_SOURCES, results)
        ],
        total=sum(len(r) for r in results),
    )
