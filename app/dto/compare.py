from pydantic import BaseModel

from app.dto.university import ProgramItem


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


class CompareChoice(BaseModel):
    universitas: str
    program: str


class CompareChoicesRequest(BaseModel):
    pilihan: list[CompareChoice]


class UniRef(BaseModel):
    id: str
    name: str


class ProgramResult(BaseModel):
    name: str
    score: float | None = None
    score_text: str = ""
    degree: str | None = None


class CompareChoiceResult(BaseModel):
    universitas: UniRef
    program: ProgramResult


class CompareRank(BaseModel):
    universitas: str
    program: str
    score: float | None = None


class Perbandingan(BaseModel):
    tertinggi: CompareRank
    terendah: CompareRank
    selisih: float | None = None
    urutan: list[CompareRank]


class CompareChoicesResponse(BaseModel):
    pilihan: list[CompareChoiceResult]
    perbandingan: Perbandingan
