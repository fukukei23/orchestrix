"""PipelineOrchestrator の単体テスト"""
import pytest
from unittest.mock import MagicMock

from src.core.collaboration.pipeline import (
    PipelineOrchestrator, PipelineStep
)


@pytest.fixture
def mock_wrapper():
    wrapper = MagicMock()
    wrapper.execute_command.return_value = {'success': True, 'output': 'step output'}
    wrapper.estimate_cost.return_value = 0.02
    return wrapper


@pytest.fixture
def orchestrator(mock_wrapper):
    return PipelineOrchestrator(mock_wrapper)


@pytest.fixture
def simple_pipeline():
    return [
        {'agent_id': 'claude_code', 'model': 'sonnet', 'prompt_template': 'Review: {input}'},
    ]


@pytest.fixture
def multi_step_pipeline():
    return [
        {
            'agent_id': 'claude_code',
            'model': 'haiku',
            'prompt_template': 'Analyze: {input}',
            'use_previous_output': False,
        },
        {
            'agent_id': 'codex_cli',
            'model': 'gpt-4',
            'prompt_template': 'Implement: {input}',
            'use_previous_output': True,
        },
    ]


class TestExecutePipeline:

    def test_single_step_success(self, orchestrator, simple_pipeline):
        """単一ステップ成功"""
        result = orchestrator.execute_pipeline("test code", simple_pipeline)

        assert result['success'] is True
        assert result['completed_steps'] == 1
        assert result['successful_steps'] == 1

    def test_multi_step_success(self, orchestrator, multi_step_pipeline):
        """複数ステップ成功"""
        result = orchestrator.execute_pipeline("test code", multi_step_pipeline)

        assert result['success'] is True
        assert result['completed_steps'] == 2
        assert result['final_output'] == 'step output'

    def test_step_failure_aborts_pipeline(self, orchestrator, multi_step_pipeline, mock_wrapper):
        """途中ステップ失敗で中断"""
        mock_wrapper.execute_command.side_effect = [
            {'success': False, 'error': 'API error'},
        ]

        result = orchestrator.execute_pipeline("test code", multi_step_pipeline)

        assert result['success'] is False
        assert result['completed_steps'] == 1
        assert 'failed' in result['error']

    def test_empty_pipeline(self, orchestrator):
        """空パイプライン"""
        result = orchestrator.execute_pipeline("test", [])

        assert result['success'] is True
        assert result['completed_steps'] == 0
        assert result['final_output'] is None

    def test_results_contain_step_info(self, orchestrator, multi_step_pipeline):
        """結果にステップ情報が含まれる"""
        result = orchestrator.execute_pipeline("test", multi_step_pipeline)

        for step_result in result['results']:
            assert 'step_number' in step_result
            assert 'agent_id' in step_result
            assert 'model' in step_result

    def test_context_passed(self, orchestrator, simple_pipeline):
        """コンテキスト付き実行"""
        result = orchestrator.execute_pipeline("test", simple_pipeline, context={'key': 'value'})

        assert result['success'] is True


class TestBuildPipelineSteps:

    def test_build_from_config(self, orchestrator):
        """設定からステップ構築"""
        config = [
            {'agent_id': 'claude_code', 'model': 'sonnet', 'prompt_template': 'Do {input}'},
            {'agent_id': 'codex_cli', 'model': 'gpt-4', 'prompt_template': 'Fix {input}', 'use_previous_output': True},
        ]

        steps = orchestrator._build_pipeline_steps("initial", config)

        assert len(steps) == 2
        assert all(isinstance(s, PipelineStep) for s in steps)
        assert steps[0].step_order == 1
        assert steps[1].step_order == 2
        assert steps[1].input_from_previous is True

    def test_default_model(self, orchestrator):
        """デフォルトモデル"""
        config = [{'agent_id': 'claude_code', 'prompt_template': 'test'}]
        steps = orchestrator._build_pipeline_steps("x", config)

        assert 'claude-sonnet' in steps[0].model


class TestPipelinePresets:

    def test_code_review_pipeline(self, orchestrator):
        """コードレビューパイプライン"""
        pipeline = orchestrator.create_code_review_pipeline()

        assert len(pipeline) == 3
        assert pipeline[0]['agent_id'] == 'claude_code'
        assert pipeline[1]['use_previous_output'] is True

    def test_feature_pipeline(self, orchestrator):
        """機能実装パイプライン"""
        pipeline = orchestrator.create_feature_pipeline()

        assert len(pipeline) == 4
        has_test_step = any('test' in s['prompt_template'].lower() for s in pipeline)
        assert has_test_step


class TestEstimateCost:

    def test_estimate_pipeline_cost(self, orchestrator, mock_wrapper):
        """パイプラインコスト推定"""
        config = [
            {'agent_id': 'claude_code', 'model': 'sonnet'},
            {'agent_id': 'codex_cli', 'model': 'gpt-4'},
        ]
        mock_wrapper.estimate_cost.return_value = 0.05

        cost = orchestrator.estimate_pipeline_cost(config, 1000)

        assert cost == 0.10

    def test_estimate_empty_pipeline(self, orchestrator, mock_wrapper):
        """空パイプラインのコスト"""
        cost = orchestrator.estimate_pipeline_cost([], 1000)
        assert cost == 0.0
