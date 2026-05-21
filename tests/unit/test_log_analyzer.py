"""Log Analyzer テスト"""
import pytest
from datetime import datetime, timedelta

from src.analytics.log_analyzer import LogAnalyzer


@pytest.fixture
def analyzer():
    return LogAnalyzer()


def _make_execution(status="success", agent_type="claude_code", model_used="claude-sonnet",
                    cost_usd=0.01, hours_ago=0, exit_code=0,
                    input_tokens=100, output_tokens=50):
    now = datetime.utcnow()
    return {
        "status": status,
        "agent_type": agent_type,
        "model_used": model_used,
        "cost_usd": cost_usd,
        "created_at": (now - timedelta(hours=hours_ago)).isoformat(),
        "start_time": (now - timedelta(hours=hours_ago, minutes=5)).isoformat(),
        "end_time": (now - timedelta(hours=hours_ago)).isoformat(),
        "exit_code": exit_code,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }


class TestAnalyzeExecutions:

    def test_empty_returns_error(self, analyzer):
        result = analyzer.analyze_executions([])
        assert "error" in result

    def test_basic_analysis_structure(self, analyzer):
        data = [_make_execution()]
        result = analyzer.analyze_executions(data)
        assert "total_executions" in result
        assert "success_rate" in result
        assert "cost_analysis" in result
        assert result["total_executions"] == 1

    def test_time_range_filter(self, analyzer):
        old = _make_execution(hours_ago=48)
        recent = _make_execution(hours_ago=1)
        now = datetime.utcnow()
        result = analyzer.analyze_executions(
            [old, recent],
            time_range={"start": now - timedelta(hours=24),
                        "end": now}
        )
        assert result["total_executions"] == 1


class TestSuccessRate:

    def test_all_success(self, analyzer):
        data = [_make_execution(), _make_execution()]
        result = analyzer.analyze_executions(data)
        assert result["success_rate"]["success_rate"] == 1.0

    def test_mixed_success_failure(self, analyzer):
        data = [_make_execution(status="success"), _make_execution(status="failed")]
        result = analyzer.analyze_executions(data)
        assert result["success_rate"]["success_rate"] == 0.5
        assert result["success_rate"]["failed"] == 1

    def test_trend_improving(self, analyzer):
        data = [
            _make_execution(status="failed", hours_ago=200),
            _make_execution(status="failed", hours_ago=180),
            _make_execution(status="success", hours_ago=5),
            _make_execution(status="success", hours_ago=3),
        ]
        result = analyzer.analyze_executions(data)
        assert result["success_rate"]["trend"] == "improving"

    def test_trend_declining(self, analyzer):
        data = [
            _make_execution(status="success", hours_ago=200),
            _make_execution(status="success", hours_ago=180),
            _make_execution(status="failed", hours_ago=5),
            _make_execution(status="failed", hours_ago=3),
        ]
        result = analyzer.analyze_executions(data)
        assert result["success_rate"]["trend"] == "declining"


class TestCostAnalysis:

    def test_cost_calculation(self, analyzer):
        data = [_make_execution(cost_usd=0.05), _make_execution(cost_usd=0.15)]
        result = analyzer.analyze_executions(data)
        cost = result["cost_analysis"]
        assert cost["total_cost"] == pytest.approx(0.20)
        assert cost["avg_cost"] == pytest.approx(0.10)

    def test_cost_distribution(self, analyzer):
        data = [
            _make_execution(cost_usd=0.005),
            _make_execution(cost_usd=0.05),
            _make_execution(cost_usd=0.50),
            _make_execution(cost_usd=5.0),
        ]
        result = analyzer.analyze_executions(data)
        dist = result["cost_analysis"]["cost_distribution"]
        assert dist["under_0.01"] == 1
        assert dist["0.01_to_0.1"] == 1
        assert dist["0.1_to_1.0"] == 1
        assert dist["1.0_to_10.0"] == 1


class TestAgentPerformance:

    def test_agent_breakdown(self, analyzer):
        data = [
            _make_execution(agent_type="claude_code", status="success"),
            _make_execution(agent_type="openai", status="failed"),
        ]
        result = analyzer.analyze_executions(data)
        ap = result["agent_performance"]
        assert "claude_code" in ap
        assert ap["claude_code"]["success_rate"] == 1.0
        assert "openai" in ap
        assert ap["openai"]["success_rate"] == 0.0


class TestModelPerformance:

    def test_model_breakdown(self, analyzer):
        data = [
            _make_execution(model_used="gpt-4o", input_tokens=200, output_tokens=100),
            _make_execution(model_used="claude-sonnet", input_tokens=50, output_tokens=25),
        ]
        result = analyzer.analyze_executions(data)
        mp = result["model_performance"]
        assert "gpt-4o" in mp
        assert mp["gpt-4o"]["total_input_tokens"] == 200
        assert "claude-sonnet" in mp
        assert mp["claude-sonnet"]["total_input_tokens"] == 50


class TestTemporalAnalysis:

    def test_temporal_structure(self, analyzer):
        data = [_make_execution(hours_ago=10)]
        result = analyzer.analyze_executions(data)
        ta = result["temporal_analysis"]
        assert "hourly_distribution" in ta
        assert "daily_distribution" in ta


class TestErrorPatterns:

    def test_no_errors(self, analyzer):
        data = [_make_execution(status="success")]
        result = analyzer.analyze_executions(data)
        assert result["error_patterns"]["total_errors"] == 0

    def test_error_by_agent(self, analyzer):
        data = [
            _make_execution(status="failed", agent_type="claude_code", exit_code=1),
            _make_execution(status="failed", agent_type="claude_code", exit_code=1),
            _make_execution(status="success"),
        ]
        result = analyzer.analyze_executions(data)
        ep = result["error_patterns"]
        assert ep["total_errors"] == 2
        assert ep["error_rate"] == pytest.approx(2 / 3)


class TestClusterTasks:

    def test_basic_clustering(self, analyzer):
        tasks = [
            {"complexity_score": 0.1, "priority": 1, "cost_usd": 0.01},
            {"complexity_score": 0.9, "priority": 10, "cost_usd": 5.0},
            {"complexity_score": 0.5, "priority": 5, "cost_usd": 1.0},
        ]
        result = analyzer.cluster_tasks(tasks, n_clusters=2)
        assert "cluster_analysis" in result
        assert result["n_clusters"] == 2

    def test_no_features_returns_error(self, analyzer):
        result = analyzer.cluster_tasks([{"title": "no features"}])
        assert "error" in result


class TestRecommendOptimalAllocation:

    def test_recommend_high_success_agent(self, analyzer):
        analysis = {
            "agent_performance": {
                "claude_code": {"success_rate": 0.95, "avg_cost": 0.01},
                "openai": {"success_rate": 0.70, "avg_cost": 0.02},
            }
        }
        result = analyzer.recommend_optimal_allocation(analysis)
        assert result["total_recommendations"] >= 1
        rec_types = [r["type"] for r in result["recommendations"]]
        assert "high_success_rate" in rec_types

    def test_recommend_cost_efficient_model(self, analyzer):
        analysis = {
            "model_performance": {
                "gpt-4o": {"success_rate": 0.9, "avg_cost": 0.05},
                "gpt-3.5": {"success_rate": 0.85, "avg_cost": 0.01},
            }
        }
        result = analyzer.recommend_optimal_allocation(analysis)
        rec_types = [r["type"] for r in result["recommendations"]]
        assert "cost_efficient" in rec_types

    def test_empty_analysis_returns_empty(self, analyzer):
        result = analyzer.recommend_optimal_allocation({})
        assert result["total_recommendations"] == 0
