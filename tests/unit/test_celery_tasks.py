"""Celery worker/tasks テスト"""
import pytest
from unittest.mock import MagicMock


class TestCreateCeleryApp:

    def test_create_app_config(self):
        from src.scheduler.worker import create_celery_app
        app = create_celery_app()
        assert app.conf.task_serializer == 'json'
        assert app.conf.timezone == 'Asia/Tokyo'


def _call_task(task_proxy, *args, **kwargs):
    """Call the underlying function of a bound Celery task"""
    mock_self = MagicMock()
    mock_self.request.id = "test-req"
    return task_proxy.__wrapped__.__func__(mock_self, *args, **kwargs)


class TestWorkerFunctions:

    def test_execute_task_success(self):
        from src.scheduler.worker import execute_task
        result = _call_task(execute_task, {
            "task_id": "t1",
            "description": "Test",
            "agent_id": "claude_code",
            "model": "claude-sonnet"
        })
        assert result["status"] == "success"
        assert result["task_id"] == "t1"

    def test_execute_task_with_missing_fields(self):
        from src.scheduler.worker import execute_task
        result = _call_task(execute_task, {})
        assert result["status"] == "success"

    def test_schedule_task(self):
        from src.scheduler.worker import schedule_task
        result = _call_task(schedule_task, "t1", "0 9 * * *")
        assert result["status"] == "scheduled"
        assert "t1" in result["message"]

    def test_analyze_logs(self):
        from src.scheduler.worker import analyze_logs
        result = _call_task(analyze_logs, days=7)
        assert result["period_days"] == 7
        assert "7" in result["message"]

    def test_health_check(self):
        from src.scheduler.worker import health_check
        result = _call_task(health_check)
        assert result["status"] == "healthy"
