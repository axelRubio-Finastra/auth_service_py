## test_main.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_signup_validation():
    response = client.post("/signup", json={
        "email": "invalid",
        "password": "123",
    })
    assert response.status_code == 422

def test_login_without_validation():
    response = client.post("/login", json={
        "email": "test@example.com",
        "password": "testpassword",
    })
    assert response.status_code in (401, 403, 404)  # Expecting unauthorized or not found
