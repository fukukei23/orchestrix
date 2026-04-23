"""Task Orchestratorのユニットテスト"""
import pytest
from src.core.master_orchestrator import MasterOrchestrator


@pytest.fixture
def orchestrator():
    """Orchestratorインスタンスフィクスチャ"""
    return MasterOrchestrator()


def test_orchestrate_simple_task(orchestrator: MasterOrchestrator):
    """シンプルなタスクのオーケストレーションをテスト"""
    task_description = "Create a simple function that adds two numbers"

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

    result = orchestrator.orchestrate_task(task_description)

    assert result is not None
    assert result["complexity"] > 0.5  # 複雑なタスク
    assert result["level"] in ["low", "medium", "high", "very_high"]
    assert result["subtasks"] > 2  # 複雑なタスクは複数のサブタスクに分解される


def test_llm_client_error_handling(orchestrator: MasterOrchestrator):
    """LLMクライアントのエラーハンドリングをテスト"""
    # 無効なエージェントタイプを指定
    result = orchestrator.orchestrate_task("Test task", agent_type="invalid_agent")

    assert result is not None
    assert result["status"] == "failed"
    assert "llm_result" in result
    assert result["llm_result"]["success"] is False
    assert "error" in result["llm_result"]
