"""
エージェント割り振りモジュール
タスクの複雑度に基づいて最適なエージェントを選択・割り振ります。
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AgentAllocation:
    agent_id: str
    model: str
    reasoning: str


class AgentAllocator:
    def __init__(self, cli_wrapper):
        self.wrapper = cli_wrapper
        self.allocation_rules = {
            'simple': {'agent_id': 'claude_code', 'model': 'claude-haiku-4-5-20251001', 'complexity_range': (0.0, 0.35)},
            'medium': {'agent_id': 'claude_code', 'model': 'claude-sonnet-4-5-20250929', 'complexity_range': (0.35, 0.65)},
            'complex': {'agent_id': 'claude_code', 'model': 'claude-opus-4-6', 'complexity_range': (0.65, 1.0)}
        }

    def allocate(self, task: Dict, context: Dict = None) -> AgentAllocation:
        if context is None:
            context = {}
        complexity = task.get('complexity_score', 0.5)
        required_features = task.get('required_features', [])

        allocation = self._allocate_by_complexity(complexity)
        allocation = self._adjust_for_context(allocation, task, context)
        return allocation

    def _allocate_by_complexity(self, complexity: float) -> AgentAllocation:
        for level, rule in self.allocation_rules.items():
            min_complexity, max_complexity = rule['complexity_range']
            if min_complexity <= complexity < max_complexity:
                return AgentAllocation(agent_id=rule['agent_id'], model=rule['model'], reasoning=f'Complexity level: {level} ({complexity:.2f})')
        return AgentAllocation(agent_id=self.allocation_rules['complex']['agent_id'], model=self.allocation_rules['complex']['model'], reasoning=f'Complexity level: complex (1.00)')

    def _adjust_for_context(self, allocation: AgentAllocation, task: Dict, context: Dict) -> AgentAllocation:
        if task.get('priority', 0) >= 8:
            if allocation.model.startswith('claude-haiku'):
                allocation.model = 'claude-sonnet-4-5-20250929'
                allocation.reasoning += ' (upgraded for high priority)'
            elif allocation.model.startswith('claude-sonnet'):
                allocation.model = 'claude-opus-4-6'
                allocation.reasoning += ' (upgraded for high priority)'
        return allocation
