"""Database Models テスト"""
import pytest

from src.database.models import Task, Execution, User, AgentConfig, generate_uuid


class TestGenerateUuid:

    def test_returns_string(self):
        result = generate_uuid()
        assert isinstance(result, str)

    def test_unique_values(self):
        ids = {generate_uuid() for _ in range(100)}
        assert len(ids) == 100

    def test_valid_uuid_format(self):
        import uuid
        result = generate_uuid()
        parsed = uuid.UUID(result)
        assert str(parsed) == result


class TestTaskModel:

    def test_create_and_retrieve(self, client):
        resp = client.post("/api/v1/tasks", json={"title": "Model Test", "goal": "Goal"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "pending"
        assert len(data["id"]) == 36

        fetched = client.get(f"/api/v1/tasks/{data['id']}")
        assert fetched.status_code == 200
        assert fetched.json()["title"] == "Model Test"

    def test_task_with_all_fields(self, client):
        resp = client.post("/api/v1/tasks", json={
            "title": "Full Task",
            "description": "Detailed",
            "goal": "Achieve X",
            "priority": 5,
            "cron_expression": "0 * * * *"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Full Task"


class TestExecutionModel:

    def test_execution_via_api(self, client):
        created = client.post("/api/v1/tasks", json={"title": "T", "goal": "G"})
        task_id = created.json()["id"]
        resp = client.post(f"/api/v1/tasks/{task_id}/execute")
        assert resp.status_code == 200

        execs = client.get(f"/api/v1/tasks/{task_id}/executions").json()
        assert len(execs) == 1
        assert execs[0]["task_id"] == task_id


class TestUserModel:

    def test_user_via_api(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "username": "modeluser", "email": "mu@e.com", "password": "Pass1234"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert len(data["id"]) == 36
        assert data["username"] == "modeluser"


class TestAgentConfigModel:

    def test_config_fields(self):
        config = AgentConfig(name="test_agent", cli_command="echo hi")
        assert config.name == "test_agent"
        assert config.cli_command == "echo hi"
