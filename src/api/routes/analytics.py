"""
分析関連のAPIルート
"""

from collections import defaultdict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import logging

from ..dependencies import get_db
from ...database.models import Execution


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/executions/summary", response_model=dict)
async def get_execution_summary(
    days: int = 7,
    db: Session = Depends(get_db)
):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    executions = db.query(Execution)\
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

    total = len(executions)
    successful = len([e for e in executions if e.status == 'success'])
    total_cost = sum(e.cost_usd for e in executions if e.cost_usd)

    return {
        "total_executions": total,
        "successful": successful,
        "failed": total - successful,
        "success_rate": round(successful / total, 4) if total > 0 else 0.0,
        "total_cost_usd": round(total_cost, 4) if total_cost else 0.0,
        "avg_cost_usd": round(total_cost / total, 4) if total > 0 else 0.0,
        "period": f"{start_date.isoformat()} to {end_date.isoformat()}"
    }


@router.get("/agent-performance", response_model=List[dict])
async def get_agent_performance(
    days: int = 30,
    db: Session = Depends(get_db)
):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    executions = db.query(Execution)\
        .filter(Execution.start_time >= start_date)\
        .filter(Execution.start_time <= end_date)\
        .all()

    if not executions:
        return []

    agent_stats = defaultdict(lambda: {
        'total': 0, 'successful': 0, 'failed': 0, 'total_cost': 0.0
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


@router.get("/model-performance", response_model=List[dict])
async def get_model_performance(
    days: int = 30,
    db: Session = Depends(get_db)
):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    executions = db.query(Execution)\
        .filter(Execution.start_time >= start_date)\
        .filter(Execution.start_time <= end_date)\
        .all()

    if not executions:
        return []

    model_stats = defaultdict(lambda: {
        'total': 0, 'successful': 0,
        'total_input_tokens': 0, 'total_output_tokens': 0,
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

    results = []
    for model_id, stats in model_stats.items():
        total = stats['total']
        results.append({
            "model_id": model_id,
            "total_executions": total,
            "successful_executions": stats['successful'],
            "success_rate": round(stats['successful'] / total, 4) if total > 0 else 0.0,
            "total_input_tokens": stats['total_input_tokens'],
            "total_output_tokens": stats['total_output_tokens'],
            "avg_input_tokens": round(stats['total_input_tokens'] / total, 2) if total > 0 else 0,
            "avg_output_tokens": round(stats['total_output_tokens'] / total, 2) if total > 0 else 0,
            "total_cost_usd": round(stats['total_cost'], 4),
            "avg_cost_usd": round(stats['total_cost'] / total, 4) if total > 0 else 0.0
        })

    return results


@router.get("/error-analysis", response_model=dict)
async def get_error_analysis(
    days: int = 30,
    db: Session = Depends(get_db)
):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    executions = db.query(Execution)\
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

    errors_by_agent = defaultdict(int)
    errors_by_exit_code = defaultdict(int)

    for exec in executions:
        errors_by_agent[exec.agent_type or 'unknown'] += 1
        errors_by_exit_code[str(exec.exit_code or 'unknown')] += 1

    recommendations = []

    if errors_by_agent:
        worst_agent = max(errors_by_agent.items(), key=lambda x: x[1])
        if worst_agent[1] > len(executions) * 0.3:
            recommendations.append(
                f"エージェント {worst_agent[0]} がエラーの{worst_agent[1]}%を占めています。"
                "このエージェントの設定を確認してください。"
            )

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


@router.get("/trends", response_model=dict)
async def get_trends(
    days: int = 90,
    db: Session = Depends(get_db)
):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    executions = db.query(Execution)\
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

    weekly_stats = defaultdict(lambda: {'total': 0, 'successful': 0})

    for exec in executions:
        week_key = exec.start_time.strftime('%Y-W%U') if exec.start_time else 'unknown'
        weekly_stats[week_key]['total'] += 1
        if exec.status == 'success':
            weekly_stats[week_key]['successful'] += 1

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
