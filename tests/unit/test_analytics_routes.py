"""Analytics APIルートのテスト"""
import pytest
from datetime import datetime, timedelta


def _create_execution(client, task_id=None, agent_type="claude_code",
                      model_used="claude-sonnet", status="success",
                      cost_usd=0.05, exit_code=0,
                      input_tokens=100, output_tokens=50):
    if task_id is None:
        resp = client.post("/api/v1/tasks", json={"title": "T", "goal": "G"})
        task_id = resp.json()["id"]
    client.post(f"/api/v1/tasks/{task_id}/execute")
    return task_id


class TestExecutionSummary:

    def test_summary_empty(self, client):
        resp = client.get("/api/v1/analytics/executions/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_executions"] == 0
        assert data["success_rate"] == 0.0

    def test_summary_with_data(self, client):
        _create_execution(client)
        resp = client.get("/api/v1/analytics/executions/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_executions"] >= 1


class TestAgentPerformance:

    def test_empty(self, client):
        resp = client.get("/api/v1/analytics/agent-performance")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_with_data(self, client):
        _create_execution(client, agent_type="claude_code")
        resp = client.get("/api/v1/analytics/agent-performance")
        assert resp.status_code == 200
        data = resp.json()
        assert any(a["agent_id"] == "claude_code" for a in data)


class TestModelPerformance:

    def test_empty(self, client):
        resp = client.get("/api/v1/analytics/model-performance")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_with_data(self, client):
        _create_execution(client)
        resp = client.get("/api/v1/analytics/model-performance")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0
        assert "model_id" in data[0]


class TestErrorAnalysis:

    def test_no_errors(self, client):
        resp = client.get("/api/v1/analytics/error-analysis")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_errors"] == 0

    def test_with_errors(self, client):
        _create_execution(client)
        resp = client.get("/api/v1/analytics/error-analysis")
        assert resp.status_code == 200
        assert "total_errors" in resp.json()


class TestTrends:

    def test_no_data(self, client):
        resp = client.get("/api/v1/analytics/trends")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_executions"] == 0

    def test_with_data(self, client):
        _create_execution(client)
        resp = client.get("/api/v1/analytics/trends")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_executions"] >= 1
