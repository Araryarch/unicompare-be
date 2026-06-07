from pydantic import BaseModel, Field


class ProgramItem(BaseModel):
    id: int | None = None
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


class ProgramsResponse(BaseModel):
    university_id: str
    university_name: str
    programs: list[ProgramItem]


class CreateUniversityRequest(BaseModel):
    id: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=3, max_length=255)
    sources: list[str] = []


class UpdateUniversityRequest(BaseModel):
    name: str | None = None
    sources: list[str] | None = None


class UpdateProgramScoreItem(BaseModel):
    id: int
    score: float | None = None
    score_text: str | None = None


class UpdateProgramScoresRequest(BaseModel):
    programs: list[UpdateProgramScoreItem]


class UniversityCreateResponse(BaseModel):
    id: str
    name: str
    sources: list[str]
    program_count: int = 0


class ProgramUpdateResponse(BaseModel):
    id: int
    name: str
    score: float | None
    score_text: str
    degree: str | None
