"""
ログ分析モジュール
実行履歴を分析して成功率・コスト・パターンを抽出します。
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import logging


class LogAnalyzer:
    """ログアナライザー"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_executions(self,
                        executions: List[Dict],
                        time_range: Dict = None) -> Dict:
        """
        実行履歴を分析

        Args:
            executions: 実行データのリスト
            time_range: 時間範囲 {'start': datetime, 'end': datetime}

        Returns:
            分析結果
        """
        if not executions:
            return {'error': 'No executions to analyze'}

        # DataFrameに変換
        df = pd.DataFrame(executions)

        # created_at列をdatetimeに変換
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])

        # 時間範囲でフィルタ
        if time_range:
            start = pd.to_datetime(time_range['start'])
            end = pd.to_datetime(time_range['end'])
            df = df[(df['created_at'] >= start) & (df['created_at'] <= end)]

        analysis = {
            'total_executions': len(df),
            'time_range': time_range,
            'summary': self._calculate_summary(df),
            'success_rate': self._calculate_success_rate(df),
            'cost_analysis': self._calculate_cost_analysis(df),
            'agent_performance': self._calculate_agent_performance(df),
            'model_performance': self._calculate_model_performance(df),
            'temporal_analysis': self._calculate_temporal_analysis(df),
            'error_patterns': self._analyze_error_patterns(df)
        }

        return analysis

    def _calculate_summary(self, df: pd.DataFrame) -> Dict:
        """サマリー統計を計算"""
        if 'start_time' not in df.columns or 'end_time' not in df.columns:
            return {}

        # 実行時間を計算
        df['execution_time'] = (
            pd.to_datetime(df['end_time']) - pd.to_datetime(df['start_time'])
        ).dt.total_seconds()

        return {
            'total_executions': len(df),
            'successful': len(df[df['status'] == 'success']),
            'failed': len(df[df['status'] == 'failed']),
            'avg_execution_time': df['execution_time'].mean(),
            'median_execution_time': df['execution_time'].median(),
            'max_execution_time': df['execution_time'].max(),
            'min_execution_time': df['execution_time'].min(),
            'std_execution_time': df['execution_time'].std()
        }

    def _calculate_success_rate(self, df: pd.DataFrame) -> Dict:
        """成功率を計算"""
        if 'status' not in df.columns:
            return {}

        total = len(df)
        successful = len(df[df['status'] == 'success'])

        return {
            'total': total,
            'successful': successful,
            'failed': total - successful,
            'success_rate': successful / total if total > 0 else 0,
            'trend': self._calculate_trend(df)
        }

    def _calculate_trend(self, df: pd.DataFrame) -> str:
        """成功率の傾向を計算"""
        if 'created_at' not in df.columns or 'status' not in df.columns:
            return 'unknown'

        # 日付でソート
        df_sorted = df.sort_values('created_at')

        # 最近7日間と7日前で比較
        df_sorted['date'] = pd.to_datetime(df_sorted['created_at']).dt.date
        now = df_sorted['date'].max()

        recent_df = df_sorted[df_sorted['date'] >= now - timedelta(days=7)]
        older_df = df_sorted[df_sorted['date'] < now - timedelta(days=7)]

        recent_success_rate = (recent_df[recent_df['status'] == 'success'].shape[0] /
                           recent_df.shape[0]) if len(recent_df) > 0 else 0
        older_success_rate = (older_df[older_df['status'] == 'success'].shape[0] /
                          older_df.shape[0]) if len(older_df) > 0 else 0

        if recent_success_rate > older_success_rate + 0.05:
            return 'improving'
        elif recent_success_rate < older_success_rate - 0.05:
            return 'declining'
        else:
            return 'stable'

    def _calculate_cost_analysis(self, df: pd.DataFrame) -> Dict:
        """コスト分析を計算"""
        if 'cost_usd' not in df.columns:
            return {}

        return {
            'total_cost': df['cost_usd'].sum(),
            'avg_cost': df['cost_usd'].mean(),
            'median_cost': df['cost_usd'].median(),
            'max_cost': df['cost_usd'].max(),
            'min_cost': df['cost_usd'].min(),
            'cost_distribution': self._get_cost_distribution(df),
            'cost_per_success': df[df['status'] == 'success']['cost_usd'].sum() /
                               df[df['status'] == 'success'].shape[0]
                               if len(df[df['status'] == 'success']) > 0 else 0
        }

    def _get_cost_distribution(self, df: pd.DataFrame) -> Dict:
        """コストの分布を取得"""
        if 'cost_usd' not in df.columns:
            return {}

        return {
            'under_0.01': len(df[df['cost_usd'] < 0.01]),
            '0.01_to_0.1': len(df[(df['cost_usd'] >= 0.01) & (df['cost_usd'] < 0.1)]),
            '0.1_to_1.0': len(df[(df['cost_usd'] >= 0.1) & (df['cost_usd'] < 1.0)]),
            '1.0_to_10.0': len(df[(df['cost_usd'] >= 1.0) & (df['cost_usd'] < 10.0)]),
            'over_10.0': len(df[df['cost_usd'] >= 10.0])
        }

    def _calculate_agent_performance(self, df: pd.DataFrame) -> Dict:
        """エージェントごとのパフォーマンスを計算"""
        if 'agent_type' not in df.columns or 'status' not in df.columns:
            return {}

        agent_stats = {}
        for agent_id, group in df.groupby('agent_type'):
            total = len(group)
            successful = len(group[group['status'] == 'success'])

            agent_stats[agent_id] = {
                'total_executions': total,
                'successful_executions': successful,
                'failed_executions': total - successful,
                'success_rate': successful / total if total > 0 else 0,
                'total_cost': group['cost_usd'].sum() if 'cost_usd' in group.columns else 0,
                'avg_cost': group['cost_usd'].mean() if 'cost_usd' in group.columns else 0
            }

        return agent_stats

    def _calculate_model_performance(self, df: pd.DataFrame) -> Dict:
        """モデルごとのパフォーマンスを計算"""
        if 'model_used' not in df.columns or 'status' not in df.columns:
            return {}

        model_stats = {}
        for model_name, group in df.groupby('model_used'):
            total = len(group)
            successful = len(group[group['status'] == 'success'])

            # トークン統計
            total_input_tokens = group['input_tokens'].sum() if 'input_tokens' in group.columns else 0
            total_output_tokens = group['output_tokens'].sum() if 'output_tokens' in group.columns else 0

            model_stats[model_name] = {
                'total_executions': total,
                'successful_executions': successful,
                'failed_executions': total - successful,
                'success_rate': successful / total if total > 0 else 0,
                'total_cost': group['cost_usd'].sum() if 'cost_usd' in group.columns else 0,
                'avg_cost': group['cost_usd'].mean() if 'cost_usd' in group.columns else 0,
                'total_input_tokens': total_input_tokens,
                'total_output_tokens': total_output_tokens,
                'avg_input_tokens': group['input_tokens'].mean() if 'input_tokens' in group.columns else 0,
                'avg_output_tokens': group['output_tokens'].mean() if 'output_tokens' in group.columns else 0
            }

        return model_stats

    def _calculate_temporal_analysis(self, df: pd.DataFrame) -> Dict:
        """時間帯ごとの分析を計算"""
        if 'created_at' not in df.columns:
            return {}

        df['hour'] = pd.to_datetime(df['created_at']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['created_at']).dt.dayofweek

        # 時間帯ごとの実行数
        hourly_counts = df.groupby('hour').size().to_dict()

        # 曜日ごとの実行数
        daily_counts = df.groupby('day_of_week').size().to_dict()

        return {
            'peak_hour': int(df['hour'].mode()[0]) if len(df) > 0 else None,
            'hourly_distribution': hourly_counts,
            'daily_distribution': daily_counts,
            'busiest_day': max(daily_counts, key=daily_counts.get) if daily_counts else None
        }

    def _analyze_error_patterns(self, df: pd.DataFrame) -> Dict:
        """エラーパターンを分析"""
        failed_df = df[df['status'] == 'failed']

        if len(failed_df) == 0:
            return {'total_errors': 0}

        error_types = {}

        # 退出コードで分類
        if 'exit_code' in failed_df.columns:
            for code, group in failed_df.groupby('exit_code'):
                error_types[f'exit_code_{code}'] = len(group)

        # エージェントごとの失敗
        if 'agent_type' in failed_df.columns:
            for agent_id, group in failed_df.groupby('agent_type'):
                error_types[f'agent_{agent_id}'] = len(group)

        return {
            'total_errors': len(failed_df),
            'error_by_type': error_types,
            'error_rate': len(failed_df) / len(df) if len(df) > 0 else 0,
            'recommendations': self._generate_error_recommendations(error_types)
        }

    def _generate_error_recommendations(self, error_types: Dict) -> List[str]:
        """エラーから改善提案を生成"""
        recommendations = []

        total_errors = sum(error_types.values())

        if total_errors == 0:
            return recommendations

        # 頻繁なエラータイプを特定
        sorted_errors = sorted(error_types.items(), key=lambda x: x[1], reverse=True)
        top_error = sorted_errors[0]

        if top_error[1] > total_errors * 0.3:
            error_type = top_error[0]
            recommendations.append(
                f"⚠️ '{error_type}' がエラー全体の{top_error[1]/total_errors*100:.0f}%を占めています。"
            )

            # 特定的な提案
            if 'exit_code' in error_type:
                recommendations.append(
                    "退出コードに関連する問題を調査してください。"
                    "環境設定、依存関係、リソース不足を確認してください。"
                )
            elif 'agent' in error_type:
                recommendations.append(
                    f"エージェント {error_type.replace('agent_', '')} の設定を確認してください。"
                    "APIキーやネットワーク接続に問題がないか検証してください。"
                )

        return recommendations

    def cluster_tasks(self, tasks: List[Dict], n_clusters: int = 3) -> Dict:
        """
        タスクをクラスタリングで分類

        Args:
            tasks: タスクデータのリスト
            n_clusters: クラスタ数（デフォルト: 3）

        Returns:
            クラスタリング結果
        """
        df = pd.DataFrame(tasks)

        # 特徴量の選択
        features = []
        if 'complexity_score' in df.columns:
            features.append('complexity_score')
        if 'priority' in df.columns:
            features.append('priority')
        if 'input_tokens' in df.columns:
            features.append('input_tokens')
        if 'cost_usd' in df.columns:
            features.append('cost_usd')

        if not features:
            return {'error': 'No features available for clustering'}

        # 特徴量のスケーリング
        df_features = df[features].fillna(0)
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(df_features)

        # K-meansクラスタリング
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(features_scaled)

        df['cluster'] = clusters

        # クラスターごとの特徴を分析
        cluster_analysis = {}
        for cluster_id, group in df.groupby('cluster'):
            cluster_analysis[cluster_id] = {
                'count': len(group),
                'avg_complexity': group['complexity_score'].mean() if 'complexity_score' in group.columns else 0,
                'avg_priority': group['priority'].mean() if 'priority' in group.columns else 0,
                'avg_cost': group['cost_usd'].mean() if 'cost_usd' in group.columns else 0,
                'task_ids': group.index.tolist()
            }

        return {
            'n_clusters': n_clusters,
            'cluster_analysis': cluster_analysis,
            'tasks_with_clusters': df.to_dict('records')
        }

    def recommend_optimal_allocation(self, analysis: Dict) -> Dict:
        """
        分析結果に基づいて最適なエージェント割り振りを推薦

        Args:
            analysis: 分析結果

        Returns:
            推奨事項
        """
        recommendations = []

        # 成功率の分析
        if 'agent_performance' in analysis:
            best_agent = max(
                analysis['agent_performance'].items(),
                key=lambda x: x[1]['success_rate']
            )

            if best_agent[1]['success_rate'] > 0.9:
                recommendations.append({
                    'type': 'high_success_rate',
                    'priority': 'high',
                    'message': f"エージェント {best_agent[0]} の成功率が高いです（{best_agent[1]['success_rate']:.1%}）。"
                               "このエージェントを優先的に使用することを推奨します。"
                })

        # コスト効率の分析
        if 'model_performance' in analysis:
            cost_efficient_models = [
                (model, stats)
                for model, stats in analysis['model_performance'].items()
                if stats['success_rate'] > 0.8
            ]

            if cost_efficient_models:
                best_model = min(cost_efficient_models, key=lambda x: x[1]['avg_cost'])
                recommendations.append({
                    'type': 'cost_efficient',
                    'priority': 'medium',
                    'message': f"モデル {best_model[0]} が最もコスト効率が良いです（平均コスト: ${best_model[1]['avg_cost']:.4f}）。"
                               "コストを削減するためにこのモデルを検討してください。"
                })

        # エラーパターンに基づく推薨
        if 'error_patterns' in analysis:
            if 'recommendations' in analysis['error_patterns']:
                recommendations.extend([
                    {
                        'type': 'error_mitigation',
                        'priority': 'high',
                        'message': rec
                    }
                    for rec in analysis['error_patterns']['recommendations']
                ])

        return {
            'total_recommendations': len(recommendations),
            'recommendations': recommendations
        }
