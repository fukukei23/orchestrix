"""Tasks APIルートの詳細テスト"""
import pytest


def _create_task(client, title="Test Task", **kwargs):
    payload = {"title": title, "description": "desc", "goal": "goal", "priority": 1}
    payload.update(kwargs)
    return client.post("/api/v1/tasks", json=payload)


class TestListTasks:

    def test_empty_list(self, client):
        resp = client.get("/api/v1/tasks")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_with_data(self, client):
        _create_task(client, title="Task A")
        resp = client.get("/api/v1/tasks")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_filter_by_status(self, client):
        _create_task(client, title="Pending")
        resp = client.get("/api/v1/tasks", params={"status_filter": "pending"})
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_filter_by_status_no_match(self, client):
        _create_task(client)
        resp = client.get("/api/v1/tasks", params={"status_filter": "completed"})
        assert resp.status_code == 200
        assert len(resp.json()) == 0

    def test_filter_by_priority(self, client):
        _create_task(client, priority=5)
        _create_task(client, title="Low", priority=1)
        resp = client.get("/api/v1/tasks", params={"priority_min": 3})
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_pagination(self, client):
        for i in range(5):
            _create_task(client, title=f"Task {i}")
        resp = client.get("/api/v1/tasks", params={"skip": 2, "limit": 2})
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestGetTask:

    def test_get_existing_task(self, client):
        created = _create_task(client)
        task_id = created.json()["id"]
        resp = client.get(f"/api/v1/tasks/{task_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == task_id

    def test_get_nonexistent_task(self, client):
        resp = client.get("/api/v1/tasks/nonexistent-id")
        assert resp.status_code == 404

    def test_get_task_with_execution(self, client):
        created = _create_task(client)
        task_id = created.json()["id"]
        client.post(f"/api/v1/tasks/{task_id}/execute")
        resp = client.get(f"/api/v1/tasks/{task_id}")
        assert resp.status_code == 200
        assert resp.json()["latest_execution"] is not None


class TestCreateTask:

    def test_create_basic(self, client):
        resp = _create_task(client, title="New Task")
        assert resp.status_code == 201
        assert resp.json()["status"] == "pending"

    def test_create_with_all_fields(self, client):
        resp = client.post("/api/v1/tasks", json={
            "title": "Full Task", "description": "Detailed desc",
            "goal": "Achieve X", "priority": 10, "cron_expression": "0 * * * *",
        })
        assert resp.status_code == 201

    def test_create_defaults(self, client):
        resp = client.post("/api/v1/tasks", json={"title": "Minimal"})
        assert resp.status_code == 201
        assert resp.json()["status"] == "pending"


class TestUpdateTask:

    def test_update_title(self, client):
        created = _create_task(client)
        task_id = created.json()["id"]
        resp = client.put(f"/api/v1/tasks/{task_id}", json={"title": "Updated"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated"

    def test_update_status(self, client):
        created = _create_task(client)
        task_id = created.json()["id"]
        resp = client.put(f"/api/v1/tasks/{task_id}", json={"status": "running"})
        assert resp.status_code == 200
        assert resp.json()["status"] == "running"

    def test_update_nonexistent(self, client):
        resp = client.put("/api/v1/tasks/no-id", json={"title": "X"})
        assert resp.status_code == 404


class TestDeleteTask:

    def test_delete_existing(self, client):
        created = _create_task(client)
        task_id = created.json()["id"]
        resp = client.delete(f"/api/v1/tasks/{task_id}")
        assert resp.status_code == 204

    def test_delete_nonexistent(self, client):
        resp = client.delete("/api/v1/tasks/no-id")
        assert resp.status_code == 404


class TestExecuteTask:

    def test_execute_existing(self, client):
        created = _create_task(client)
        task_id = created.json()["id"]
        resp = client.post(f"/api/v1/tasks/{task_id}/execute")
        assert resp.status_code == 200
        assert resp.json()["status"] == "started"

    def test_execute_nonexistent(self, client):
        resp = client.post("/api/v1/tasks/no-id/execute")
        assert resp.status_code == 404


class TestTaskExecutions:

    def test_executions_empty(self, client):
        created = _create_task(client)
        task_id = created.json()["id"]
        resp = client.get(f"/api/v1/tasks/{task_id}/executions")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_executions_after_execute(self, client):
        created = _create_task(client)
        task_id = created.json()["id"]
        client.post(f"/api/v1/tasks/{task_id}/execute")
        resp = client.get(f"/api/v1/tasks/{task_id}/executions")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_executions_nonexistent_task(self, client):
        resp = client.get("/api/v1/tasks/no-id/executions")
        assert resp.status_code == 404
