"""FallbackOrchestrator の単体テスト"""
import pytest
from unittest.mock import MagicMock, patch

from src.core.collaboration.fallback import (
    FallbackOrchestrator, FallbackConfig, FallbackExecution
)


@pytest.fixture
def mock_wrapper():
    wrapper = MagicMock()
    wrapper.execute_command.return_value = {'success': True, 'output': 'test output'}
    wrapper.estimate_cost.return_value = 0.01
    return wrapper


@pytest.fixture
def orchestrator(mock_wrapper):
    return FallbackOrchestrator(mock_wrapper)


@pytest.fixture
def config():
    return FallbackConfig(
        primary_agent_id='claude_code',
        primary_model='claude-sonnet-4-5-20250929',
        fallback_agents=[
            {'agent_id': 'codex_cli', 'model': 'gpt-4'},
            {'agent_id': 'gemini_cli', 'model': 'gemini-1.5-pro'},
        ],
        max_retries=3,
        retry_delay=0  # テストでは遅延なし
    )


class TestExecuteWithFallback:

    @patch('time.sleep')
    def test_success_on_first_attempt(self, mock_sleep, orchestrator, config):
        """最初の試行で成功"""
        result = orchestrator.execute_with_fallback("test prompt", config)

        assert result['success'] is True
        assert result['completed_attempts'] == 1
        assert result['final_agent_id'] == 'claude_code'
        assert result['output'] == 'test output'

    @patch('time.sleep')
    def test_success_on_fallback(self, mock_sleep, orchestrator, config, mock_wrapper):
        """プライマリ失敗→フォールバック成功"""
        mock_wrapper.execute_command.side_effect = [
            {'success': False, 'error': 'API error'},
            {'success': True, 'output': 'fallback output'},
        ]

        result = orchestrator.execute_with_fallback("test prompt", config)

        assert result['success'] is True
        assert result['completed_attempts'] == 2
        assert result['final_agent_id'] == 'codex_cli'
        assert result['output'] == 'fallback output'

    @patch('time.sleep')
    def test_all_attempts_fail(self, mock_sleep, orchestrator, config, mock_wrapper):
        """全試行失敗"""
        mock_wrapper.execute_command.return_value = {'success': False, 'error': 'timeout'}

        result = orchestrator.execute_with_fallback("test prompt", config)

        assert result['success'] is False
        assert result['completed_attempts'] == 3
        assert 'All attempts failed' in result['error']

    @patch('time.sleep')
    def test_total_cost_accumulated(self, mock_sleep, orchestrator, config, mock_wrapper):
        """コストが蓄積される"""
        mock_wrapper.estimate_cost.return_value = 0.05

        result = orchestrator.execute_with_fallback("test prompt", config)

        assert result['total_cost'] == 0.05

    @patch('time.sleep')
    def test_executions_recorded(self, mock_sleep, orchestrator, config):
        """実行履歴が記録される"""
        result = orchestrator.execute_with_fallback("test prompt", config)

        assert len(result['executions']) == 1
        assert isinstance(result['executions'][0], FallbackExecution)


class TestFallbackConfigs:

    def test_claude_to_openai_config(self, orchestrator):
        """Claude→OpenAIフォールバック設定"""
        config = orchestrator.create_claude_to_openai_fallback()

        assert config.primary_agent_id == 'claude_code'
        assert len(config.fallback_agents) == 2
        assert config.max_retries == 3

    def test_speed_to_quality_config(self, orchestrator):
        """高速→品質フォールバック設定"""
        config = orchestrator.create_speed_to_quality_fallback()

        assert config.primary_model == 'claude-haiku-4-5-20251001'
        assert len(config.fallback_agents) == 2


class TestAnalyzeFailures:

    def test_analyze_empty_executions(self, orchestrator):
        """空の実行履歴"""
        result = orchestrator.analyze_failures([])

        assert 'error' in result

    def test_analyze_mixed_results(self, orchestrator):
        """成功・失敗混在の分析"""
        executions = [
            FallbackExecution(1, 'claude_code', 'sonnet', True, 'ok', None, 1.0, 0.01),
            FallbackExecution(2, 'codex_cli', 'gpt-4', False, '', 'timeout', 2.0, 0.02),
            FallbackExecution(3, 'gemini_cli', 'gemini', False, '', 'api error', 3.0, 0.03),
        ]

        result = orchestrator.analyze_failures(executions)

        assert result['total_executions'] == 3
        assert result['successful'] == 1
        assert result['failed'] == 2
        assert 'agent_performance' in result

    def test_analyze_agent_performance(self, orchestrator):
        """エージェントごとの成功率"""
        executions = [
            FallbackExecution(1, 'claude_code', 'sonnet', True, 'ok', None, 1.0, 0.01),
            FallbackExecution(2, 'claude_code', 'sonnet', False, '', 'error', 1.0, 0.01),
        ]

        result = orchestrator.analyze_failures(executions)

        assert result['agent_performance']['claude_code']['success_rate'] == 0.5


class TestClassifyError:

    def test_classify_timeout(self, orchestrator):
        assert orchestrator._classify_error("Request timeout after 30s") == 'timeout'

    def test_classify_api_error(self, orchestrator):
        assert orchestrator._classify_error("Rate limit exceeded") == 'api_error'

    def test_classify_auth_error(self, orchestrator):
        assert orchestrator._classify_error("Auth failed: unauthorized access") == 'authentication'

    def test_classify_network_error(self, orchestrator):
        assert orchestrator._classify_error("Connection refused") == 'network'

    def test_classify_unknown(self, orchestrator):
        assert orchestrator._classify_error("Something unexpected") == 'unknown'


class TestGenerateRecommendations:

    def test_no_issues(self, orchestrator):
        """問題なし"""
        recommendations = orchestrator._generate_recommendations([], {})
        assert any('検出されませんでした' in r for r in recommendations)

    def test_timeout_recommendation(self, orchestrator):
        """タイムアウト推奨"""
        patterns = [
            {'error_type': 'timeout', 'agent_id': 'a', 'model': 'm', 'attempt': 1, 'error_message': 't/o'},
            {'error_type': 'timeout', 'agent_id': 'a', 'model': 'm', 'attempt': 2, 'error_message': 't/o'},
        ]
        recommendations = orchestrator._generate_recommendations(patterns, {})
        assert any('タイムアウト' in r for r in recommendations)

    def test_low_success_rate_recommendation(self, orchestrator):
        """低成功率推奨"""
        perf = {'agent_x': {'success_rate': 0.2, 'total_attempts': 3}}
        recommendations = orchestrator._generate_recommendations([], perf)
        assert any('agent_x' in r for r in recommendations)
