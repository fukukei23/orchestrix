"""APIエンドポイントのユニットテスト"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.main import app
from src.database.models import Base

# テスト用データベース設定
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def client():
    """FastAPIテストクライアント"""
    return TestClient(app)


@pytest.fixture
def db_session():
    """データベースセッションフィクスチャ"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_health_check(client: TestClient):
    """ヘルスチェックエンドポイントのテスト"""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "services" in data
    assert data["services"]["api"] == "operational"
    assert data["services"]["database"] == "operational"
    assert data["services"]["redis"] == "operational"


def test_root_endpoint(client: TestClient):
    """ルートエンドポイントのテスト"""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "Orchestrix API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "operational"


def test_get_tasks_empty(client: TestClient, db_session):
    """空のタスクリストを取得するテスト"""
    response = client.get("/api/v1/tasks")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 0


def test_get_agents(client: TestClient):
    """エージェントリストを取得するテスト"""
    response = client.get("/api/v1/agents")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0  # 定義済みのエージェントが存在する


def test_login_invalid_credentials(client: TestClient):
    """無効な認証情報でログインを試みるテスト"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401
    data = response.json()

    assert "detail" in data


def test_create_task(client: TestClient):
    """タスク作成のテスト"""
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "goal": "Complete the test",
        "priority": 1
    }

    response = client.post("/api/v1/tasks", json=task_data)

    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["title"] == "Test Task"
    assert data["status"] == "pending"


def test_get_executions_empty(client: TestClient):
    """空の実行履歴を取得するテスト"""
    response = client.get("/api/v1/executions")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
