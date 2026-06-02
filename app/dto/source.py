from pydantic import BaseModel


class SourceInfo(BaseModel):
    name: str
    label: str
    count: int


class SourcesResponse(BaseModel):
    sources: list[SourceInfo]
    total: int
