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

        import random
        import string
        rnd = ''.join(random.choices(string.ascii_lowercase, k=5))
        test_user = f"tester_{rnd}"
        test_pass = "password123"

        print(f"Testing /api/auth/register with user {test_user}...")
        r = await client.post("/api/auth/register", json={"username": test_user, "password": test_pass})
        print("/api/auth/register:", r.status_code)

        print("Testing /api/auth/login...")
        r = await client.post("/api/auth/login", json={"username": test_user, "password": test_pass})
        print("/api/auth/login:", r.status_code)
        
        token = r.json().get("access_token")
        print("Testing /api/auth/me...")
        r = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        print("/api/auth/me:", r.status_code)
        print("User Info:", r.json())

if __name__ == "__main__":
    asyncio.run(test_api())
