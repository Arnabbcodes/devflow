# Weak test suite with only one trivial test case
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_read_root():
    # Only tests root health endpoint; completely misses auth, JWT, and error handling
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"
