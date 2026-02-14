"""
ComplexityAnalyzer の単体テスト
"""

import pytest
import sys
import os

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.complexity_analyzer import ComplexityAnalyzer


@pytest.fixture
def analyzer():
    """ComplexityAnalyzer インスタンスのフィクスチャ"""
    return ComplexityAnalyzer()


class TestComplexityAnalyzer:
    """ComplexityAnalyzer のテストクラス"""

    def test_simple_task(self, analyzer):
        """単純なタスクの複雑度をテスト"""
        description = "Fix a bug in the login form"
        complexity = analyzer.analyze(description)

        assert 0.0 <= complexity <= 1.0
        assert analyzer.get_complexity_level(complexity) in ['simple', 'medium', 'complex']
        assert complexity < 0.35  # 単純なは低い

    def test_medium_task(self, analyzer):
        """中程度なタスクの複雑度をテスト"""
        description = """
        Implement user authentication with JWT tokens.
        Create login and registration endpoints.
        Add password hashing and validation.
        Set up database models for users.
        """
        complexity = analyzer.analyze(description)

        assert 0.0 <= complexity <= 1.0
        assert 0.35 <= complexity < 0.65  # 中程度

    def test_complex_task(self, analyzer):
        """複雑なタスクの複雑度をテスト"""
        description = """
        Design and implement a microservices architecture.
        Set up Kubernetes deployment with Docker.
        Implement inter-service communication with gRPC.
        Add distributed tracing and monitoring.
        Create CI/CD pipelines with Jenkins.
        Set up service mesh with Istio.
        """
        complexity = analyzer.analyze(description)

        assert 0.0 <= complexity <= 1.0
        assert complexity >= 0.65  # 複雑

    def test_with_context(self, analyzer):
        """コンテキスト付きの複雑度分析をテスト"""
        description = "Create REST API for task management"

        context = {
            'dependencies': ['task', 'user', 'auth'],
            'files': ['tasks.py', 'models.py', 'serializers.py']
        }

        complexity = analyzer.analyze(description, context)

        assert 0.0 <= complexity <= 1.0
        # 依存関係とファイルで複雑度が上がる
        assert complexity > 0.3

    def test_length_analysis(self, analyzer):
        """説明の長さによる分析をテスト"""
        short_desc = "Fix bug"
        long_desc = "Implement a comprehensive feature with multiple components and extensive error handling"

        short_complexity = analyzer.analyze(short_desc)
        long_complexity = analyzer.analyze(long_desc)

        assert long_complexity > short_complexity

    def test_technical_terms(self, analyzer):
        """技術用語の数による分析をテスト"""
        no_tech_desc = "Create a simple button"
        tech_desc = "Implement React component with TypeScript, use hooks for state management, integrate with FastAPI backend, add unit tests with pytest"

        no_tech_complexity = analyzer.analyze(no_tech_desc)
        tech_complexity = analyzer.analyze(tech_desc)

        assert tech_complexity > no_tech_complexity

    def test_get_complexity_level(self, analyzer):
        """複雑度レベルの取得をテスト"""
        assert analyzer.get_complexity_level(0.2) == 'simple'
        assert analyzer.get_complexity_level(0.5) == 'medium'
        assert analyzer.get_complexity_level(0.8) == 'complex'

    def test_weights_sum_to_one(self, analyzer):
        """全ての重みが1.0であることをテスト"""
        total_weight = sum(analyzer.weights.values())
        assert total_weight == 1.0
