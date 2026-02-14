"""
Fallback 協調学習パターン
エージェントが失敗した際に、自動的に代替エージェントに切り替えます
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import logging


@dataclass
class FallbackConfig:
    """Fallback設定"""
    primary_agent_id: str
    primary_model: str
    fallback_agents: List[Dict]  # [{'agent_id': '...', 'model': '...'}]
    max_retries: int = 3
    retry_delay: int = 5  # 秒


@dataclass
class FallbackExecution:
    """Fallback実行情報"""
    attempt: int
    agent_id: str
    model: str
    success: bool
    output: str
    error: Optional[str]
    execution_time: float
    cost_usd: float


class FallbackOrchestrator:
    """Fallback オーケストレーター"""

    def __init__(self, cli_wrapper):
        """
        初期化

        Args:
            cli_wrapper: CLIWrapperインスタンス
        """
        self.wrapper = cli_wrapper
        self.logger = logging.getLogger(__name__)

    def execute_with_fallback(self,
                             prompt: str,
                             fallback_config: FallbackConfig,
                             context: Dict = None) -> Dict:
        """
        Fallback付きで実行（失敗したら自動切替）

        Args:
            prompt: 実行するプロンプト
            fallback_config: Fallback設定
            context: 実行コンテキスト

        Returns:
            実行結果
        """
        if context is None:
            context = {}

        self.logger.info(
            f"Starting execution with fallback "
            f"(primary: {fallback_config.primary_agent_id})"
        )

        executions = []
        agents_to_try = [fallback_config.primary_agent_id] + \
                       [agent['agent_id'] for agent in fallback_config.fallback_agents]

        # 最大リトライ回数分実行
        for attempt in range(min(fallback_config.max_retries, len(agents_to_try))):
            agent_id = agents_to_try[attempt]
            model = (fallback_config.primary_model if attempt == 0
                     else fallback_config.fallback_agents[attempt - 1]['model'])

            self.logger.info(f"Attempt {attempt + 1}: Using agent {agent_id}")

            # 実行
            execution = self._execute_attempt(prompt, agent_id, model, attempt + 1)
            executions.append(execution)

            # 成功したら終了
            if execution.success:
                self.logger.info(f"✓ Success on attempt {attempt + 1}")
                return {
                    'success': True,
                    'completed_attempts': attempt + 1,
                    'final_agent_id': agent_id,
                    'final_model': model,
                    'output': execution.output,
                    'executions': executions,
                    'total_cost': sum(e.cost_usd for e in executions)
                }

            # 失敗したら遅延
            if attempt < min(fallback_config.max_retries, len(agents_to_try)) - 1:
                import time
                self.logger.warning(
                    f"Attempt {attempt + 1} failed: {execution.error}. "
                    f"Waiting {fallback_config.retry_delay}s before retry..."
                )
                time.sleep(fallback_config.retry_delay)

        # 全て失敗
        self.logger.error(f"All {len(executions)} attempts failed")
        return {
            'success': False,
            'completed_attempts': len(executions),
            'executions': executions,
            'error': 'All attempts failed',
            'total_cost': sum(e.cost_usd for e in executions)
        }

    def _execute_attempt(self,
                        prompt: str,
                        agent_id: str,
                        model: str,
                        attempt_number: int) -> FallbackExecution:
        """単一の試行を実行"""
        import time
        start_time = time.time()

        result = self.wrapper.execute_command(
            agent_id=agent_id,
            prompt=prompt,
            model=model,
            timeout=300
        )

        execution_time = time.time() - start_time

        # コストを見積もる
        cost = self.wrapper.estimate_cost(
            agent_id=agent_id,
            model=model,
            input_tokens=1000,
            output_tokens=1000
        )

        return FallbackExecution(
            attempt=attempt_number,
            agent_id=agent_id,
            model=model,
            success=result['success'],
            output=result.get('output', ''),
            error=result.get('error') if not result['success'] else None,
            execution_time=execution_time,
            cost_usd=cost
        )

    def create_claude_to_openai_fallback(self) -> FallbackConfig:
        """Claude → OpenAIのFallback設定を作成"""
        return FallbackConfig(
            primary_agent_id='claude_code',
            primary_model='claude-sonnet-4-5-20250929',
            fallback_agents=[
                {
                    'agent_id': 'codex_cli',
                    'model': 'gpt-4'
                },
                {
                    'agent_id': 'codex_cli',
                    'model': 'gpt-3.5-turbo'
                }
            ],
            max_retries=3,
            retry_delay=5
        )

    def create_speed_to_quality_fallback(self) -> FallbackConfig:
        """高速モデル→品質モデルのFallback設定を作成"""
        return FallbackConfig(
            primary_agent_id='claude_code',
            primary_model='claude-haiku-4-5-20251001',
            fallback_agents=[
                {
                    'agent_id': 'claude_code',
                    'model': 'claude-sonnet-4-5-20250929'
                },
                {
                    'agent_id': 'claude_code',
                    'model': 'claude-opus-4-6'
                }
            ],
            max_retries=3,
            retry_delay=3
        )

    def analyze_failures(self, executions: List[FallbackExecution]) -> Dict:
        """
        失敗パターンを分析

        Args:
            executions: 実行履歴

        Returns:
            分析結果
        """
        if not executions:
            return {'error': 'No executions to analyze'}

        failure_analysis = {
            'total_executions': len(executions),
            'successful': sum(1 for e in executions if e.success),
            'failed': sum(1 for e in executions if not e.success),
            'agent_performance': {},
            'error_patterns': []
        }

        # エージェントごとの成功率を計算
        agent_stats = {}
        for execution in executions:
            agent_id = execution.agent_id
            if agent_id not in agent_stats:
                agent_stats[agent_id] = {'total': 0, 'success': 0}
            agent_stats[agent_id]['total'] += 1
            if execution.success:
                agent_stats[agent_id]['success'] += 1

        for agent_id, stats in agent_stats.items():
            success_rate = stats['success'] / stats['total'] if stats['total'] > 0 else 0
            failure_analysis['agent_performance'][agent_id] = {
                'total_attempts': stats['total'],
                'successful_attempts': stats['success'],
                'success_rate': success_rate
            }

        # エラーパターンを分類
        failed_executions = [e for e in executions if not e.success and e.error]
        for execution in failed_executions:
            error = execution.error or 'Unknown error'

            # エラータイプを分類
            error_type = self._classify_error(error)
            failure_analysis['error_patterns'].append({
                'attempt': execution.attempt,
                'agent_id': execution.agent_id,
                'model': execution.model,
                'error_type': error_type,
                'error_message': error
            })

        # 改善提案
        failure_analysis['recommendations'] = self._generate_recommendations(
            failure_analysis['error_patterns'],
            failure_analysis['agent_performance']
        )

        return failure_analysis

    def _classify_error(self, error: str) -> str:
        """エラーを分類"""
        error_lower = error.lower()

        error_types = {
            'timeout': ['timeout', 'timed out', 'deadline'],
            'api_error': ['api', 'rate limit', 'quota'],
            'authentication': ['auth', 'unauthorized', 'api key'],
            'network': ['network', 'connection', 'dns'],
            'parsing': ['parse', 'format', 'invalid'],
            'resource': ['memory', 'disk', 'out of'],
        }

        for error_type, keywords in error_types.items():
            if any(keyword in error_lower for keyword in keywords):
                return error_type

        return 'unknown'

    def _generate_recommendations(self,
                               error_patterns: List[Dict],
                               agent_performance: Dict) -> List[str]:
        """改善提案を生成"""
        recommendations = []

        # タイムアウトが多い場合
        timeout_errors = [e for e in error_patterns if e['error_type'] == 'timeout']
        if len(timeout_errors) >= 2:
            recommendations.append(
                "⚠️ タイムアウトが頻発しています。"
                "プロンプトを短縮するか、タイムアウト値を増やすことを検討してください。"
            )

        # APIエラーが多い場合
        api_errors = [e for e in error_patterns if e['error_type'] == 'api_error']
        if len(api_errors) >= 2:
            recommendations.append(
                "⚠️ APIエラーが頻発しています。"
                "APIキーを確認するか、レート制限を待ってください。"
            )

        # 特定のエージェントの成功率が低い場合
        for agent_id, performance in agent_performance.items():
            if performance['success_rate'] < 0.3 and performance['total_attempts'] >= 2:
                recommendations.append(
                    f"⚠️ {agent_id} の成功率が低いです（{performance['success_rate']:.0%}）。"
                    "別のエージェントを試すことを推奨します。"
                )

        if not recommendations:
            recommendations.append(
                "✓ 実行履歴から特定の問題パターンは検出されませんでした。"
            )

        return recommendations
