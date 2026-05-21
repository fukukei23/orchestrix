"""APIエンドポイントのユニットテスト"""
import pytest


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "services" in data


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Orchestrix API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "operational"


def test_get_tasks_empty(client):
    response = client.get("/api/v1/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0


def test_get_agents(client):
    response = client.get("/api/v1/agents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_login_invalid_credentials(client):
    response = client.post("/api/v1/auth/login", json={
        "username": "nonexistent", "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_create_task(client):
    response = client.post("/api/v1/tasks", json={
        "title": "Test Task", "description": "This is a test task",
        "goal": "Complete the test", "priority": 1
    })
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"
    assert response.json()["status"] == "pending"


def test_get_executions_empty(client):
    response = client.get("/api/v1/executions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
