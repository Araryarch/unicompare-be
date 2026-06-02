from pydantic import BaseModel


class ProgramItem(BaseModel):
    name: str
    score_text: str
    score: float | None = None
    source_count: int = 1
    sources: list[str] = []
    degree: str | None = None


class UniversityListItem(BaseModel):
    id: str
    name: str
    sources: list[str]
    program_count: int


class UniversityListResponse(BaseModel):
    total: int
    universities: list[UniversityListItem]


class UniversityDetail(BaseModel):
    id: str
    name: str
    sources: list[str]
    program_count: int
    programs: list[ProgramItem]
