"""Celeryタスク定義"""
from celery import Celery
from datetime import timedelta
import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

# Celeryアプリケーション
celery_app = Celery(
    'orchestrix',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

@celery_app.task
def execute_async_task(task_id: str, goal: str, agent_type: str = 'claude_code') -> Dict[str, Any]:
    """
    非同期でタスクを実行する

    Args:
        task_id: タスクID
        goal: タスクの目標
        agent_type: エージェントタイプ

    Returns:
        実行結果
    """
    from ..core.master_orchestrator import MasterOrchestrator
    from ..database.connection import SessionLocal
    from ..database.models import Task, Execution
    from datetime import datetime

    orchestrator = MasterOrchestrator()
    db = SessionLocal()

    try:
        # タスクを取得
        task = db.query(Task).filter(Task.id == task_id).first()

        if not task:
            return {
                'success': False,
                'error': f"Task {task_id} not found"
            }

        # タスクステータスをrunningに変更
        task.status = 'running'
        db.commit()

        # 実行レコード作成
        execution = Execution(
            task_id=task_id,
            agent_type=agent_type,
            model_used=f"{agent_type}_default",
            status='running',
            start_time=datetime.now()
        )

        db.add(execution)
        db.commit()

        # オーケストレーターを実行
        result = orchestrator.orchestrate_task(goal, agent_type=agent_type)

        # 実行結果を更新
        execution.end_time = datetime.now()
        execution.status = 'completed' if result.get('status') == 'completed' else 'failed'
        task.status = 'completed' if result.get('status') == 'completed' else 'failed'

        # LLMの結果を保存
        if result.get('llm_result') and result['llm_result'].get('success'):
            llm_data = result['llm_result']
            execution.input_tokens = llm_data.get('input_tokens', 0)
            execution.output_tokens = llm_data.get('output_tokens', 0)

            # コストを計算（AgentConfigから取得）
            # TODO: AgentConfigテーブルからコストを取得
            execution.cost_usd = 0.0

        db.commit()

        return {
            'success': True,
            'task_id': task_id,
            'execution_id': execution.id,
            'result': result
        }

    except Exception as e:
        db.rollback()

        # エラーを記録
        if 'task_id' in locals():
            execution.status = 'failed'
            db.commit()

        return {
            'success': False,
            'error': str(e)
        }
    finally:
        db.close()


@celery_app.task
def periodic_health_check() -> Dict[str, Any]:
    """
    定期的なヘルスチェック

    Returns:
        ヘルスチェック結果
    """
    from ..database.connection import engine
    from sqlalchemy import text

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            is_healthy = result.scalar() is not None

        return {
            'success': True,
            'healthy': is_healthy,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        return {
            'success': False,
            'healthy': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@celery_app.task
def cleanup_old_executions(days: int = 30) -> Dict[str, Any]:
    """
    古い実行履歴を削除する

    Args:
        days: 削除対象の日数（デフォルト: 30日）

    Returns:
        削除結果
    """
    from ..database.connection import engine
    from sqlalchemy import text
    from datetime import datetime, timedelta

    try:
        cutoff_date = datetime.now() - timedelta(days=days)

        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    DELETE FROM executions
                    WHERE start_time < :cutoff_date
                    AND status = 'completed'
                """),
                {'cutoff_date': cutoff_date}
            )

            deleted_count = result.rowcount

        return {
            'success': True,
            'deleted_count': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Celery Beat設定（定期実行）
celery_app.conf.beat_schedule = {
    'periodic-health-check': {
        'task': 'src.scheduler.celery_tasks.periodic_health_check',
        'schedule': 300.0,  # 5分ごと
    },
    'periodic-cleanup': {
        'task': 'src.scheduler.celery_tasks.cleanup_old_executions',
        'schedule': 86400.0,  # 1日ごと
    },
}
