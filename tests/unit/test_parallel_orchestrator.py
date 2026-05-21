"""ParallelOrchestrator の単体テスト"""
import pytest
from unittest.mock import MagicMock

from src.core.collaboration.parallel import (
    ParallelOrchestrator, ParallelTask, ParallelResult
)


@pytest.fixture
def mock_wrapper():
    wrapper = MagicMock()
    wrapper.execute_command.return_value = {'success': True, 'output': 'test output'}
    wrapper.estimate_cost.return_value = 0.01
    return wrapper


@pytest.fixture
def orchestrator(mock_wrapper):
    return ParallelOrchestrator(mock_wrapper)


def _make_result(task_id, agent_id, model, success, exec_time=1.0, cost=0.01, output='out'):
    return ParallelResult(
        task_id=task_id, agent_id=agent_id, model=model,
        success=success, output=output,
        execution_time=exec_time, cost_usd=cost
    )


class TestExecuteParallel:

    def test_all_succeed(self, orchestrator, mock_wrapper):
        """全エージェント成功"""
        configs = [
            {'agent_id': 'claude_code', 'model': 'sonnet'},
            {'agent_id': 'codex_cli', 'model': 'gpt-4'},
        ]

        result = orchestrator.execute_parallel("test prompt", configs)

        assert result['success'] is True
        assert result['total_tasks'] == 2
        assert result['successful_tasks'] == 2
        assert result['failed_tasks'] == 0

    def test_partial_failure(self, orchestrator, mock_wrapper):
        """一部エージェント失敗"""
        mock_wrapper.execute_command.side_effect = [
            {'success': False, 'output': '', 'error': 'timeout'},
            {'success': True, 'output': 'ok'},
        ]

        configs = [
            {'agent_id': 'claude_code', 'model': 'sonnet'},
            {'agent_id': 'codex_cli', 'model': 'gpt-4'},
        ]

        result = orchestrator.execute_parallel("test prompt", configs)

        assert result['success'] is True
        assert result['successful_tasks'] == 1
        assert result['failed_tasks'] == 1

    def test_all_fail(self, orchestrator, mock_wrapper):
        """全エージェント失敗"""
        mock_wrapper.execute_command.return_value = {'success': False, 'error': 'fail'}

        configs = [{'agent_id': 'claude_code', 'model': 'sonnet'}]

        result = orchestrator.execute_parallel("test prompt", configs)

        assert result['success'] is False

    def test_max_workers_limit(self, orchestrator, mock_wrapper):
        """最大並列数制限"""
        configs = [
            {'agent_id': f'agent_{i}', 'model': 'm'} for i in range(5)
        ]

        result = orchestrator.execute_parallel("test prompt", configs, max_workers=2)

        assert result['total_tasks'] == 2

    def test_total_cost_accumulated(self, orchestrator, mock_wrapper):
        """コスト合算"""
        mock_wrapper.estimate_cost.return_value = 0.03

        configs = [
            {'agent_id': 'claude_code', 'model': 'sonnet'},
            {'agent_id': 'codex_cli', 'model': 'gpt-4'},
        ]

        result = orchestrator.execute_parallel("test prompt", configs)

        assert result['total_cost'] == 0.06

    def test_best_result_selected(self, orchestrator, mock_wrapper):
        """最良結果が選択される"""
        result = orchestrator.execute_parallel("test prompt", [
            {'agent_id': 'claude_code', 'model': 'sonnet'},
        ])

        assert result['best_result'] is not None


class TestSelectBestResult:

    def test_select_fastest_and_cheapest(self, orchestrator):
        """最速かつ最安を選択"""
        results = [
            _make_result('1', 'a', 'm1', True, exec_time=1.0, cost=0.05),
            _make_result('2', 'b', 'm2', True, exec_time=0.5, cost=0.01),
            _make_result('3', 'c', 'm3', True, exec_time=2.0, cost=0.02),
        ]

        best = orchestrator._select_best_result(results)

        assert best.task_id == '2'

    def test_all_failed_returns_first(self, orchestrator):
        """全失敗時は最初の結果"""
        results = [
            _make_result('1', 'a', 'm', False),
            _make_result('2', 'b', 'm', False),
        ]

        best = orchestrator._select_best_result(results)

        assert best.task_id == '1'

    def test_empty_results(self, orchestrator):
        """結果なし"""
        best = orchestrator._select_best_result([])
        assert best is None

    def test_prefers_successful_over_failed(self, orchestrator):
        """成功を優先"""
        results = [
            _make_result('1', 'a', 'm', False, exec_time=0.1, cost=0.001),
            _make_result('2', 'b', 'm', True, exec_time=10.0, cost=1.0),
        ]

        best = orchestrator._select_best_result(results)

        assert best.success is True


class TestConfigs:

    def test_diverse_agent_config(self, orchestrator):
        """多様エージェント設定"""
        configs = orchestrator.create_diverse_agent_config()

        assert len(configs) == 3
        agent_ids = [c['agent_id'] for c in configs]
        assert 'claude_code' in agent_ids

    def test_same_agent_different_model_config(self, orchestrator):
        """同一エージェント・異モデル設定"""
        configs = orchestrator.create_same_agent_different_model_config()

        assert len(configs) == 3
        assert all(c['agent_id'] == 'claude_code' for c in configs)
        models = [c['model'] for c in configs]
        assert len(set(models)) == 3


class TestCompareResults:

    def test_compare_mixed_results(self, orchestrator):
        """結果比較"""
        results = [
            _make_result('1', 'claude', 'sonnet', True, exec_time=1.0, cost=0.03, output='short'),
            _make_result('2', 'codex', 'gpt-4', True, exec_time=2.0, cost=0.06, output='longer output here'),
        ]

        comparison = orchestrator.compare_results(results)

        assert comparison['total_results'] == 2
        assert comparison['successful'] == 2
        assert len(comparison['metrics']) == 2

    def test_compare_empty_results(self, orchestrator):
        """空結果の比較"""
        comparison = orchestrator.compare_results([])
        assert 'error' in comparison

    def test_compare_with_similarities(self, orchestrator):
        """類似度計算"""
        results = [
            _make_result('1', 'a', 'm', True, output='hello world'),
            _make_result('2', 'b', 'm', True, output='hello world'),
        ]

        comparison = orchestrator.compare_results(results)

        assert 'output_similarities' in comparison
        assert len(comparison['output_similarities']) == 1
        assert comparison['output_similarities'][0]['similarity'] == 1.0
