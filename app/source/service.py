import asyncio
import json
import os

from app.dto.source import SourceInfo, SourcesResponse


async def get_sources() -> SourcesResponse:
    data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sources.json")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return SourcesResponse(**data)
