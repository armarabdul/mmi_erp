import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"

def test_admin_login():
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@mmi-demo.com",
        "password": "Demo@12345"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "Admin"
    assert data["user"]["email"] == "admin@mmi-demo.com"

def test_branch_manager_login():
    res = client.post("/api/v1/auth/login", json={
        "email": "manager@mmi-demo.com",
        "password": "Demo@12345"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["role"] == "Branch Manager"
    assert data["user"]["branch_id"] is not None

def test_invalid_login():
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@mmi-demo.com",
        "password": "WrongPassword!"
    })
    assert res.status_code == 401

def test_protected_routes_unauthorized():
    res = client.get("/api/v1/dashboard")
    assert res.status_code == 401
