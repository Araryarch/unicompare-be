from fastapi.testclient import TestClient
from app.main import app
import sys

client = TestClient(app)

print("Testing Root...")
r = client.get("/")
print("Root:", r.status_code)

print("Testing /api/sources...")
r = client.get("/api/sources")
print("/api/sources:", r.status_code)

print("Testing /api/universities?limit=1...")
r = client.get("/api/universities?limit=1")
print("/api/universities:", r.status_code)

print("Testing /api/compare?score=500...")
r = client.get("/api/compare?score=500")
print("/api/compare:", r.status_code)
