"""
TaskDecomposer の単体テスト
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.task_decomposer import TaskDecomposer, SubTask


@pytest.fixture
def decomposer():
    """TaskDecomposer インスタンスのフィクスチャ"""
    return TaskDecomposer()


class TestTaskDecomposer:
    """TaskDecomposer のテストクラス"""

    def test_decompose_feature_task(self, decomposer):
        """機能実装タスクの分解をテスト"""
        description = "Implement user authentication feature"
        subtasks = decomposer.decompose(description)

        assert len(subtasks) > 1
        assert subtasks[0].title.startswith("Step 1:")
        assert all(isinstance(task, SubTask) for task in subtasks)

    def test_decompose_bugfix_task(self, decomposer):
        """バグ修正タスクの分解をテスト"""
        description = "Fix login form validation error"
        subtasks = decomposer.decompose(description)

        assert len(subtasks) > 1
        assert "Bug Fix" in subtasks[0].title

    def test_decompose_refactor_task(self, decomposer):
        """リファクタリングタスクの分解をテスト"""
        description = "Refactor database queries for better performance"
        subtasks = decomposer.decompose(description)

        assert len(subtasks) > 1
        assert "Refactor" in subtasks[0].title

    def test_decompose_documentation_task(self, decomposer):
        """ドキュメント作成タスクの分解をテスト"""
        description = "Write documentation for API endpoints"
        subtasks = decomposer.decompose(description)

        assert len(subtasks) > 1
        assert "Documentation" in subtasks[0].title

    def test_decompose_testing_task(self, decomposer):
        """テスト作成タスクの分解をテスト"""
        description = "Write test cases for the authentication module"
        subtasks = decomposer.decompose(description)

        assert len(subtasks) > 1
        assert "Testing" in subtasks[0].title

    def test_subtask_dependencies(self, decomposer):
        """サブタスクの依存関係をテスト"""
        description = "Implement complex feature"
        subtasks = decomposer.decompose(description)

        # 最初のタスクは依存関係がない
        assert len(subtasks[0].dependencies) == 0

        # 2番目以降のタスクは依存関係がある
        if len(subtasks) > 1:
            assert len(subtasks[1].dependencies) >= 1

    def test_build_dag(self, decomposer):
        """DAG構築をテスト"""
        description = "Create a new feature"
        subtasks = decomposer.decompose(description)
        dag = decomposer.build_dag(subtasks)

        assert isinstance(dag, dict)
        # 全てのサブタスクIDがキーとして存在する
        assert set(dag.keys()) == {task.id for task in subtasks}

    def test_max_subtasks_limit(self, decomposer):
        """最大サブタスク数の制限をテスト"""
        description = "Implement a large feature"
        max_subtasks = 5
        subtasks = decomposer.decompose(description, max_subtasks=max_subtasks)

        assert len(subtasks) <= max_subtasks

    def test_complexity_in_subtasks(self, decomposer):
        """サブタスクの複雑度をテスト"""
        description = "Create new user management system"
        subtasks = decomposer.decompose(description)

        # 全てのサブタスクに複雑度が設定されている
        assert all(hasattr(task, 'complexity') for task in subtasks)
        assert all(0 <= task.complexity <= 1.0 for task in subtasks)
