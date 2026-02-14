"""
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
            subtasks.append(SubTask(id=self._generate_id(), title=f"Step {i+1}: {step}", description=f"{description}\n\n{step}", dependencies=dependencies, complexity=0.5 + (i * 0.05)))
        return subtasks

    def _decompose_bugfix(self, description: str, max_subtasks: int) -> List[SubTask]:
        subtasks = []
        steps = ["Reproduce and understand bug", "Identify root cause", "Implement fix", "Add test case for bug", "Verify fix doesn't break other functionality", "Update documentation if needed"]
        for i, step in enumerate(steps[:max_subtasks]):
            dependencies = [subtasks[-1].id] if i > 0 else []
            subtasks.append(SubTask(id=self._generate_id(), title=f"Bug Fix: {step}", description=f"{description}\n\n{step}", dependencies=dependencies, complexity=0.4 + (i * 0.05)))
        return subtasks

    def _decompose_refactor(self, description: str, max_subtasks: int) -> List[SubTask]:
        subtasks = []
        steps = ["Analyze current code structure", "Identify refactoring opportunities", "Refactor - Phase 1 (High impact changes)", "Refactor - Phase 2 (Low impact changes)", "Run existing tests to verify", "Add new tests for refactored code"]
        for i, step in enumerate(steps[:max_subtasks]):
            dependencies = [subtasks[-1].id] if i > 0 else []
            subtasks.append(SubTask(id=self._generate_id(), title=f"Refactor: {step}", description=f"{description}\n\n{step}", dependencies=dependencies, complexity=0.6 + (i * 0.05)))
        return subtasks

    def _decompose_documentation(self, description: str, max_subtasks: int) -> List[SubTask]:
        subtasks = []
        steps = ["Create document structure", "Write overview and introduction", "Write detailed sections", "Add examples and code samples", "Review and edit"]
        for i, step in enumerate(steps[:max_subtasks]):
            dependencies = [subtasks[-1].id] if i > 0 else []
            subtasks.append(SubTask(id=self._generate_id(), title=f"Documentation: {step}", description=f"{description}\n\n{step}", dependencies=dependencies, complexity=0.3 + (i * 0.05)))
        return subtasks

    def _decompose_testing(self, description: str, max_subtasks: int) -> List[SubTask]:
        subtasks = []
        steps = ["Identify test scenarios", "Write unit tests", "Write integration tests", "Write e2e tests if applicable", "Set up test coverage reporting"]
        for i, step in enumerate(steps[:max_subtasks]):
            dependencies = [subtasks[-1].id] if i > 0 else []
            subtasks.append(SubTask(id=self._generate_id(), title=f"Testing: {step}", description=f"{description}\n\n{step}", dependencies=dependencies, complexity=0.4 + (i * 0.05)))
        return subtasks

    def _decompose_deployment(self, description: str, max_subtasks: int) -> List[SubTask]:
        subtasks = []
        steps = ["Prepare deployment configuration", "Set up environment variables", "Run pre-deployment tests", "Deploy to staging environment", "Verify staging deployment", "Deploy to production", "Monitor and verify"]
        for i, step in enumerate(steps[:max_subtasks]):
            dependencies = [subtasks[-1].id] if i > 0 else []
            subtasks.append(SubTask(id=self._generate_id(), title=f"Deploy: {step}", description=f"{description}\n\n{step}", dependencies=dependencies, complexity=0.5 + (i * 0.05)))
        return subtasks

    def _decompose_generic(self, description: str, max_subtasks: int) -> List[SubTask]:
        subtasks = []
        steps = ["Analyze task", "Plan approach", "Implement", "Test", "Review and finalize"]
        for i, step in enumerate(steps[:max_subtasks]):
            dependencies = [subtasks[-1].id] if i > 0 else []
            subtasks.append(SubTask(id=self._generate_id(), title=f"{step}", description=f"{description}\n\n{step}", dependencies=dependencies, complexity=0.5))
        return subtasks

    def build_dag(self, subtasks: List[SubTask]) -> Dict[str, List[str]]:
        dag = {}
        for subtask in subtasks:
            dag[subtask.id] = subtask.dependencies
        return dag
