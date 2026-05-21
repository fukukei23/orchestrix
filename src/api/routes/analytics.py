"""
分析関連のAPIルート
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ..dependencies import get_db


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/executions/summary", response_model=dict)
async def get_execution_summary(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    実行サマリーを取得

    Args:
        days: 過去何日分か（デフォルト: 7日）
        db: データベースセッション

    Returns:
        実行サマリー
    """
    from ...database.models import Execution

    # 時間範囲を計算
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # 指定期間の実行を取得
    from ...database.connection import SessionLocal as get_session
    session = get_session()

    try:
        executions = session.query(Execution)\
            .filter(Execution.start_time >= start_date)\
            .filter(Execution.start_time <= end_date)\
            .all()

        if not executions:
            return {
                "total_executions": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0,
                "total_cost_usd": 0.0,
                "avg_cost_usd": 0.0,
                "period": f"{start_date.isoformat()} to {end_date.isoformat()}"
            }

        # 統計を計算
        total = len(executions)
        successful = len([e for e in executions if e.status == 'success'])
        failed = total - successful
        total_cost = sum(e.cost_usd for e in executions if e.cost_usd)

        return {
            "total_executions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round(successful / total, 4) if total > 0 else 0.0,
            "total_cost_usd": round(total_cost, 4) if total_cost else 0.0,
            "avg_cost_usd": round(total_cost / total, 4) if total > 0 else 0.0,
            "period": f"{start_date.isoformat()} to {end_date.isoformat()}"
        }
    finally:
        session.close()


@router.get("/agent-performance", response_model=List[dict])
async def get_agent_performance(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    エージェントパフォーマンスを取得

    Args:
        days: 過去何日分か（デフォルト: 30日）
        db: データベースセッション

    Returns:
        エージェントパフォーマンスのリスト
    """
    from ...database.models import Execution

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    from ...database.connection import SessionLocal as get_session
    session = get_session()

    try:
        executions = session.query(Execution)\
            .filter(Execution.start_time >= start_date)\
            .filter(Execution.start_time <= end_date)\
            .all()

        if not executions:
            return []

        # エージェントごとにグループ化
        from collections import defaultdict
        agent_stats = defaultdict(lambda: {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'total_cost': 0.0
        })

        for exec in executions:
            agent_id = exec.agent_type or 'unknown'
            agent_stats[agent_id]['total'] += 1
            if exec.status == 'success':
                agent_stats[agent_id]['successful'] += 1
            else:
                agent_stats[agent_id]['failed'] += 1
            if exec.cost_usd:
                agent_stats[agent_id]['total_cost'] += exec.cost_usd

        # 結果をフォーマット
        results = []
        for agent_id, stats in agent_stats.items():
            results.append({
                "agent_id": agent_id,
                "total_executions": stats['total'],
                "successful_executions": stats['successful'],
                "failed_executions": stats['failed'],
                "success_rate": round(stats['successful'] / stats['total'], 4) if stats['total'] > 0 else 0.0,
                "total_cost_usd": round(stats['total_cost'], 4),
                "avg_cost_usd": round(stats['total_cost'] / stats['total'], 4) if stats['total'] > 0 else 0.0
            })

        return results
    finally:
        session.close()


@router.get("/model-performance", response_model=List[dict])
async def get_model_performance(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    モデルパフォーマンスを取得

    Args:
        days: 過去何日分か（デフォルト: 30日）
        db: データベースセッション

    Returns:
        モデルパフォーマンスのリスト
    """
    from ...database.models import Execution

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    from ...database.connection import SessionLocal as get_session
    session = get_session()

    try:
        executions = session.query(Execution)\
            .filter(Execution.start_time >= start_date)\
            .filter(Execution.start_time <= end_date)\
            .all()

        if not executions:
            return []

        # モデルごとにグループ化
        from collections import defaultdict
        model_stats = defaultdict(lambda: {
            'total': 0,
            'successful': 0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_cost': 0.0
        })

        for exec in executions:
            model_id = exec.model_used or 'unknown'
            model_stats[model_id]['total'] += 1
            if exec.status == 'success':
                model_stats[model_id]['successful'] += 1
            if exec.input_tokens:
                model_stats[model_id]['total_input_tokens'] += exec.input_tokens
            if exec.output_tokens:
                model_stats[model_id]['total_output_tokens'] += exec.output_tokens
            if exec.cost_usd:
                model_stats[model_id]['total_cost'] += exec.cost_usd

        # 結果をフォーマット
        results = []
        for model_id, stats in model_stats.items():
            avg_input = stats['total_input_tokens'] / stats['total'] if stats['total'] > 0 else 0
            avg_output = stats['total_output_tokens'] / stats['total'] if stats['total'] > 0 else 0
            success_rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0

            results.append({
                "model_id": model_id,
                "total_executions": stats['total'],
                "successful_executions": stats['successful'],
                "success_rate": round(success_rate, 4),
                "total_input_tokens": stats['total_input_tokens'],
                "total_output_tokens": stats['total_output_tokens'],
                "avg_input_tokens": round(avg_input, 2),
                "avg_output_tokens": round(avg_output, 2),
                "total_cost_usd": round(stats['total_cost'], 4),
                "avg_cost_usd": round(stats['total_cost'] / stats['total'], 4) if stats['total'] > 0 else 0.0
            })

        return results
    finally:
        session.close()


@router.get("/error-analysis", response_model=dict)
async def get_error_analysis(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    エラー分析を取得

    Args:
        days: 過去何日分か（デフォルト: 30日）
        db: データベースセッション

    Returns:
        エラー分析結果
    """
    from ...database.models import Execution

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    from ...database.connection import SessionLocal as get_session
    session = get_session()

    try:
        executions = session.query(Execution)\
            .filter(Execution.start_time >= start_date)\
            .filter(Execution.start_time <= end_date)\
            .filter(Execution.status == 'failed')\
            .all()

        if not executions:
            return {
                "total_errors": 0,
                "error_by_agent": {},
                "error_by_exit_code": {},
                "recommendations": ["No errors in the specified period"]
            }

        # エージェントごとに集計
        from collections import defaultdict
        errors_by_agent = defaultdict(int)
        errors_by_exit_code = defaultdict(int)

        for exec in executions:
            agent_id = exec.agent_type or 'unknown'
            exit_code = exec.exit_code or 'unknown'
            errors_by_agent[agent_id] += 1
            errors_by_exit_code[str(exit_code)] += 1

        # 改善提案
        recommendations = []

        # 頻繁なエージェントエラー
        if errors_by_agent:
            worst_agent = max(errors_by_agent.items(), key=lambda x: x[1])
            if worst_agent[1] > len(executions) * 0.3:
                recommendations.append(
                    f"エージェント {worst_agent[0]} がエラーの{worst_agent[1]}%を占めています。"
                    "このエージェントの設定を確認してください。"
                )

        # 頻繁な終了コード
        if errors_by_exit_code:
            worst_exit_code = max(errors_by_exit_code.items(), key=lambda x: x[1])
            if worst_exit_code[1] > len(executions) * 0.2:
                recommendations.append(
                    f"終了コード {worst_exit_code[0]} が頻繁に発生しています。"
                    "このエラーの原因を調査してください。"
                )

        return {
            "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
            "total_errors": len(executions),
            "error_by_agent": dict(errors_by_agent),
            "error_by_exit_code": dict(errors_by_exit_code),
            "recommendations": recommendations
        }
    finally:
        session.close()


@router.get("/trends", response_model=dict)
async def get_trends(
    days: int = 90,
    db: Session = Depends(get_db)
):
    """
    トレンド分析を取得

    Args:
        days: 過去何日分か（デフォルト: 90日）
        db: データベースセッション

    Returns:
        トレンド分析結果
    """
    from ...database.models import Execution

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    from ...database.connection import SessionLocal as get_session
    session = get_session()

    try:
        executions = session.query(Execution)\
            .filter(Execution.start_time >= start_date)\
            .filter(Execution.start_time <= end_date)\
            .order_by(Execution.start_time)\
            .all()

        if not executions:
            return {
                "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
                "total_executions": 0,
                "trends": {}
            }

        # 週ごとにグループ化
        from collections import defaultdict
        weekly_stats = defaultdict(lambda: {'total': 0, 'successful': 0})

        for exec in executions:
            week_key = exec.start_time.strftime('%Y-W%U') if exec.start_time else 'unknown'
            weekly_stats[week_key]['total'] += 1
            if exec.status == 'success':
                weekly_stats[week_key]['success'] = successful

        # 週ごとの成功率を計算
        trends = {}
        for week_key, stats in weekly_stats.items():
            success_rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
            trends[week_key] = {
                'total': stats['total'],
                'successful': stats['successful'],
                'success_rate': round(success_rate, 4)
            }

        return {
            "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
            "total_executions": len(executions),
            "trends": trends
        }
    finally:
        session.close()
