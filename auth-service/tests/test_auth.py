import pytest


# ---------- health ----------

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "auth-service"
    assert "db" in body
    assert "version" in body


# ---------- register ----------

def test_register_new_user(client):
    resp = client.post("/auth/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "secret123",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["username"] == "testuser"
    assert body["role"] == "user"


def test_register_duplicate_username(client):
    client.post("/auth/register", json={
        "username": "dupuser",
        "email": "dup1@example.com",
        "password": "secret123",
    })
    resp = client.post("/auth/register", json={
        "username": "dupuser",
        "email": "dup2@example.com",
        "password": "secret123",
    })
    assert resp.status_code == 400


def test_register_cannot_self_assign_admin(client):
    """Role field must be 'user' or 'admin' (enum) — no free-text injection."""
    resp = client.post("/auth/register", json={
        "username": "hacker",
        "email": "hacker@example.com",
        "password": "secret123",
        "role": "superuser",  # invalid enum value
    })
    assert resp.status_code == 422


# ---------- login ----------

def test_login_success(client):
    client.post("/auth/register", json={
        "username": "loginuser",
        "email": "loginuser@example.com",
        "password": "mypassword",
    })
    resp = client.post(
        "/auth/login",
        data={"username": "loginuser", "password": "mypassword"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"
    assert body["role"] == "user"


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "username": "pwduser",
        "email": "pwduser@example.com",
        "password": "correct",
    })
    resp = client.post(
        "/auth/login",
        data={"username": "pwduser", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_login_nonexistent_user(client):
    resp = client.post(
        "/auth/login",
        data={"username": "nobody", "password": "anything"},
    )
    assert resp.status_code == 401


# ---------- verify ----------

def test_verify_valid_token(client):
    client.post("/auth/register", json={
        "username": "verifyuser",
        "email": "verifyuser@example.com",
        "password": "pass",
    })
    token = client.post(
        "/auth/login",
        data={"username": "verifyuser", "password": "pass"},
    ).json()["access_token"]

    resp = client.get("/auth/verify", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == "verifyuser"
    assert body["role"] == "user"


def test_verify_invalid_token(client):
    resp = client.get("/auth/verify", headers={"Authorization": "Bearer totally.invalid.token"})
    assert resp.status_code == 401


# ---------- refresh ----------

def test_refresh_returns_new_access_token(client):
    client.post("/auth/register", json={
        "username": "refreshuser",
        "email": "refreshuser@example.com",
        "password": "pass",
    })
    tokens = client.post(
        "/auth/login",
        data={"username": "refreshuser", "password": "pass"},
    ).json()

    resp = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["access_token"] != tokens["access_token"]


# ---------- logout ----------

def test_logout_revokes_token(client):
    client.post("/auth/register", json={
        "username": "logoutuser",
        "email": "logoutuser@example.com",
        "password": "pass",
    })
    token = client.post(
        "/auth/login",
        data={"username": "logoutuser", "password": "pass"},
    ).json()["access_token"]

    resp = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    # Token must be rejected after logout
    resp = client.get("/auth/verify", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


# ---------- mock-token removed ----------

def test_mock_token_endpoint_removed(client):
    resp = client.get("/auth/mock-token")
    assert resp.status_code == 404
