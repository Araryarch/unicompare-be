import logging

from fastapi import FastAPI

from app.compare.api import router as compare_router
from app.source.api import router as source_router
from app.university.api import router as university_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Unicompare")

app.include_router(source_router, prefix="/api")
app.include_router(university_router, prefix="/api")
app.include_router(compare_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
