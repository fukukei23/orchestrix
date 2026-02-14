"""
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
