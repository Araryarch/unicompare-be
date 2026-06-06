import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.orm import declarative_base

load_dotenv()

_engine: AsyncEngine | None = None
_AsyncSessionLocal = None
Base = declarative_base()


def _init_engine():
    global _engine
    if _engine is not None:
        return

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. "
            "Set it in .env or environment variables to use database features."
        )

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    database_url = database_url.replace("sslmode=require", "ssl=require")
    database_url = database_url.replace("&channel_binding=require", "")

    _engine = create_async_engine(database_url, echo=False)


def _get_engine() -> AsyncEngine:
    _init_engine()
    assert _engine is not None
    return _engine


def _get_sessionmaker():
    global _AsyncSessionLocal
    if _AsyncSessionLocal is not None:
        return _AsyncSessionLocal

    engine = _get_engine()

    _AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    return _AsyncSessionLocal


async def init_db():
    engine = _get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    sessionmaker = _get_sessionmaker()
    async with sessionmaker() as session:
        yield session
