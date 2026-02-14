"""
Parallel 協調学習パターン
複数のエージェントが並列で実行され、最良の結果を選択します
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import logging


@dataclass
class ParallelTask:
    """並列タスク"""
    task_id: str
    agent_id: str
    model: str
    prompt: str
    timeout: int = 300


@dataclass
class ParallelResult:
    """並列実行結果"""
    task_id: str
    agent_id: str
    model: str
    success: bool
    output: str
    execution_time: float
    cost_usd: float


class ParallelOrchestrator:
    """並列実行オーケストレーター"""

    def __init__(self, cli_wrapper):
        """
        初期化

        Args:
            cli_wrapper: CLIWrapperインスタンス
        """
        self.wrapper = cli_wrapper
        self.logger = logging.getLogger(__name__)

    def execute_parallel(self,
                      prompt: str,
                      agent_configs: List[Dict],
                      context: Dict = None,
                      max_workers: int = 3) -> Dict:
        """
        複数のエージェントで並列実行

        Args:
            prompt: 実行するプロンプト
            agent_configs: エージェント設定のリスト
                [
                    {
                        'agent_id': 'claude_code',
                        'model': 'claude-sonnet-4-5-20250929'
                    },
                    {
                        'agent_id': 'codex_cli',
                        'model': 'gpt-4'
                    },
                    ...
                ]
            context: 実行コンテキスト
            max_workers: 最大並列数（デフォルト: 3）

        Returns:
            並列実行の結果
        """
        if context is None:
            context = {}

        agent_configs = agent_configs[:max_workers]  # 最大並列数に制限
        self.logger.info(f"Executing parallel tasks with {len(agent_configs)} agents")

        # 並列タスクを作成
        tasks = [
            ParallelTask(
                task_id=f"parallel_{i}",
                agent_id=config['agent_id'],
                model=config.get('model', 'claude-sonnet-4-5-20250929'),
                prompt=prompt,
                timeout=config.get('timeout', 300)
            )
            for i, config in enumerate(agent_configs)
        ]

        # 並列実行（実際には順次実装、将来的にthreading/multiprocessing）
        results = []
        import time
        start_time = time.time()

        for task in tasks:
            result = self._execute_single_task(task)
            results.append(result)

        total_time = time.time() - start_time

        # 結果を分析
        best_result = self._select_best_result(results)

        return {
            'success': any(r.success for r in results),
            'total_tasks': len(tasks),
            'successful_tasks': sum(1 for r in results if r.success),
            'failed_tasks': len(results) - sum(1 for r in results if r.success),
            'total_execution_time': total_time,
            'total_cost': sum(r.cost_usd for r in results),
            'results': results,
            'best_result': best_result
        }

    def _execute_single_task(self, task: ParallelTask) -> ParallelResult:
        """単一のタスクを実行"""
        import time
        start_time = time.time()

        execution_result = self.wrapper.execute_command(
            agent_id=task.agent_id,
            prompt=task.prompt,
            model=task.model,
            timeout=task.timeout
        )

        execution_time = time.time() - start_time

        # コストを見積もる
        cost = self.wrapper.estimate_cost(
            agent_id=task.agent_id,
            model=task.model,
            input_tokens=1000,  # 推定値
            output_tokens=1000   # 推定値
        )

        return ParallelResult(
            task_id=task.task_id,
            agent_id=task.agent_id,
            model=task.model,
            success=execution_result['success'],
            output=execution_result.get('output', ''),
            execution_time=execution_time,
            cost_usd=cost
        )

    def _select_best_result(self, results: List[ParallelResult]) -> Optional[ParallelResult]:
        """
        最良の結果を選択

        選択基準（優先順位）：
        1. 成功していること
        2. 実行時間が短い
        3. コストが低い
        """
        successful_results = [r for r in results if r.success]

        if not successful_results:
            # 全て失敗したら、最初の結果を返す
            return results[0] if results else None

        # 実行時間でソート
        sorted_by_time = sorted(successful_results, key=lambda x: x.execution_time)
        top_3_by_time = sorted_by_time[:3]

        # コストでソート
        sorted_by_cost = sorted(top_3_by_time, key=lambda x: x.cost_usd)

        # 最良の結果を返す
        return sorted_by_cost[0]

    def create_diverse_agent_config(self) -> List[Dict]:
        """異なるエージェントの設定を作成"""
        return [
            {
                'agent_id': 'claude_code',
                'model': 'claude-sonnet-4-5-20250929',
                'timeout': 300
            },
            {
                'agent_id': 'codex_cli',
                'model': 'gpt-4',
                'timeout': 300
            },
            {
                'agent_id': 'gemini_cli',
                'model': 'gemini-1.5-pro',
                'timeout': 300
            }
        ]

    def create_same_agent_different_model_config(self) -> List[Dict]:
        """同じエージェントの異なるモデルの設定を作成"""
        return [
            {
                'agent_id': 'claude_code',
                'model': 'claude-haiku-4-5-20251001',
                'timeout': 180  # 低速モデルは短めに
            },
            {
                'agent_id': 'claude_code',
                'model': 'claude-sonnet-4-5-20250929',
                'timeout': 300
            },
            {
                'agent_id': 'claude_code',
                'model': 'claude-opus-4-6',
                'timeout': 450  # 高速モデルは長めに
            }
        ]

    def compare_results(self, results: List[ParallelResult]) -> Dict:
        """
        複数の結果を比較

        Args:
            results: 並列実行結果のリスト

        Returns:
            比較結果
        """
        if not results:
            return {'error': 'No results to compare'}

        comparison = {
            'total_results': len(results),
            'successful': sum(1 for r in results if r.success),
            'failed': len(results) - sum(1 for r in results if r.success),
            'metrics': []
        }

        for result in results:
            metrics = {
                'task_id': result.task_id,
                'agent_id': result.agent_id,
                'model': result.model,
                'success': result.success,
                'execution_time': result.execution_time,
                'cost_usd': result.cost_usd,
                'output_length': len(result.output) if result.output else 0
            }
            comparison['metrics'].append(metrics)

        # 出力の類似度を計算（簡易実装）
        successful_outputs = [r.output for r in results if r.success and r.output]
        if len(successful_outputs) >= 2:
            from difflib import SequenceMatcher
            similarities = []
            for i, output1 in enumerate(successful_outputs):
                for j, output2 in enumerate(successful_outputs):
                    if i < j:
                        matcher = SequenceMatcher(None, output1, output2)
                        similarity = matcher.ratio()
                        similarities.append({
                            'result_1': i,
                            'result_2': j,
                            'similarity': similarity
                        })
            comparison['output_similarities'] = similarities

        return comparison
