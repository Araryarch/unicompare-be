from typing import Optional
from sqlalchemy import String, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Source(Base):
    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    label: Mapped[str] = mapped_column(String, nullable=False)
    count: Mapped[int] = mapped_column(Integer, default=0)

class University(Base):
    __tablename__ = "universities"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    sources: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    programs: Mapped[list["Program"]] = relationship("Program", back_populates="university", cascade="all, delete-orphan")

class Program(Base):
    __tablename__ = "programs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    university_id: Mapped[str] = mapped_column(String, ForeignKey("universities.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    score_text: Mapped[str] = mapped_column(String, nullable=False)
    degree: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True)
    source_count: Mapped[int] = mapped_column(Integer, default=1)

    university: Mapped["University"] = relationship("University", back_populates="programs")
