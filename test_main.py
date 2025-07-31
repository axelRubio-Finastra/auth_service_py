## test_main.py

from fastapi.testclient import TestClient
from app.main import app
from app import auth
from app.database import SessionLocal
from app.models import User
import pytest
from unittest.mock import patch

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_users():
    yield
    db = SessionLocal()
    db.query(User).delete()
    db.commit()
    db.close()

def test_signup_invalid_email():
    response = client.post("/signup", json={
        "email": "invalid",
        "password": "12345678",
        "name": "Test",
        "last_name": "User"
    })
    assert response.status_code == 422

def test_signup_success():
    with patch("app.email_utils.send_verification_email") as mock_send:
        response = client.post("/signup", json={
            "email": "testuser@example.com",
            "password": "strongpassword",
            "name": "Test",
            "last_name": "User"
        })
        assert response.status_code == 200
        mock_send.assert_called_once()

def test_signup_duplicate():
    # First signup
    client.post("/signup", json={
        "email": "dupe@example.com",
        "password": "strongpassword",
        "name": "Test",
        "last_name": "User"
    })
    # Duplicate signup
    response = client.post("/signup", json={
        "email": "dupe@example.com",
        "password": "strongpassword",
        "name": "Test",
        "last_name": "User"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_unverified():
    client.post("/signup", json={
        "email": "unverified@example.com",
        "password": "strongpassword",
        "name": "Test",
        "last_name": "User"
    })
    response = client.post("/login", json={
        "email": "unverified@example.com",
        "password": "strongpassword"
    })
    assert response.status_code == 403
    assert "Email not verified" in response.json()["detail"]

def test_resend_verification():
    client.post("/signup", json={
        "email": "resend@example.com",
        "password": "strongpassword",
        "name": "Test",
        "last_name": "User"
    })
    response = client.post("/resend-verification-email", json={"email": "resend@example.com"})
    assert response.status_code == 200
    assert "Verification email resent" in response.json()["msg"]

def test_verify_email():
    signup_resp = client.post("/signup", json={
        "email": "verifyme@example.com",
        "password": "strongpassword",
        "name": "Verify",
        "last_name": "Me"
    })
    assert signup_resp.status_code == 200

    # Fetch the token from the database
    db = SessionLocal()
    user = db.query(User).filter(User.email == "verifyme@example.com").first()
    token = user.verification_token
    db.close()

    verify_resp = client.get(f"/verify-email?token={token}")
    assert verify_resp.status_code == 200
    assert "Email successfully verified" in verify_resp.json()["message"]

def test_admin_only_route():
    # Generate a token with admin role
    token = auth.create_access_token("admin@example.com", "admin")
    headers = {"token": token}
    resp = client.get("/admin-only", headers=headers)
    assert resp.status_code == 200
    assert "Welcome to the admin route!" in resp.json()["message"]

    # Test with non-admin role
    user_token = auth.create_access_token("user@example.com", "user")
    headers = {"token": user_token}
    resp = client.get("/admin-only", headers=headers)
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Not authorized"
