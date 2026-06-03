import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

async def test_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        print("Testing Root...")
        r = await client.get("/")
        print("Root:", r.status_code)
        
        print("Testing /api/sources...")
        r = await client.get("/api/sources")
        print("/api/sources:", r.status_code)
        
        print("Testing /api/universities?limit=1...")
        r = await client.get("/api/universities?limit=1")
        print("/api/universities:", r.status_code)
        
        print("Testing /api/compare?score=500...")
        r = await client.get("/api/compare?score=500")
        print("/api/compare:", r.status_code)

if __name__ == "__main__":
    asyncio.run(test_api())
