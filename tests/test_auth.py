import sys
import os
import pytest
from jose import jwt
from backend.app.app import app
from backend.app.model.models import User
from backend.app.repository.mail_handling import NotificationService

async def test_register_success(client):
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "supersecurepassword123",
        "confirm_password": "supersecurepassword123"
    }
    response = await client.post("/auth/register", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Register Sucessful please verify then proceed to login"
    
    # Assert verification email was sent
    sent = app.state.sent_emails
    assert len(sent) == 1
    assert sent[0]["recipients"] == ["newuser@example.com"]
    assert "token=" in sent[0]["context_data"]["url"]

async def test_register_duplicate_email_fails(client, db_session):
    existing_user = User(
        username="duplicate",
        email="duplicate@example.com", 
        password="fakehashedpassword"  
    )
    db_session.add(existing_user)
    await db_session.commit()

    payload = {
        "username": "duplicate",
        "email": "duplicate@example.com",
        "password": "password123",
        "confirm_password": "password123",
    }
    response = await client.post("/auth/register", json=payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Username or Email already registered"

async def test_verify_email(client):
    # Register first
    payload = {
        "username": "verifyuser",
        "email": "verifyuser@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    await client.post("/auth/register", json=payload)
    
    sent = app.state.sent_emails
    assert len(sent) == 1
    magic_url = sent[0]["context_data"]["url"]
    token = magic_url.split("token=")[1]
    
    # Verify email
    response = await client.get(f"/auth/verify-email?token={token}")
    assert response.status_code == 200
    assert response.json()["message"] == "Succesfully verified"
    
    # Invalid token fails
    invalid_resp = await client.get("/auth/verify-email?token=invalid_token_here")
    assert invalid_resp.status_code == 400

async def test_login_success(client):
    # Register
    payload = {
        "username": "loginuser",
        "email": "loginuser@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    await client.post("/auth/register", json=payload)
    
    # Verify
    magic_url = app.state.sent_emails[0]["context_data"]["url"]
    token = magic_url.split("token=")[1]
    await client.get(f"/auth/verify-email?token={token}")
    
    # Login
    login_payload = {
        "username": "loginuser",
        "password": "password123"
    }
    response = await client.post("/auth/login", json=login_payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Login Successful"
    assert "access_token" in client.cookies

async def test_login_unverified_fails(client):
    # Register, but don't verify
    payload = {
        "username": "unverified",
        "email": "unverified@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    await client.post("/auth/register", json=payload)
    
    # Login
    login_payload = {
        "username": "unverified",
        "password": "password123"
    }
    # login endpoint will try to send a verification email again if not verified and it raises 403
    response = await client.post("/auth/login", json=login_payload)
    assert response.status_code == 403
    assert "verify your email address" in response.json()["detail"]

async def test_me_authenticated(auth_client):
    response = await auth_client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert data["user"]["username"] == "authuser"
    assert data["user"]["email"] == "authuser@example.com"

async def test_me_unauthenticated(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401

async def test_logout(auth_client):
    response = await auth_client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful. Session cleared."
    assert "access_token" not in auth_client.cookies or auth_client.cookies.get("access_token") == ""

async def test_password_reset_flow(client, db_session):
    # Register & Verify
    payload = {
        "username": "resetuser",
        "email": "resetuser@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    await client.post("/auth/register", json=payload)
    magic_url = app.state.sent_emails[0]["context_data"]["url"]
    token = magic_url.split("token=")[1]
    await client.get(f"/auth/verify-email?token={token}")
    
    # Request reset
    app.state.sent_emails.clear()
    reset_req = {"email": "resetuser@example.com"}
    response = await client.post("/auth/password-reset", json=reset_req)
    assert response.status_code == 200
    assert response.json()["message"] == "Check you mail"
    
    sent = app.state.sent_emails
    assert len(sent) == 1
    magic_url_reset = sent[0]["context_data"]["url"]
    reset_token = magic_url_reset.split("token=")[1]
    
    # Reset password verify
    reset_verify_payload = {
        "new_password": "newsecurepassword123",
        "confirm_password": "newsecurepassword123"
    }
    verify_resp = await client.post(f"/auth/password-reset-verify?token={reset_token}", json=reset_verify_payload)
    assert verify_resp.status_code == 200
    assert verify_resp.json()["message"] == "Succesful"
    
    # Try login with new password
    login_payload = {
        "username": "resetuser",
        "password": "newsecurepassword123"
    }
    login_resp = await client.post("/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    assert login_resp.json()["message"] == "Login Successful"