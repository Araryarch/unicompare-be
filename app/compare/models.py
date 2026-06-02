from pydantic import BaseModel

from app.university.models import ProgramItem


class CompareUniversity(BaseModel):
    id: str
    name: str
    sources: list[str]
    eligible_count: int
    program_count: int
    eligible_programs: list[ProgramItem]


class CompareResponse(BaseModel):
    user_score: float
    total: int
    universities: list[CompareUniversity]
