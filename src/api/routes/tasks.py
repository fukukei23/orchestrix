"""
タスク関連のAPIルート
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ...database.connection import SessionLocal
from ...database.models import Task, Execution
from ..dependencies import get_db


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[dict])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    priority_min: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    タスク一覧を取得

    Args:
        skip: スキップ数（ページネーション用）
        limit: 最大取得数
        status_filter: ステータスでフィルタ
        priority_min: 最小優先度でフィルタ
        db: データベースセッション

    Returns:
        タスクのリスト
    """
    query = db.query(Task)

    if status_filter:
        query = query.filter(Task.status == status_filter)

    if priority_min:
        query = query.filter(Task.priority >= priority_min)

    tasks = query.order_by(desc(Task.priority), Task.created_at)\
                .offset(skip)\
                .limit(limit)\
                .all()

    return [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "goal": task.goal,
            "complexity_score": task.complexity_score,
            "status": task.status,
            "priority": task.priority,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "scheduled_at": task.scheduled_at.isoformat() if task.scheduled_at else None,
            "cron_expression": task.cron_expression
        }
        for task in tasks
    ]


@router.get("/{task_id}", response_model=dict)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    タスク詳細を取得

    Args:
        task_id: タスクID
        db: データベースセッション

    Returns:
        タスク詳細
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    # 最新の実行を取得
    latest_execution = db.query(Execution)\
        .filter(Execution.task_id == task_id)\
        .order_by(desc(Execution.start_time))\
        .first()

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "goal": task.goal,
        "complexity_score": task.complexity_score,
        "status": task.status,
        "priority": task.priority,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        "scheduled_at": task.scheduled_at.isoformat() if task.scheduled_at else None,
        "cron_expression": task.cron_expression,
        "latest_execution": {
            "id": latest_execution.id,
            "agent_type": latest_execution.agent_type,
            "model_used": latest_execution.model_used,
            "status": latest_execution.status,
            "start_time": latest_execution.start_time.isoformat() if latest_execution.start_time else None,
            "end_time": latest_execution.end_time.isoformat() if latest_execution.end_time else None,
            "exit_code": latest_execution.exit_code,
            "cost_usd": latest_execution.cost_usd
        } if latest_execution else None
    }


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: dict,
    db: Session = Depends(get_db)
):
    """
    新規タスクを作成

    Args:
        task_data: タスクデータ
        db: データベースセッション

    Returns:
        作成されたタスク
    """
    task = Task(
        title=task_data.get('title', ''),
        description=task_data.get('description'),
        goal=task_data.get('goal', ''),
        complexity_score=task_data.get('complexity_score'),
        priority=task_data.get('priority', 0),
        status='pending',
        cron_expression=task_data.get('cron_expression')
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    logger.info(f"Created new task: {task.id}")

    return {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "message": "Task created successfully"
    }


@router.put("/{task_id}", response_model=dict)
async def update_task(
    task_id: str,
    task_data: dict,
    db: Session = Depends(get_db)
):
    """
    タスクを更新

    Args:
        task_id: タスクID
        task_data: 更新データ
        db: データベースセッション

    Returns:
        更新されたタスク
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    # 更新
    if 'title' in task_data:
        task.title = task_data['title']
    if 'description' in task_data:
        task.description = task_data['description']
    if 'goal' in task_data:
        task.goal = task_data['goal']
    if 'status' in task_data:
        task.status = task_data['status']
    if 'priority' in task_data:
        task.priority = task_data['priority']
    if 'cron_expression' in task_data:
        task.cron_expression = task_data['cron_expression']

    db.commit()
    db.refresh(task)

    logger.info(f"Updated task: {task_id}")

    return {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "message": "Task updated successfully"
    }


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    タスクを削除

    Args:
        task_id: タスクID
        db: データベースセッション
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    db.delete(task)
    db.commit()

    logger.info(f"Deleted task: {task_id}")


@router.post("/{task_id}/execute", response_model=dict)
async def execute_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    タスクを実行

    Args:
        task_id: タスクID
        db: データベースセッション

    Returns:
        実行結果
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    # TODO: オーケストレーターを呼び出す
    # from ...core.master_orchestrator import MasterOrchestrator
    # orchestrator = MasterOrchestrator()
    # result = orchestrator.orchestrate_task(task.goal)

    # 今はダミー実行を作成
    execution = Execution(
        task_id=task_id,
        agent_type='claude_code',
        model_used='claude-sonnet-4-5-20250929',
        status='running',
        start_time=datetime.now()
    )

    db.add(execution)
    db.commit()

    logger.info(f"Started execution for task: {task_id}")

    return {
        "execution_id": execution.id,
        "task_id": task_id,
        "status": "started",
        "message": "Task execution started"
    }


@router.get("/{task_id}/executions", response_model=List[dict])
async def get_task_executions(
    task_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    タスクの実行履歴を取得

    Args:
        task_id: タスクID
        limit: 最大取得数
        db: データベースセッション

    Returns:
        実行履歴のリスト
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    executions = db.query(Execution)\
        .filter(Execution.task_id == task_id)\
        .order_by(desc(Execution.start_time))\
        .limit(limit)\
        .all()

    return [
        {
            "id": exec.id,
            "task_id": exec.task_id,
            "agent_type": exec.agent_type,
            "model_used": exec.model_used,
            "status": exec.status,
            "start_time": exec.start_time.isoformat() if exec.start_time else None,
            "end_time": exec.end_time.isoformat() if exec.end_time else None,
            "exit_code": exec.exit_code,
            "cost_usd": exec.cost_usd
        }
        for exec in executions
    ]
