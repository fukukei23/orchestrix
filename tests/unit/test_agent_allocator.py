"""AgentAllocator の単体テスト"""
import pytest
from unittest.mock import MagicMock

from src.core.agent_allocator import AgentAllocator, AgentAllocation


@pytest.fixture
def mock_wrapper():
    return MagicMock()


@pytest.fixture
def allocator(mock_wrapper):
    return AgentAllocator(mock_wrapper)


class TestAgentAllocator:

    def test_allocate_simple_task(self, allocator):
        """低複雑度タスクはhaikuに割り当て"""
        task = {'complexity_score': 0.1}
        result = allocator.allocate(task)

        assert isinstance(result, AgentAllocation)
        assert result.agent_id == 'claude_code'
        assert 'haiku' in result.model

    def test_allocate_medium_task(self, allocator):
        """中複雑度タスクはsonnetに割り当て"""
        task = {'complexity_score': 0.5}
        result = allocator.allocate(task)

        assert result.agent_id == 'claude_code'
        assert 'sonnet' in result.model

    def test_allocate_complex_task(self, allocator):
        """高複雑度タスクはopusに割り当て"""
        task = {'complexity_score': 0.8}
        result = allocator.allocate(task)

        assert result.agent_id == 'claude_code'
        assert 'opus' in result.model

    def test_allocate_boundary_simple_medium(self, allocator):
        """simple/medium境界値"""
        task_low = {'complexity_score': 0.34}
        task_high = {'complexity_score': 0.35}

        result_low = allocator.allocate(task_low)
        result_high = allocator.allocate(task_high)

        assert 'haiku' in result_low.model
        assert 'sonnet' in result_high.model

    def test_allocate_boundary_medium_complex(self, allocator):
        """medium/complex境界値"""
        task_low = {'complexity_score': 0.64}
        task_high = {'complexity_score': 0.65}

        result_low = allocator.allocate(task_low)
        result_high = allocator.allocate(task_high)

        assert 'sonnet' in result_low.model
        assert 'opus' in result_high.model

    def test_allocate_no_complexity_defaults_to_medium(self, allocator):
        """複雑度未指定時はデフォルト0.5（medium）"""
        task = {}
        result = allocator.allocate(task)

        assert 'sonnet' in result.model

    def test_allocate_high_priority_upgrade(self, allocator):
        """高優先度（priority>=8）はモデルをアップグレード"""
        task = {'complexity_score': 0.1, 'priority': 8}
        result = allocator.allocate(task)

        assert 'sonnet' in result.model or 'opus' in result.model
        assert 'upgraded' in result.reasoning

    def test_allocate_high_priority_sonnet_to_opus(self, allocator):
        """高優先度でsonnet→opusにアップグレード"""
        task = {'complexity_score': 0.5, 'priority': 9}
        result = allocator.allocate(task)

        assert 'opus' in result.model
        assert 'upgraded' in result.reasoning

    def test_allocate_normal_priority_no_upgrade(self, allocator):
        """通常優先度はアップグレードなし"""
        task = {'complexity_score': 0.1, 'priority': 5}
        result = allocator.allocate(task)

        assert 'haiku' in result.model
        assert 'upgraded' not in result.reasoning

    def test_allocate_with_context(self, allocator):
        """コンテキスト付きで正常動作"""
        task = {'complexity_score': 0.3}
        context = {'user': 'test'}
        result = allocator.allocate(task, context)

        assert isinstance(result, AgentAllocation)

    def test_reasoning_contains_complexity(self, allocator):
        """reasoningに複雑度が含まれる"""
        task = {'complexity_score': 0.5}
        result = allocator.allocate(task)

        assert '0.50' in result.reasoning
