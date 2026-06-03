import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

load_dotenv()

_engine = None
_AsyncSessionLocal = None
Base = declarative_base()


def _get_sessionmaker():
    global _engine, _AsyncSessionLocal
    if _AsyncSessionLocal is not None:
        return _AsyncSessionLocal

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. "
            "Set it in .env or environment variables to use database features."
        )

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    _engine = create_async_engine(database_url, echo=False)
    _AsyncSessionLocal = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    return _AsyncSessionLocal


async def get_db():
    sessionmaker = _get_sessionmaker()
    async with sessionmaker() as session:
        yield session
