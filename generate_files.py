#!/usr/bin/env python3
"""
Orchestrixファイル生成スクリプト
すべてのプロジェクトファイルを一括で作成します
"""

import os

PROJECT_ROOT = "/home/yn441611/projects/orchestrix"

def create_file(filepath, content):
    """ファイルを作成するヘルパー関数"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created: {filepath}")

# Task Decomposer
task_decomposer = '''"""
タスク分解モジュール
複雑なタスクを小さなサブタスクに分解します。
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SubTask:
    """サブタスクを表すデータクラス"""
    id: str
    title: str
    description: str
    dependencies: List[str]
    complexity: float


class TaskDecomposer:
    """タスクを分解するクラス"""

    def __init__(self, complexity_analyzer=None):
        self.complexity_analyzer = complexity_analyzer
        self.task_counter = 0

    def decompose(self, task_description: str, max_subtasks: int = 10, min_complexity: float = 0.6) -> List[SubTask]:
        """タスクをサブタスクに分解"""
        if self.complexity_analyzer:
            complexity = self.complexity_analyzer.analyze(task_description)
            if complexity < min_complexity:
                return [SubTask(id=self._generate_id(), title="Original Task", description=task_description, dependencies=[], complexity=complexity)]

        task_type = self._identify_task_type(task_description)
        return self._decompose_by_type(task_description, task_type, max_subtasks)

    def _generate_id(self) -> str:
        self.task_counter += 1
        return f"subtask_{self.task_counter}"

    def _identify_task_type(self, description: str) -> str:
        lower_desc = description.lower()
        task_patterns = {
            'feature': ['add', 'implement', 'create', 'build', 'develop'],
            'bugfix': ['fix', 'bug', 'error', 'issue', 'resolve'],
            'refactor': ['refactor', 'improve', 'optimize', 'clean'],
            'documentation': ['document', 'readme', 'guide', 'tutorial'],
            'testing': ['test', 'unit test', 'integration test', 'e2e'],
            'deployment': ['deploy', 'release', 'publish'],
        }
        max_matches = 0
        detected_type = 'generic'
        for task_type, keywords in task_patterns.items():
            matches = sum(1 for keyword in keywords if keyword in lower_desc)
            if matches > max_matches:
                max_matches = matches
                detected_type = task_type
        return detected_type

    def _decompose_by_type(self, description: str, task_type: str, max_subtasks: int) -> List[SubTask]:
        decomposers = {
            'feature': self._decompose_feature,
            'bugfix': self._decompose_bugfix,
            'refactor': self._decompose_refactor,
            'documentation': self._decompose_documentation,
            'testing': self._decompose_testing,
            'deployment': self._decompose_deployment,
        }
        decomposer = decomposers.get(task_type, self._decompose_generic)
        return decomposer(description, max_subtasks)

    def _decompose_feature(self, description: str, max_subtasks: int) -> List[SubTask]:
        subtasks = []
        steps = ["Analyze requirements and design approach", "Set up basic structure and files", "Implement core functionality", "Add error handling and edge cases", "Write unit tests", "Write integration tests", "Review and optimize code", "Update documentation"]
        for i, step in enumerate(steps[:max_subtasks]):
            dependencies = [subtasks[-1].id] if i > 0 else []
            subtasks.append(SubTask(id=self._generate_id(), title=f"Step {i+1}: {step}", description=f"{description}\\n\\n{step}", dependencies=dependencies, complexity=0.5 + (i * 0.05)))
        return subtasks

    def _decompose_bugfix(self, description: str, max_subtasks: int) -> List[SubTask]:
        subtasks = []
        steps = ["Reproduce and understand bug", "Identify root cause", "Implement fix", "Add test case for bug", "Verify fix doesn't break other functionality", "Update documentation if needed"]
        for i, step in enumerate(steps[:max_subtasks]):
            dependencies = [subtasks[-1].id] if i > 0 else []
            subtasks.append(SubTask(id=self._generate_id(), title=f"Bug Fix: {step}", description=f"{description}\\n\\n{step}", dependencies=dependencies, complexity=0.4 + (i * 0.05)))
        return subtasks

    def _decompose_refactor(self, description: str, max_subtasks: int) -> List[SubTask]:
        subtasks = []
        steps = ["Analyze current code structure", "Identify refactoring opportunities", "Refactor - Phase 1 (High impact changes)", "Refactor - Phase 2 (Low impact changes)", "Run existing tests to verify", "Add new tests for refactored code"]
        for i, step in enumerate(steps[:max_subtasks]):
            dependencies = [subtasks[-1].id] if i > 0 else []
            subtasks.append(SubTask(id=self._generate_id(), title=f"Refactor: {step}", description=f"{description}\\n\\n{step}", dependencies=dependencies, complexity=0.6 + (i * 0.05)))
        return subtasks

    def _decompose_documentation(self, description: str, max_subtasks: int) -> List[SubTask]:
        subtasks = []
        steps = ["Create document structure", "Write overview and introduction", "Write detailed sections", "Add examples and code samples", "Review and edit"]
        for i, step in enumerate(steps[:max_subtasks]):
            dependencies = [subtasks[-1].id] if i > 0 else []
            subtasks.append(SubTask(id=self._generate_id(), title=f"Documentation: {step}", description=f"{description}\\n\\n{step}", dependencies=dependencies, complexity=0.3 + (i * 0.05)))
        return subtasks

    def _decompose_testing(self, description: str, max_subtasks: int) -> List[SubTask]:
        subtasks = []
        steps = ["Identify test scenarios", "Write unit tests", "Write integration tests", "Write e2e tests if applicable", "Set up test coverage reporting"]
        for i, step in enumerate(steps[:max_subtasks]):
            dependencies = [subtasks[-1].id] if i > 0 else []
            subtasks.append(SubTask(id=self._generate_id(), title=f"Testing: {step}", description=f"{description}\\n\\n{step}", dependencies=dependencies, complexity=0.4 + (i * 0.05)))
        return subtasks

    def _decompose_deployment(self, description: str, max_subtasks: int) -> List[SubTask]:
        subtasks = []
        steps = ["Prepare deployment configuration", "Set up environment variables", "Run pre-deployment tests", "Deploy to staging environment", "Verify staging deployment", "Deploy to production", "Monitor and verify"]
        for i, step in enumerate(steps[:max_subtasks]):
            dependencies = [subtasks[-1].id] if i > 0 else []
            subtasks.append(SubTask(id=self._generate_id(), title=f"Deploy: {step}", description=f"{description}\\n\\n{step}", dependencies=dependencies, complexity=0.5 + (i * 0.05)))
        return subtasks

    def _decompose_generic(self, description: str, max_subtasks: int) -> List[SubTask]:
        subtasks = []
        steps = ["Analyze task", "Plan approach", "Implement", "Test", "Review and finalize"]
        for i, step in enumerate(steps[:max_subtasks]):
            dependencies = [subtasks[-1].id] if i > 0 else []
            subtasks.append(SubTask(id=self._generate_id(), title=f"{step}", description=f"{description}\\n\\n{step}", dependencies=dependencies, complexity=0.5))
        return subtasks

    def build_dag(self, subtasks: List[SubTask]) -> Dict[str, List[str]]:
        dag = {}
        for subtask in subtasks:
            dag[subtask.id] = subtask.dependencies
        return dag
'''

# Agent Allocator
agent_allocator = '''"""
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
'''

# CLI Wrapper
cli_wrapper = '''"""
汎用CLI Wrapperモジュール
様々なAIエージェントCLIを統一的に扱うためのラッパー
"""

import subprocess
import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path
import os


class CLIWrapper:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'agents.yaml')
        self.config_path = config_path
        self.agents_config = self._load_config()

    def _load_config(self) -> Dict:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {'agents': {
                'claude_code': {'name': 'Claude Code', 'cli_command': 'claude', 'default_model': 'claude-sonnet-4-5-20250929', 'supports_features': ['code', 'file_edit', 'bash'], 'cost_per_1k_input': 3.0, 'cost_per_1k_output': 15.0, 'enabled': True}
            }}

    def get_available_agents(self) -> List[str]:
        return [agent_id for agent_id, config in self.agents_config['agents'].items() if config.get('enabled', True)]

    def get_agent_config(self, agent_id: str) -> Optional[Dict]:
        return self.agents_config['agents'].get(agent_id)
'''

# Master Orchestrator
master_orchestrator = '''"""
マスターオーケストレーターモジュール
全体的なタスク管理、エージェント調整、実行監視を行います。
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging

from .complexity_analyzer import ComplexityAnalyzer
from .task_decomposer import TaskDecomposer, SubTask


class MasterOrchestrator:
    def __init__(self, config_path: str = None):
        self.complexity_analyzer = ComplexityAnalyzer()
        self.task_decomposer = TaskDecomposer(self.complexity_analyzer)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def orchestrate_task(self, task_description: str, context: Dict = None) -> Dict:
        if context is None:
            context = {}
        self.logger.info(f"Starting task: {task_description[:50]}...")

        complexity = self.complexity_analyzer.analyze(task_description, context)
        complexity_level = self.complexity_analyzer.get_complexity_level(complexity)

        self.logger.info(f"Complexity score: {complexity:.2f} (Level: {complexity_level})")

        subtasks = self.task_decomposer.decompose(task_description)
        self.logger.info(f"Decomposed into {len(subtasks)} subtasks")

        return {
            'complexity': complexity,
            'level': complexity_level,
            'subtasks': len(subtasks),
            'status': 'completed'
        }
'''

# Agent Config YAML
agents_yaml = '''agents:
  claude_code:
    name: Claude Code
    cli_command: claude
    default_model: claude-sonnet-4-5-20250929
    supports_features:
      - code
      - file_edit
      - bash
    cost_per_1k_input: 3.0
    cost_per_1k_output: 15.0
    enabled: true

  codex_cli:
    name: Codex CLI
    cli_command: codex
    default_model: gpt-4
    supports_features:
      - code
      - file_edit
    cost_per_1k_input: 30.0
    cost_per_1k_output: 60.0
    enabled: true

  gemini_cli:
    name: Gemini CLI
    cli_command: gemini
    default_model: gemini-1.5-pro
    supports_features:
      - code
      - multimodal
    cost_per_1k_input: 1.25
    cost_per_1k_output: 5.0
    enabled: true
'''

# Main execution
print("🚀 Generating Orchestrix project files...\\n")

files_to_create = [
    (f"{PROJECT_ROOT}/src/core/task_decomposer.py", task_decomposer),
    (f"{PROJECT_ROOT}/src/core/agent_allocator.py", agent_allocator),
    (f"{PROJECT_ROOT}/src/agents/cli_wrapper.py", cli_wrapper),
    (f"{PROJECT_ROOT}/src/core/master_orchestrator.py", master_orchestrator),
    (f"{PROJECT_ROOT}/config/agents.yaml", agents_yaml),
]

for filepath, content in files_to_create:
    create_file(filepath, content)

print("\\n✅ All files generated successfully!")
print("\\nNext steps:")
print("1. pip install -r requirements.txt")
print("2. docker-compose up -d")
print("3. ./git-setup.sh  # Commit and push to remote")
