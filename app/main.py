import logging

from fastapi import FastAPI

from app.auth.api import router as auth_router
from app.compare.api import router as compare_router
from app.source.api import router as source_router
from app.university.api import router as university_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Unicompare")

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
