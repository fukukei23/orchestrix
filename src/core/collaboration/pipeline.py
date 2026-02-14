"""
Pipeline 協調学習パターン
複数のエージェントが順次連携してタスクを改善します（A→B→C）
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import logging


@dataclass
class PipelineStep:
    """Pipelineの各ステップ"""
    step_order: int
    agent_id: str
    model: str
    prompt: str
    input_from_previous: bool  # 前のステップの出力を入力に使うか
    timeout: int = 300  # タイムアウト（秒）


class PipelineOrchestrator:
    """Pipeline オーケストレーター"""

    def __init__(self, cli_wrapper):
        """
        初期化

        Args:
            cli_wrapper: CLIWrapperインスタンス
        """
        self.wrapper = cli_wrapper
        self.logger = logging.getLogger(__name__)

    def execute_pipeline(self,
                      initial_prompt: str,
                      pipeline_config: List[Dict],
                      context: Dict = None) -> Dict:
        """
        Pipeline を実行（A→B→C...順次）

        Args:
            initial_prompt: 最初のステップのプロンプト
            pipeline_config: Pipeline設定
                [
                    {
                        'agent_id': 'claude_code',
                        'model': 'claude-sonnet-4-5-20250929',
                        'prompt_template': 'Review and improve: {input}',
                        'use_previous_output': True
                    },
                    ...
                ]
            context: 実行コンテキスト

        Returns:
            全体の実行結果
        """
        if context is None:
            context = {}

        self.logger.info(f"Starting pipeline with {len(pipeline_config)} steps")

        steps = self._build_pipeline_steps(initial_prompt, pipeline_config)
        results = []
        current_input = initial_prompt

        # 各ステップを順次実行
        for i, step in enumerate(steps):
            self.logger.info(f"Executing pipeline step {i+1}/{len(steps)}: {step.agent_id}")

            # プロンプトを構築
            if step.input_from_previous and i > 0:
                # 前のステップの出力を入力に使用
                previous_result = results[i-1]
                if previous_result['success']:
                    current_input = step.prompt.format(input=current_input)
                    # 前の出力を添付
                    current_input += f"\n\nPrevious output:\n{previous_result['output']}"
                else:
                    # 前のステップが失敗したら中断
                    self.logger.error(f"Step {i} failed, aborting pipeline")
                    return {
                        'success': False,
                        'error': f'Step {i} failed: {previous_result.get("error")}',
                        'results': results,
                        'completed_steps': i
                    }
            else:
                # 独立したプロンプト
                current_input = step.prompt.format(input=current_input) if '{input}' in step.prompt else step.prompt

            # ステップを実行
            result = self.wrapper.execute_command(
                agent_id=step.agent_id,
                prompt=current_input,
                model=step.model,
                timeout=step.timeout
            )

            result['step_number'] = i + 1
            result['agent_id'] = step.agent_id
            result['model'] = step.model
            results.append(result)

            # 次のステップのために入力を更新
            current_input = result.get('output', '')

            self.logger.info(f"Step {i+1} completed: {'success' if result['success'] else 'failed'}")

        # 全体結果を集計
        success_count = sum(1 for r in results if r['success'])
        return {
            'success': all(r['success'] for r in results),
            'completed_steps': len(results),
            'successful_steps': success_count,
            'failed_steps': len(results) - success_count,
            'results': results,
            'final_output': results[-1].get('output') if results and results[-1].get('success') else None
        }

    def _build_pipeline_steps(self,
                            initial_prompt: str,
                            pipeline_config: List[Dict]) -> List[PipelineStep]:
        """Pipelineステップを構築"""
        steps = []

        for i, config in enumerate(pipeline_config):
            steps.append(PipelineStep(
                step_order=i + 1,
                agent_id=config['agent_id'],
                model=config.get('model', 'claude-sonnet-4-5-20250929'),
                prompt=config['prompt_template'],
                input_from_previous=config.get('use_previous_output', False),
                timeout=config.get('timeout', 300)
            ))

        return steps

    def create_code_review_pipeline(self) -> List[Dict]:
        """コードレビュー用Pipeline設定を作成"""
        return [
            {
                'agent_id': 'claude_code',
                'model': 'claude-haiku-4-5-20251001',
                'prompt_template': 'Analyze the following code for potential bugs and improvements:\n\n{input}',
                'use_previous_output': False
            },
            {
                'agent_id': 'codex_cli',
                'model': 'gpt-4',
                'prompt_template': 'Based on the analysis, implement the improvements:\n\n{input}',
                'use_previous_output': True
            },
            {
                'agent_id': 'claude_code',
                'model': 'claude-sonnet-4-5-20250929',
                'prompt_template': 'Final review: Ensure code quality, add documentation, and check for edge cases:\n\n{input}',
                'use_previous_output': True
            }
        ]

    def create_feature_pipeline(self) -> List[Dict]:
        """機能実装用Pipeline設定を作成"""
        return [
            {
                'agent_id': 'claude_code',
                'model': 'claude-haiku-4-5-20251001',
                'prompt_template': 'Design the architecture for the following feature:\n\n{input}',
                'use_previous_output': False
            },
            {
                'agent_id': 'claude_code',
                'model': 'claude-sonnet-4-5-20250929',
                'prompt_template': 'Implement the core functionality based on the design:\n\n{input}',
                'use_previous_output': True
            },
            {
                'agent_id': 'codex_cli',
                'model': 'gpt-4',
                'prompt_template': 'Write comprehensive unit tests for the implementation:\n\n{input}',
                'use_previous_output': True
            },
            {
                'agent_id': 'claude_code',
                'model': 'claude-sonnet-4-5-20250929',
                'prompt_template': 'Review the code and tests, add documentation, and create integration tests:\n\n{input}',
                'use_previous_output': True
            }
        ]

    def estimate_pipeline_cost(self,
                          pipeline_config: List[Dict],
                          estimated_tokens_per_step: int) -> float:
        """
        Pipeline全体の推定コストを計算

        Args:
            pipeline_config: Pipeline設定
            estimated_tokens_per_step: 各ステップの推定トークン数

        Returns:
            推定コスト（USD）
        """
        total_cost = 0.0

        for config in pipeline_config:
            agent_id = config['agent_id']
            model = config.get('model', 'claude-sonnet-4-5-20250929')

            cost = self.wrapper.estimate_cost(
                agent_id=agent_id,
                model=model,
                input_tokens=estimated_tokens_per_step,
                output_tokens=estimated_tokens_per_step
            )
            total_cost += cost

        return total_cost
