import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.auth.api import router as auth_router
from app.compare.api import router as compare_router
from app.database import init_db
from app.source.api import router as source_router
from app.university.api import router as university_router

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Creating database tables...")
    await init_db()
    log.info("Database ready")
    yield


app = FastAPI(title="Unicompare", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    log.error(f"Database error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "A database error occurred"},
    )

app.include_router(auth_router, prefix="/api")
app.include_router(source_router, prefix="/api")
app.include_router(university_router, prefix="/api")
app.include_router(compare_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "Unicompare API",
        "version": "1.0.0",
        "status": "ok",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
