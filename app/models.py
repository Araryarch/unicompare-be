from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base

class Source(Base):
    __tablename__ = "sources"

    name = Column(String, primary_key=True, index=True)
    label = Column(String, nullable=False)
    count = Column(Integer, default=0)

class University(Base):
    __tablename__ = "universities"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    sources = Column(JSON, nullable=False, default=list)

    programs = relationship("Program", back_populates="university", cascade="all, delete-orphan")

class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    university_id = Column(String, ForeignKey("universities.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    score_text = Column(String, nullable=False)
    degree = Column(String, nullable=True)
    score = Column(Float, nullable=True, index=True)
    source_count = Column(Integer, default=1)

    university = relationship("University", back_populates="programs")
