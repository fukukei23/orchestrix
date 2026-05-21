"""Execution routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ...api.dependencies import get_db
from ...database.models import Execution, Task
from pydantic import BaseModel


class ExecutionResponse(BaseModel):
    """実行履歴レスポンスモデル"""
    id: str
    task_id: str
    agent_type: str
    model_used: str
    start_time: str
    end_time: str | None = None
    status: str
    exit_code: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None
    git_branch: str | None = None
    git_worktree_path: str | None = None


router = APIRouter()


@router.get("/executions", response_model=List[ExecutionResponse])
async def get_executions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """実行履歴を取得する"""
    executions = db.query(Execution).order_by(Execution.start_time.desc()).offset(skip).limit(limit).all()

    return [
        ExecutionResponse(
            id=ex.id,
            task_id=ex.task_id,
            agent_type=ex.agent_type,
            model_used=ex.model_used,
            start_time=ex.start_time.isoformat() if ex.start_time else None,
            end_time=ex.end_time.isoformat() if ex.end_time else None,
            status=ex.status,
            exit_code=ex.exit_code,
            input_tokens=ex.input_tokens,
            output_tokens=ex.output_tokens,
            cost_usd=ex.cost_usd,
            git_branch=ex.git_branch,
            git_worktree_path=ex.git_worktree_path
        )
        for ex in executions
    ]


@router.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    db: Session = Depends(get_db)
):
    """特定の実行履歴を取得する"""
    execution = db.query(Execution).filter(Execution.id == execution_id).first()

    if not execution:
        return None

    return ExecutionResponse(
        id=execution.id,
        task_id=execution.task_id,
        agent_type=execution.agent_type,
        model_used=execution.model_used,
        start_time=execution.start_time.isoformat() if execution.start_time else None,
        end_time=execution.end_time.isoformat() if execution.end_time else None,
        status=execution.status,
        exit_code=execution.exit_code,
        input_tokens=execution.input_tokens,
        output_tokens=execution.output_tokens,
        cost_usd=execution.cost_usd,
        git_branch=execution.git_branch,
        git_worktree_path=execution.git_worktree_path
    )
