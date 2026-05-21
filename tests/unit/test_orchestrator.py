"""Task Orchestratorのユニットテスト"""
import pytest
from unittest.mock import patch, MagicMock

from src.core.master_orchestrator import MasterOrchestrator


@pytest.fixture
def orchestrator():
    """Orchestratorインスタンスフィクスチャ"""
    return MasterOrchestrator()


def test_orchestrate_simple_task(orchestrator: MasterOrchestrator):
    """シンプルなタスクのオーケストレーションをテスト"""
    task_description = "Create a simple function that adds two numbers"

    mock_client = MagicMock()
    mock_client.invoke.return_value = {"success": True, "model": "test-model"}

    with patch.object(orchestrator.llm_factory, 'get_client', return_value=mock_client):
        result = orchestrator.orchestrate_task(task_description)

    assert result is not None
    assert "complexity" in result
    assert "level" in result
    assert "subtasks" in result
    assert result["status"] == "completed"


def test_orchestrate_complex_task(orchestrator: MasterOrchestrator):
    """複雑なタスクのオーケストレーションをテスト"""
    task_description = """
    Create a comprehensive web application with the following features:
    - User authentication with JWT tokens
    - RESTful API with FastAPI
    - Database integration with PostgreSQL
    - Frontend built with React and Vite
    - Task scheduling with Celery
    - Integration with multiple LLM providers (Claude, OpenAI)
    - Automated testing pipeline
    - Docker containerization
    """

    mock_client = MagicMock()
    mock_client.invoke.return_value = {"success": True, "model": "test-model"}

    with patch.object(orchestrator.llm_factory, 'get_client', return_value=mock_client):
        result = orchestrator.orchestrate_task(task_description)

    assert result is not None
    assert result["complexity"] > 0.3
    assert result["level"] in ["low", "medium", "high", "very_high", "simple", "complex"]
    assert result["subtasks"] >= 1


def test_llm_client_error_handling(orchestrator: MasterOrchestrator):
    """LLMクライアントのエラーハンドリングをテスト"""
    # 無効なエージェントタイプを指定
    result = orchestrator.orchestrate_task("Test task", agent_type="invalid_agent")

    assert result is not None
    assert result["status"] == "failed"
    assert "llm_result" in result
    assert result["llm_result"]["success"] is False
    assert "error" in result["llm_result"]
