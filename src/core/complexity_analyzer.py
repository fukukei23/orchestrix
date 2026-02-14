"""
タスク複雑度判定モジュール
タスクの複雑さを0.0-1.0のスコアで判定します。
"""

from typing import Dict, List
import re


class ComplexityAnalyzer:
    """タスクの複雑度を分析するクラス"""

    def __init__(self):
        # 各要因の重み
        self.weights = {
            'length': 0.15,          # 説明の長さ
            'technical_terms': 0.25,    # 技術用語の数
            'dependencies': 0.20,        # 依存関係の数
            'complexity_keywords': 0.30, # 複雑度を示すキーワード
            'files_scope': 0.10         # 対象ファイルの数
        }

    def analyze(self, task_description: str, context: Dict = None) -> float:
        """
        タスクの複雑度を分析して0.0-1.0のスコアを返す

        Args:
            task_description: タスクの説明文
            context: 追加コンテキスト（依存関係、対象ファイル等）

        Returns:
            複雑度スコア（0.0-1.0）
        """
        if context is None:
            context = {}

        scores = {}

        # 各要因を分析
        scores['length'] = self._analyze_length(task_description)
        scores['technical_terms'] = self._analyze_technical_terms(task_description)
        scores['dependencies'] = self._analyze_dependencies(context.get('dependencies', []))
        scores['complexity_keywords'] = self._analyze_complexity_keywords(task_description)
        scores['files_scope'] = self._analyze_files_scope(context.get('files', []))

        # 重み付きスコアを計算
        total_score = sum(
            scores[factor] * self.weights[factor]
            for factor in self.weights.keys()
        )

        # 0.0-1.0の範囲にクランプ
        return max(0.0, min(1.0, total_score))

    def _analyze_length(self, description: str) -> float:
        """説明の長さに基づく複雑度（0.0-1.0）"""
        length = len(description)
        # 100文字以下: 0.0, 1000文字以上: 1.0
        if length <= 100:
            return 0.0
        elif length >= 1000:
            return 1.0
        else:
            return (length - 100) / 900

    def _analyze_technical_terms(self, description: str) -> float:
        """技術用語の数に基づく複雑度（0.0-1.0）"""
        technical_terms = [
            'python', 'javascript', 'typescript', 'react', 'django', 'fastapi',
            'kubernetes', 'docker', 'redis', 'postgresql', 'celery',
            'async', 'concurrent', 'distributed', 'microservices', 'api',
            'authentication', 'authorization', 'encryption', 'caching',
            'database', 'orm', 'migration', 'deployment', 'ci/cd',
            'algorithm', 'optimization', 'refactoring', 'design pattern',
            'testing', 'integration', 'e2e', 'unit test',
        ]

        lower_desc = description.lower()
        count = sum(1 for term in technical_terms if term in lower_desc)
        return min(1.0, count / 5)

    def _analyze_dependencies(self, dependencies: List[str]) -> float:
        """依存関係の数に基づく複雑度（0.0-1.0）"""
        if not dependencies:
            return 0.0
        return min(1.0, len(dependencies) / 5)

    def _analyze_complexity_keywords(self, description: str) -> float:
        """複雑度を示すキーワードに基づく複雑度（0.0-1.0）"""
        high_complexity_keywords = [
            'architecture', 'system', 'framework', 'implementation',
            'integration', 'migration', 'refactoring', 'optimization',
            'security', 'scalability', 'performance', 'concurrency',
            'database', 'schema', 'deployment', 'orchestration',
        ]

        lower_desc = description.lower()
        count = sum(1 for keyword in high_complexity_keywords if keyword in lower_desc)
        return min(1.0, count / 3)

    def _analyze_files_scope(self, files: List[str]) -> float:
        """対象ファイルの数に基づく複雑度（0.0-1.0）"""
        if not files:
            return 0.0
        return min(1.0, len(files) / 10)

    def get_complexity_level(self, score: float) -> str:
        """
        複雑度スコアからレベルを取得

        Args:
            score: 複雑度スコア（0.0-1.0）

        Returns:
            複雑度レベル（'simple', 'medium', 'complex'）
        """
        if score < 0.35:
            return 'simple'
        elif score < 0.65:
            return 'medium'
        else:
            return 'complex'
