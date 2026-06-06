import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

async def test_register():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        print("1. Testing Registration...")
        reg_payload = {"username": "user_test", "password": "password_test"}
        r = await client.post("/api/auth/register", json=reg_payload)
        print("Register Status:", r.status_code)
        print("Register Response:", r.json())
        
        print("\n2. Testing Login...")
        login_payload = {"username": "user_test", "password": "password_test"}
        r = await client.post("/api/auth/login", json=login_payload)
        print("Login Status:", r.status_code)
        print("Login Response:", r.json())

if __name__ == "__main__":
    asyncio.run(test_register())
