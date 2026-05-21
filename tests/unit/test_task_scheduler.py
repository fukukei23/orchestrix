"""TaskScheduler テスト"""
import pytest
from unittest.mock import MagicMock, patch

from src.scheduler.task_scheduler import TaskScheduler


@pytest.fixture
def mock_celery():
    app = MagicMock()
    app.conf.beat_schedule = {}
    return app


@pytest.fixture
def scheduler(mock_celery):
    return TaskScheduler(mock_celery, broker_url="redis://localhost:6379/0")


class TestInit:

    def test_configures_broker(self, mock_celery):
        TaskScheduler(mock_celery, broker_url="redis://test:6379")
        assert mock_celery.conf.broker_url == "redis://test:6379"

    def test_configures_result_backend_default(self, mock_celery):
        TaskScheduler(mock_celery, broker_url="redis://test:6379")
        assert mock_celery.conf.result_backend == "redis://test:6379"

    def test_configures_result_backend_custom(self, mock_celery):
        TaskScheduler(mock_celery, broker_url="redis://test:6379", result_backend="redis://other:6379")
        assert mock_celery.conf.result_backend == "redis://other:6379"


class TestScheduleTask:

    def test_schedule_enabled(self, scheduler, mock_celery):
        result = scheduler.schedule_task("my_task", "0 9 * * *", "t1")
        assert result is True
        assert "schedule-t1" in mock_celery.conf.beat_schedule

    def test_schedule_disabled(self, scheduler, mock_celery):
        mock_celery.conf.beat_schedule["schedule-t1"] = {"task": "x"}
        result = scheduler.schedule_task("my_task", "0 9 * * *", "t1", enabled=False)
        assert result is True
        assert "schedule-t1" not in mock_celery.conf.beat_schedule

    def test_invalid_cron_returns_false(self, scheduler):
        result = scheduler.schedule_task("my_task", "invalid", "t1")
        assert result is False


class TestValidateCron:

    def test_valid_cron(self, scheduler):
        result = scheduler.validate_cron_expression("0 9 * * *")
        assert result["valid"] is True

    def test_invalid_parts_count(self, scheduler):
        result = scheduler.validate_cron_expression("0 9 * *")
        assert result["valid"] is False
        assert "5 parts" in result["error"]

    def test_invalid_minute(self, scheduler):
        result = scheduler.validate_cron_expression("60 9 * * *")
        assert result["valid"] is False

    def test_wildcard_is_valid(self, scheduler):
        result = scheduler.validate_cron_expression("* * * * *")
        assert result["valid"] is True


class TestUnschedule:

    def test_unschedule_existing(self, scheduler, mock_celery):
        mock_celery.conf.beat_schedule["schedule-t1"] = {"task": "x"}
        result = scheduler.unschedule_task("t1")
        assert result is True
        assert "schedule-t1" not in mock_celery.conf.beat_schedule

    def test_unschedule_nonexistent(self, scheduler):
        result = scheduler.unschedule_task("ghost")
        assert result is False


class TestNaturalLanguage:

    def test_daily_9am(self, scheduler, mock_celery):
        result = scheduler.schedule_natural_language("毎日9時に実行", "task1", "t1")
        assert result["parsed"] is True
        assert result["cron_expression"] == "0 9 * * *"

    def test_every_hour(self, scheduler, mock_celery):
        result = scheduler.schedule_natural_language("毎時実行", "task1", "t1")
        assert result["parsed"] is True
        assert result["cron_expression"] == "0 * * * *"

    def test_unknown_defaults_to_9am(self, scheduler, mock_celery):
        result = scheduler.schedule_natural_language("不明なパターン", "task1", "t1")
        assert result["parsed"] is True
        assert result["cron_expression"] == "0 9 * * *"
